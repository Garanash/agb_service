"""
События для аналитики системы
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from kafka_events.kafka_events import BaseEvent


class AnalyticsEventType(str, Enum):
    """Типы событий аналитики"""
    USER_LOGIN = "user_login"
    USER_REGISTRATION = "user_registration"
    REQUEST_CREATED = "request_created"
    REQUEST_STATUS_CHANGED = "request_status_changed"
    REQUEST_COMPLETED = "request_completed"
    CONTRACTOR_ASSIGNED = "contractor_assigned"
    PAGE_VIEW = "page_view"
    ACTION_PERFORMED = "action_performed"


class UserLoginEvent(BaseEvent):
    """Событие входа пользователя в систему"""
    event_type: AnalyticsEventType = AnalyticsEventType.USER_LOGIN
    user_id: int
    user_role: str
    login_method: str = "web"  # web, mobile, api
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_duration: Optional[int] = None  # в секундах


class UserRegistrationEvent(BaseEvent):
    """Событие регистрации нового пользователя"""
    event_type: AnalyticsEventType = AnalyticsEventType.USER_REGISTRATION
    user_id: int
    user_role: str
    registration_source: str = "web"  # web, mobile, api, admin
    referral_source: Optional[str] = None


class RequestCreatedEvent(BaseEvent):
    """Событие создания новой заявки"""
    event_type: AnalyticsEventType = AnalyticsEventType.REQUEST_CREATED
    request_id: int
    customer_id: int
    equipment_type: Optional[str] = None
    equipment_brand: Optional[str] = None
    urgency: Optional[str] = None
    region: Optional[str] = None
    estimated_cost: Optional[int] = None


class RequestStatusChangedEvent(BaseEvent):
    """Событие изменения статуса заявки"""
    event_type: AnalyticsEventType = AnalyticsEventType.REQUEST_STATUS_CHANGED
    request_id: int
    old_status: str
    new_status: str
    changed_by_user_id: int
    changed_by_role: str
    processing_time_hours: Optional[float] = None


class RequestCompletedEvent(BaseEvent):
    """Событие завершения заявки"""
    event_type: AnalyticsEventType = AnalyticsEventType.REQUEST_COMPLETED
    request_id: int
    customer_id: int
    contractor_id: Optional[int] = None
    completion_time_hours: Optional[float] = None
    final_cost: Optional[int] = None
    customer_rating: Optional[int] = None


class ContractorAssignedEvent(BaseEvent):
    """Событие назначения исполнителя"""
    event_type: AnalyticsEventType = AnalyticsEventType.CONTRACTOR_ASSIGNED
    request_id: int
    contractor_id: int
    assigned_by_user_id: int
    assignment_method: str = "manual"  # manual, automatic, matching


class PageViewEvent(BaseEvent):
    """Событие просмотра страницы"""
    event_type: AnalyticsEventType = AnalyticsEventType.PAGE_VIEW
    user_id: int
    user_role: str
    page_path: str
    page_title: Optional[str] = None
    referrer: Optional[str] = None
    session_id: Optional[str] = None


class ActionPerformedEvent(BaseEvent):
    """Событие выполнения действия пользователем"""
    event_type: AnalyticsEventType = AnalyticsEventType.ACTION_PERFORMED
    user_id: int
    user_role: str
    action_name: str
    action_category: str
    target_entity_type: Optional[str] = None  # request, user, contractor, etc.
    target_entity_id: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None
