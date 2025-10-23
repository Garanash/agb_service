# 🐍 Примеры кода для Apache Kafka

## 📦 Установка зависимостей

```bash
pip install kafka-python aiokafka pydantic python-dotenv
```

## 🔧 Базовые классы и конфигурация

### `kafka_config.py`
```python
"""
Конфигурация Kafka
"""
import os
from typing import Dict, Any
from pydantic import BaseSettings

class KafkaConfig(BaseSettings):
    """Конфигурация Kafka"""
    
    # Брокеры Kafka
    bootstrap_servers: str = "localhost:9092,localhost:9093,localhost:9094"
    
    # Настройки безопасности
    security_protocol: str = "PLAINTEXT"  # PLAINTEXT, SASL_PLAINTEXT, SASL_SSL, SSL
    sasl_mechanism: str = "PLAIN"
    sasl_username: str = ""
    sasl_password: str = ""
    
    # Настройки producer
    producer_acks: str = "all"  # all, 1, 0
    producer_retries: int = 3
    producer_batch_size: int = 16384
    producer_linger_ms: int = 10
    producer_compression_type: str = "snappy"
    
    # Настройки consumer
    consumer_group_id: str = "agregator-service"
    consumer_auto_offset_reset: str = "earliest"  # earliest, latest
    consumer_enable_auto_commit: bool = True
    consumer_auto_commit_interval_ms: int = 1000
    consumer_max_poll_records: int = 500
    
    # Топики
    topics: Dict[str, Dict[str, Any]] = {
        "request-events": {
            "partitions": 6,
            "replication_factor": 3,
            "retention_ms": 604800000  # 7 дней
        },
        "workflow-events": {
            "partitions": 3,
            "replication_factor": 3,
            "retention_ms": 2592000000  # 30 дней
        },
        "notification-events": {
            "partitions": 3,
            "replication_factor": 3,
            "retention_ms": 259200000  # 3 дня
        },
        "security-events": {
            "partitions": 3,
            "replication_factor": 3,
            "retention_ms": 7776000000  # 90 дней
        },
        "hr-events": {
            "partitions": 3,
            "replication_factor": 3,
            "retention_ms": 31536000000  # 365 дней
        },
        "audit-events": {
            "partitions": 6,
            "replication_factor": 3,
            "retention_ms": 31536000000  # 365 дней
        }
    }
    
    class Config:
        env_file = ".env"
        env_prefix = "KAFKA_"

# Глобальная конфигурация
kafka_config = KafkaConfig()
```

