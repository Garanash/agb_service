"""
Kafka модуль для агрегатора сервисных услуг
"""

from .kafka_config import kafka_config, KafkaConfig
from .kafka_events import (
    BaseEvent, EventType,
    RequestCreatedEvent, RequestUpdatedEvent, RequestCancelledEvent,
    WorkflowManagerAssignedEvent, WorkflowContractorAssignedEvent, WorkflowWorkCompletedEvent,
    NotificationTelegramSentEvent, NotificationEmailSentEvent,
    SecurityContractorVerifiedEvent, AuditUserActionEvent
)
from .kafka_producer import KafkaEventProducer, kafka_producer
from .kafka_consumer import KafkaEventConsumer

__all__ = [
    'kafka_config', 'KafkaConfig',
    'BaseEvent', 'EventType',
    'RequestCreatedEvent', 'RequestUpdatedEvent', 'RequestCancelledEvent',
    'WorkflowManagerAssignedEvent', 'WorkflowContractorAssignedEvent', 'WorkflowWorkCompletedEvent',
    'NotificationTelegramSentEvent', 'NotificationEmailSentEvent',
    'SecurityContractorVerifiedEvent', 'AuditUserActionEvent',
    'KafkaEventProducer', 'kafka_producer',
    'KafkaEventConsumer'
]
