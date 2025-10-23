"""
Kafka Consumer для обработки событий
"""
import json
import logging
import signal
import sys
from typing import Dict, Any, Callable, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from .kafka_config import kafka_config
from .kafka_events import BaseEvent, EventType

logger = logging.getLogger(__name__)

class KafkaEventConsumer:
    """Consumer для обработки событий из Kafka"""
    
    def __init__(self, group_id: str, topics: list):
        self.group_id = group_id
        self.topics = topics
        self.consumer = None
        self.event_handlers: Dict[EventType, Callable] = {}
        self.running = False
        
        # Обработка сигналов для graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _initialize_consumer(self):
        """Инициализация Kafka consumer"""
        try:
            consumer_config = {
                'bootstrap_servers': kafka_config.bootstrap_servers.split(','),
                'group_id': self.group_id,
                'auto_offset_reset': kafka_config.consumer_auto_offset_reset,
                'enable_auto_commit': kafka_config.consumer_enable_auto_commit,
                'auto_commit_interval_ms': kafka_config.consumer_auto_commit_interval_ms,
                'max_poll_records': kafka_config.consumer_max_poll_records,
                'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
                'key_deserializer': lambda m: m.decode('utf-8') if m else None,
                'session_timeout_ms': 30000,
                'heartbeat_interval_ms': 10000,
                'max_poll_interval_ms': 300000,
            }
            
            # Добавляем настройки безопасности если нужно
            if kafka_config.security_protocol != "PLAINTEXT":
                consumer_config.update({
                    'security_protocol': kafka_config.security_protocol,
                    'sasl_mechanism': kafka_config.sasl_mechanism,
                    'sasl_plain_username': kafka_config.sasl_username,
                    'sasl_plain_password': kafka_config.sasl_password,
                })
            
            self.consumer = KafkaConsumer(**consumer_config)
            self.consumer.subscribe(self.topics)
            
            logger.info(f"✅ Kafka Consumer инициализирован для топиков: {self.topics}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Kafka Consumer: {e}")
            raise
    
    def register_handler(self, event_type: EventType, handler: Callable):
        """
        Регистрация обработчика для типа события
        
        Args:
            event_type: Тип события
            handler: Функция-обработчик
        """
        self.event_handlers[event_type] = handler
        logger.info(f"📝 Зарегистрирован обработчик для события: {event_type}")
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        logger.info(f"🛑 Получен сигнал {signum}, завершение работы...")
        self.running = False
    
    def _process_message(self, message) -> bool:
        """
        Обработка одного сообщения
        
        Args:
            message: Сообщение из Kafka
        
        Returns:
            bool: True если сообщение успешно обработано
        """
        try:
            # Парсим событие
            event_data = message.value
            event_type = EventType(event_data.get('event_type'))
            
            logger.info(
                f"📨 Получено событие {event_type} из топика {message.topic}, "
                f"партиция {message.partition}, offset {message.offset}"
            )
            
            # Находим обработчик
            handler = self.event_handlers.get(event_type)
            if not handler:
                logger.warning(f"⚠️ Обработчик для события {event_type} не найден")
                return True  # Пропускаем неизвестные события
            
            # Выполняем обработку
            success = handler(event_data)
            
            if success:
                logger.info(f"✅ Событие {event_type} успешно обработано")
            else:
                logger.error(f"❌ Ошибка обработки события {event_type}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
            return False
    
    def start_consuming(self):
        """Запуск потребления сообщений"""
        if not self.consumer:
            self._initialize_consumer()
        
        self.running = True
        logger.info(f"🚀 Начат процесс потребления сообщений из топиков: {self.topics}")
        
        try:
            while self.running:
                # Получаем сообщения
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                if not message_batch:
                    continue
                
                # Обрабатываем каждое сообщение
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        if not self.running:
                            break
                        
                        success = self._process_message(message)
                        
                        if not success:
                            # Здесь можно добавить логику для Dead Letter Queue
                            logger.error(f"❌ Сообщение не обработано, отправляем в DLQ")
                
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал прерывания")
        except Exception as e:
            logger.error(f"❌ Ошибка в процессе потребления: {e}")
        finally:
            self.stop_consuming()
    
    def stop_consuming(self):
        """Остановка потребления сообщений"""
        self.running = False
        if self.consumer:
            self.consumer.close()
            logger.info("🔒 Kafka Consumer закрыт")