### `kafka_events.py`
```python
"""
Схемы событий Kafka
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

class EventType(str, Enum):
    """Типы событий"""
    # Request Events
    REQUEST_CREATED = "request.created"
    REQUEST_UPDATED = "request.updated"
    REQUEST_CANCELLED = "request.cancelled"
    REQUEST_CLARIFICATION_NEEDED = "request.clarification_needed"
    
    # Workflow Events
    WORKFLOW_MANAGER_ASSIGNED = "workflow.manager_assigned"
    WORKFLOW_SENT_TO_CONTRACTORS = "workflow.sent_to_contractors"
    WORKFLOW_CONTRACTOR_ASSIGNED = "workflow.contractor_assigned"
    WORKFLOW_WORK_STARTED = "workflow.work_started"
    WORKFLOW_WORK_COMPLETED = "workflow.work_completed"
    WORKFLOW_STATUS_CHANGED = "workflow.status_changed"
    
    # Notification Events
    NOTIFICATION_EMAIL_SENT = "notification.email.sent"
    NOTIFICATION_TELEGRAM_SENT = "notification.telegram.sent"
    NOTIFICATION_SMS_SENT = "notification.sms.sent"
    NOTIFICATION_FAILED = "notification.failed"
    
    # Security Events
    SECURITY_CONTRACTOR_VERIFIED = "security.contractor_verified"
    SECURITY_CONTRACTOR_REJECTED = "security.contractor_rejected"
    SECURITY_ACCESS_GRANTED = "security.access_granted"
    SECURITY_ACCESS_REVOKED = "security.access_revoked"
    
    # HR Events
    HR_DOCUMENT_CREATED = "hr.document_created"
    HR_DOCUMENT_SIGNED = "hr.document_signed"
    HR_CONTRACT_GENERATED = "hr.contract_generated"
    HR_PAYMENT_PROCESSED = "hr.payment_processed"
    
    # Audit Events
    AUDIT_USER_ACTION = "audit.user_action"
    AUDIT_SYSTEM_EVENT = "audit.system_event"
    AUDIT_ERROR_OCCURRED = "audit.error_occurred"
    AUDIT_PERFORMANCE_METRIC = "audit.performance_metric"

class BaseEvent(BaseModel):
    """Базовый класс для всех событий"""
    event_type: EventType
    event_id: str = Field(..., description="Уникальный ID события")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"
    source: str = "agregator-service"
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RequestCreatedEvent(BaseEvent):
    """Событие создания заявки"""
    event_type: EventType = EventType.REQUEST_CREATED
    request_id: int
    customer_id: int
    title: str
    description: str
    urgency: str
    region: str
    city: str
    address: str
    equipment_type: Optional[str] = None
    priority: str = "normal"

class WorkflowContractorAssignedEvent(BaseEvent):
    """Событие назначения исполнителя"""
    event_type: EventType = EventType.WORKFLOW_CONTRACTOR_ASSIGNED
    request_id: int
    contractor_id: int
    manager_id: int
    previous_status: str
    new_status: str = "assigned"
    assignment_reason: Optional[str] = None

class NotificationTelegramSentEvent(BaseEvent):
    """Событие отправки Telegram уведомления"""
    event_type: EventType = EventType.NOTIFICATION_TELEGRAM_SENT
    recipient_id: int
    recipient_telegram_username: str
    message_type: str  # assignment, completion, reminder
    request_id: Optional[int] = None
    message_content: str
    delivery_status: str = "sent"
    telegram_message_id: Optional[int] = None

class SecurityContractorVerifiedEvent(BaseEvent):
    """Событие верификации исполнителя"""
    event_type: EventType = EventType.SECURITY_CONTRACTOR_VERIFIED
    contractor_id: int
    verification_type: str  # identity, documents, background_check
    verification_result: str  # approved, rejected, pending
    verified_by: int  # security officer id
    verification_notes: Optional[str] = None
    documents_verified: List[str] = Field(default_factory=list)

class AuditUserActionEvent(BaseEvent):
    """Событие аудита действий пользователя"""
    event_type: EventType = EventType.AUDIT_USER_ACTION
    user_id: int
    user_role: str
    action: str
    resource_type: str  # request, user, document
    resource_id: Optional[int] = None
    ip_address: str
    user_agent: str
    success: bool
    error_message: Optional[str] = None
    additional_data: Dict[str, Any] = Field(default_factory=dict)
```

## 📤 Kafka Producer

### `kafka_producer.py`
```python
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
from kafka_config import kafka_config
from kafka_events import BaseEvent

logger = logging.getLogger(__name__)

class KafkaEventProducer:
    """Producer для отправки событий в Kafka"""
    
    def __init__(self):
        self.producer = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Инициализация Kafka producer"""
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
            # Генерируем уникальный ID события если не задан
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
```

## 📥 Kafka Consumer

### `kafka_consumer.py`
```python
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
from kafka_config import kafka_config
from kafka_events import BaseEvent, EventType

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
```

## 🔄 Интеграция с существующими сервисами

