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

class RequestUpdatedEvent(BaseEvent):
    """Событие обновления заявки"""
    event_type: EventType = EventType.REQUEST_UPDATED
    request_id: int
    customer_id: int
    updated_fields: Dict[str, Any]
    updated_by: int
    update_reason: Optional[str] = None

class RequestCancelledEvent(BaseEvent):
    """Событие отмены заявки"""
    event_type: EventType = EventType.REQUEST_CANCELLED
    request_id: int
    customer_id: int
    cancelled_by: int
    cancellation_reason: str

class WorkflowManagerAssignedEvent(BaseEvent):
    """Событие назначения менеджера"""
    event_type: EventType = EventType.WORKFLOW_MANAGER_ASSIGNED
    request_id: int
    manager_id: int
    assigned_by: int
    assignment_reason: Optional[str] = None

class WorkflowContractorAssignedEvent(BaseEvent):
    """Событие назначения исполнителя"""
    event_type: EventType = EventType.WORKFLOW_CONTRACTOR_ASSIGNED
    request_id: int
    contractor_id: int
    manager_id: int
    previous_status: str
    new_status: str = "assigned"
    assignment_reason: Optional[str] = None

class WorkflowWorkCompletedEvent(BaseEvent):
    """Событие завершения работы"""
    event_type: EventType = EventType.WORKFLOW_WORK_COMPLETED
    request_id: int
    contractor_id: int
    completion_data: Dict[str, Any]
    completion_notes: Optional[str] = None

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

class NotificationEmailSentEvent(BaseEvent):
    """Событие отправки Email уведомления"""
    event_type: EventType = EventType.NOTIFICATION_EMAIL_SENT
    recipient_email: str
    recipient_id: Optional[int] = None
    message_type: str
    request_id: Optional[int] = None
    subject: str
    delivery_status: str = "sent"

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
