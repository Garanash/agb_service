"""
Kafka Producer для отправки событий
"""
import json
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError
from .kafka_config import kafka_config
from .kafka_events import BaseEvent

logger = logging.getLogger(__name__)

class KafkaEventProducer:
    """Producer для отправки событий в Kafka"""
    
    def __init__(self):
        self.producer = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Инициализация Kafka producer"""
        if not kafka_config.enabled:
            logger.info("Kafka отключен в конфигурации")
            return
            
        try:
            producer_config = {
                'bootstrap_servers': kafka_config.bootstrap_servers.split(','),
                'acks': kafka_config.producer_acks,
                'retries': kafka_config.producer_retries,
                'batch_size': kafka_config.producer_batch_size,
                'linger_ms': kafka_config.producer_linger_ms,
                'compression_type': kafka_config.producer_compression_type,
                'value_serializer': lambda v: json.dumps(v, default=str).encode('utf-8'),
                'key_serializer': lambda k: str(k).encode('utf-8') if k else None,
                'request_timeout_ms': 30000,
                'metadata_max_age_ms': 300000,
            }
            
            # Добавляем настройки безопасности если нужно
            if kafka_config.security_protocol != "PLAINTEXT":
                producer_config.update({
                    'security_protocol': kafka_config.security_protocol,
                    'sasl_mechanism': kafka_config.sasl_mechanism,
                    'sasl_plain_username': kafka_config.sasl_username,
                    'sasl_plain_password': kafka_config.sasl_password,
                })
            
            self.producer = KafkaProducer(**producer_config)
            logger.info("✅ Kafka Producer инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Kafka Producer: {e}")
            raise
    
    def publish_event(
        self, 
        topic: str, 
        event: BaseEvent, 
        key: Optional[str] = None,
        partition: Optional[int] = None
    ) -> bool:
        """
        Публикация события в Kafka
        
        Args:
            topic: Название топика
            event: Объект события
            key: Ключ для партиционирования (опционально)
            partition: Конкретная партиция (опционально)
        
        Returns:
            bool: True если событие успешно отправлено
        """
        try:
            if not kafka_config.enabled:
                logger.info(f"Kafka отключен, событие {event.event_type} не отправлено")
                return True
                
            if not self.producer:
                logger.error("Kafka producer не инициализирован")
                return False
            if not event.event_id:
                event.event_id = str(uuid.uuid4())
            
            # Добавляем correlation_id если не задан
            if not event.correlation_id:
                event.correlation_id = str(uuid.uuid4())
            
            # Подготавливаем данные для отправки
            event_data = event.dict()
            
            # Определяем ключ для партиционирования
            partition_key = key or self._get_partition_key(event)
            
            # Отправляем событие
            future = self.producer.send(
                topic=topic,
                value=event_data,
                key=partition_key,
                partition=partition
            )
            
            # Ждем подтверждения
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"✅ Событие {event.event_type} отправлено в топик {topic}, "
                f"партиция {record_metadata.partition}, "
                f"offset {record_metadata.offset}"
            )
            
            return True
            
        except KafkaTimeoutError:
            logger.error(f"⏰ Таймаут отправки события {event.event_type} в топик {topic}")
            return False
        except KafkaError as e:
            logger.error(f"❌ Kafka ошибка при отправке события {event.event_type}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при отправке события {event.event_type}: {e}")
            return False
    
    def _get_partition_key(self, event: BaseEvent) -> str:
        """
        Определяет ключ для партиционирования на основе типа события
        
        Args:
            event: Событие
        
        Returns:
            str: Ключ для партиционирования
        """
        # Для событий заявок используем request_id
        if hasattr(event, 'request_id'):
            return str(event.request_id)
        
        # Для событий пользователей используем user_id
        if hasattr(event, 'user_id'):
            return str(event.user_id)
        
        # Для событий исполнителей используем contractor_id
        if hasattr(event, 'contractor_id'):
            return str(event.contractor_id)
        
        # По умолчанию используем event_id
        return event.event_id
    
    def publish_batch(self, events: list) -> Dict[str, int]:
        """
        Публикация пакета событий
        
        Args:
            events: Список кортежей (topic, event, key)
        
        Returns:
            Dict[str, int]: Статистика отправки
        """
        results = {"success": 0, "failed": 0}
        
        for topic, event, key in events:
            if self.publish_event(topic, event, key):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"📊 Пакетная отправка завершена: {results}")
        return results
    
    def close(self):
        """Закрытие producer"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("🔒 Kafka Producer закрыт")

# Глобальный экземпляр producer
kafka_producer = KafkaEventProducer()