### `request_service_integration.py`
```python
"""
Интеграция Request Service с Kafka
"""
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from kafka_producer import kafka_producer
from kafka_events import RequestCreatedEvent, WorkflowContractorAssignedEvent
from models import RepairRequest, RequestStatus

logger = logging.getLogger(__name__)

class RequestServiceKafkaIntegration:
    """Интеграция Request Service с Kafka"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_request_with_event(self, customer_id: int, request_data: dict) -> RepairRequest:
        """
        Создание заявки с публикацией события
        
        Args:
            customer_id: ID заказчика
            request_data: Данные заявки
        
        Returns:
            RepairRequest: Созданная заявка
        """
        # Создаем заявку в БД (существующая логика)
        request = RepairRequest(
            customer_id=customer_id,
            title=request_data.get('title'),
            description=request_data.get('description'),
            urgency=request_data.get('urgency'),
            preferred_date=request_data.get('preferred_date'),
            address=request_data.get('address'),
            city=request_data.get('city'),
            region=request_data.get('region'),
            equipment_type=request_data.get('equipment_type'),
            equipment_brand=request_data.get('equipment_brand'),
            equipment_model=request_data.get('equipment_model'),
            problem_description=request_data.get('problem_description'),
            priority=request_data.get('priority', 'normal'),
            status=RequestStatus.NEW
        )
        
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        # Публикуем событие
        event = RequestCreatedEvent(
            request_id=request.id,
            customer_id=customer_id,
            title=request.title,
            description=request.description,
            urgency=request.urgency or "medium",
            region=request.region or "unknown",
            city=request.city or "",
            address=request.address or "",
            equipment_type=request.equipment_type,
            priority=request.priority
        )
        
        success = kafka_producer.publish_event("request-events", event)
        
        if success:
            logger.info(f"✅ Событие создания заявки #{request.id} опубликовано")
        else:
            logger.error(f"❌ Не удалось опубликовать событие для заявки #{request.id}")
        
        return request
    
    def assign_contractor_with_event(
        self, 
        request_id: int, 
        contractor_id: int, 
        manager_id: int
    ) -> RepairRequest:
        """
        Назначение исполнителя с публикацией события
        
        Args:
            request_id: ID заявки
            contractor_id: ID исполнителя
            manager_id: ID менеджера
        
        Returns:
            RepairRequest: Обновленная заявка
        """
        # Обновляем заявку в БД
        request = self.db.query(RepairRequest).filter(
            RepairRequest.id == request_id
        ).first()
        
        if not request:
            raise ValueError(f"Заявка {request_id} не найдена")
        
        previous_status = request.status
        request.status = RequestStatus.ASSIGNED
        request.assigned_contractor_id = contractor_id
        
        self.db.commit()
        self.db.refresh(request)
        
        # Публикуем событие
        event = WorkflowContractorAssignedEvent(
            request_id=request_id,
            contractor_id=contractor_id,
            manager_id=manager_id,
            previous_status=previous_status,
            new_status=RequestStatus.ASSIGNED,
            assignment_reason="Manager assignment"
        )
        
        success = kafka_producer.publish_event("workflow-events", event)
        
        if success:
            logger.info(f"✅ Событие назначения исполнителя для заявки #{request_id} опубликовано")
        else:
            logger.error(f"❌ Не удалось опубликовать событие назначения для заявки #{request_id}")
        
        return request
```

### `notification_service_consumer.py`
```python
"""
Consumer для Notification Service
"""
import logging
import asyncio
from typing import Dict, Any
from sqlalchemy.orm import Session
from kafka_consumer import KafkaEventConsumer
from kafka_events import EventType, RequestCreatedEvent, WorkflowContractorAssignedEvent
from services.telegram_bot_service import TelegramBotService
from services.email_service import EmailService

logger = logging.getLogger(__name__)

class NotificationServiceConsumer:
    """Consumer для обработки событий уведомлений"""
    
    def __init__(self, db: Session):
        self.db = db
        self.telegram_service = TelegramBotService(db)
        self.email_service = EmailService()
        
        # Инициализируем consumer
        self.consumer = KafkaEventConsumer(
            group_id="notification-service",
            topics=["request-events", "workflow-events"]
        )
        
        # Регистрируем обработчики
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрация обработчиков событий"""
        self.consumer.register_handler(
            EventType.REQUEST_CREATED,
            self._handle_request_created
        )
        
        self.consumer.register_handler(
            EventType.WORKFLOW_CONTRACTOR_ASSIGNED,
            self._handle_contractor_assigned
        )
    
    def _handle_request_created(self, event_data: Dict[str, Any]) -> bool:
        """
        Обработка события создания заявки
        
        Args:
            event_data: Данные события
        
        Returns:
            bool: True если обработка успешна
        """
        try:
            event = RequestCreatedEvent(**event_data)
            
            # Отправляем подтверждение заказчику
            asyncio.create_task(self._send_customer_confirmation(event))
            
            # Уведомляем менеджеров
            asyncio.create_task(self._notify_managers(event))
            
            logger.info(f"✅ Обработано событие создания заявки #{event.request_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки события создания заявки: {e}")
            return False
    
    def _handle_contractor_assigned(self, event_data: Dict[str, Any]) -> bool:
        """
        Обработка события назначения исполнителя
        
        Args:
            event_data: Данные события
        
        Returns:
            bool: True если обработка успешна
        """
        try:
            event = WorkflowContractorAssignedEvent(**event_data)
            
            # Уведомляем исполнителя
            asyncio.create_task(self._notify_contractor(event))
            
            # Уведомляем заказчика
            asyncio.create_task(self._notify_customer(event))
            
            logger.info(f"✅ Обработано событие назначения исполнителя для заявки #{event.request_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки события назначения исполнителя: {e}")
            return False
    
    async def _send_customer_confirmation(self, event: RequestCreatedEvent):
        """Отправка подтверждения заказчику"""
        try:
            # Получаем данные заказчика
            customer_profile = self.db.query(CustomerProfile).filter(
                CustomerProfile.id == event.customer_id
            ).first()
            
            if customer_profile and customer_profile.user.email:
                # Отправляем email
                await self.email_service.send_request_confirmation(
                    email=customer_profile.user.email,
                    request_id=event.request_id,
                    title=event.title
                )
                
                logger.info(f"✅ Подтверждение отправлено заказчику {event.customer_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки подтверждения заказчику: {e}")
    
    async def _notify_managers(self, event: RequestCreatedEvent):
        """Уведомление менеджеров о новой заявке"""
        try:
            # Получаем список менеджеров
            managers = self.db.query(User).filter(User.role == "manager").all()
            
            for manager in managers:
                if manager.email:
                    await self.email_service.send_new_request_notification(
                        email=manager.email,
                        request_id=event.request_id,
                        title=event.title,
                        urgency=event.urgency
                    )
            
            logger.info(f"✅ Менеджеры уведомлены о новой заявке #{event.request_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка уведомления менеджеров: {e}")
    
    async def _notify_contractor(self, event: WorkflowContractorAssignedEvent):
        """Уведомление исполнителя о назначении"""
        try:
            # Отправляем уведомление в Telegram
            success = await self.telegram_service.send_request_assignment_notification(
                contractor_id=event.contractor_id,
                request_id=event.request_id
            )
            
            if success:
                logger.info(f"✅ Исполнитель {event.contractor_id} уведомлен о назначении")
            else:
                logger.warning(f"⚠️ Не удалось уведомить исполнителя {event.contractor_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка уведомления исполнителя: {e}")
    
    async def _notify_customer(self, event: WorkflowContractorAssignedEvent):
        """Уведомление заказчика о назначении исполнителя"""
        try:
            # Получаем данные заявки
            request = self.db.query(RepairRequest).filter(
                RepairRequest.id == event.request_id
            ).first()
            
            if request and request.customer.user.email:
                # Отправляем email заказчику
                await self.email_service.send_contractor_assigned_notification(
                    email=request.customer.user.email,
                    request_id=event.request_id,
                    contractor_name=request.assigned_contractor.first_name + " " + request.assigned_contractor.last_name
                )
                
                logger.info(f"✅ Заказчик уведомлен о назначении исполнителя для заявки #{event.request_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка уведомления заказчика: {e}")
    
    def start(self):
        """Запуск consumer"""
        logger.info("🚀 Запуск Notification Service Consumer")
        self.consumer.start_consuming()
```

## 🚀 Запуск сервисов

### `main_kafka_service.py`
```python
"""
Главный файл для запуска Kafka сервисов
"""
import logging
import asyncio
from database import get_db
from notification_service_consumer import NotificationServiceConsumer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Главная функция"""
    logger.info("🚀 Запуск Kafka сервисов")
    
    # Получаем подключение к БД
    db = next(get_db())
    
    try:
        # Создаем и запускаем consumer
        notification_consumer = NotificationServiceConsumer(db)
        notification_consumer.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска сервисов: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
```

## 📊 Мониторинг и метрики

### `kafka_monitoring.py`
```python
"""
Мониторинг Kafka
"""
import logging
from typing import Dict, Any
from kafka import KafkaAdminClient
from kafka.admin import ConfigResource, ConfigResourceType
from kafka_config import kafka_config

logger = logging.getLogger(__name__)

class KafkaMonitoring:
    """Класс для мониторинга Kafka"""
    
    def __init__(self):
        self.admin_client = None
        self._initialize_admin_client()
    
    def _initialize_admin_client(self):
        """Инициализация admin client"""
        try:
            admin_config = {
                'bootstrap_servers': kafka_config.bootstrap_servers.split(','),
            }
            
            if kafka_config.security_protocol != "PLAINTEXT":
                admin_config.update({
                    'security_protocol': kafka_config.security_protocol,
                    'sasl_mechanism': kafka_config.sasl_mechanism,
                    'sasl_plain_username': kafka_config.sasl_username,
                    'sasl_plain_password': kafka_config.sasl_password,
                })
            
            self.admin_client = KafkaAdminClient(**admin_config)
            logger.info("✅ Kafka Admin Client инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Kafka Admin Client: {e}")
            raise
    
    def get_topic_metrics(self, topic: str) -> Dict[str, Any]:
        """
        Получение метрик топика
        
        Args:
            topic: Название топика
        
        Returns:
            Dict[str, Any]: Метрики топика
        """
        try:
            # Получаем метаданные топика
            metadata = self.admin_client.describe_topics([topic])
            
            if topic not in metadata:
                return {"error": f"Топик {topic} не найден"}
            
            topic_metadata = metadata[topic]
            
            metrics = {
                "topic": topic,
                "partitions": len(topic_metadata.partitions),
                "replication_factor": len(topic_metadata.partitions[0].replicas),
                "partition_details": []
            }
            
            for partition_id, partition_metadata in topic_metadata.partitions.items():
                partition_info = {
                    "partition": partition_id,
                    "leader": partition_metadata.leader,
                    "replicas": partition_metadata.replicas,
                    "isr": partition_metadata.isr  # In-Sync Replicas
                }
                metrics["partition_details"].append(partition_info)
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения метрик топика {topic}: {e}")
            return {"error": str(e)}
    
    def get_consumer_group_metrics(self, group_id: str) -> Dict[str, Any]:
        """
        Получение метрик consumer group
        
        Args:
            group_id: ID consumer group
        
        Returns:
            Dict[str, Any]: Метрики consumer group
        """
        try:
            # Получаем информацию о consumer group
            consumer_groups = self.admin_client.describe_consumer_groups([group_id])
            
            if group_id not in consumer_groups:
                return {"error": f"Consumer group {group_id} не найден"}
            
            group_info = consumer_groups[group_id]
            
            metrics = {
                "group_id": group_id,
                "state": group_info.state,
                "members": len(group_info.members),
                "member_details": []
            }
            
            for member_id, member_info in group_info.members.items():
                member_detail = {
                    "member_id": member_id,
                    "client_id": member_info.client_id,
                    "client_host": member_info.client_host,
                    "assigned_partitions": member_info.assignment.partitions
                }
                metrics["member_details"].append(member_detail)
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения метрик consumer group {group_id}: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Закрытие admin client"""
        if self.admin_client:
            self.admin_client.close()
            logger.info("🔒 Kafka Admin Client закрыт")

# Пример использования
if __name__ == "__main__":
    monitoring = KafkaMonitoring()
    
    # Получаем метрики топика
    topic_metrics = monitoring.get_topic_metrics("request-events")
    print("📊 Метрики топика request-events:")
    print(topic_metrics)
    
    # Получаем метрики consumer group
    group_metrics = monitoring.get_consumer_group_metrics("notification-service")
    print("\n📊 Метрики consumer group notification-service:")
    print(group_metrics)
    
    monitoring.close()
```

