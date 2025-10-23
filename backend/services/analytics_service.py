"""
Сервис для отправки событий аналитики в Kafka
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from kafka_events import kafka_producer
from kafka_events.analytics_events import (
    UserLoginEvent, UserRegistrationEvent, RequestCreatedEvent,
    RequestStatusChangedEvent, RequestCompletedEvent, ContractorAssignedEvent,
    PageViewEvent, ActionPerformedEvent
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Сервис для отправки событий аналитики"""
    
    def __init__(self):
        self.producer = kafka_producer
    
    def track_user_login(
        self, 
        user_id: int, 
        user_role: str,
        login_method: str = "web",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_duration: Optional[int] = None
    ):
        """Отправка события входа пользователя"""
        try:
            event = UserLoginEvent(
                user_id=user_id,
                user_role=user_role,
                login_method=login_method,
                ip_address=ip_address,
                user_agent=user_agent,
                session_duration=session_duration
            )
            
            self.producer.send_event("analytics", event, key=str(user_id))
            logger.info(f"User login event sent for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send user login event: {e}")
    
    def track_user_registration(
        self, 
        user_id: int, 
        user_role: str,
        registration_source: str = "web",
        referral_source: Optional[str] = None
    ):
        """Отправка события регистрации пользователя"""
        try:
            event = UserRegistrationEvent(
                user_id=user_id,
                user_role=user_role,
                registration_source=registration_source,
                referral_source=referral_source
            )
            
            self.producer.send_event("analytics", event, key=str(user_id))
            logger.info(f"User registration event sent for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send user registration event: {e}")
    
    def track_request_created(
        self, 
        request_id: int, 
        customer_id: int,
        equipment_type: Optional[str] = None,
        equipment_brand: Optional[str] = None,
        urgency: Optional[str] = None,
        region: Optional[str] = None,
        estimated_cost: Optional[int] = None
    ):
        """Отправка события создания заявки"""
        try:
            event = RequestCreatedEvent(
                request_id=request_id,
                customer_id=customer_id,
                equipment_type=equipment_type,
                equipment_brand=equipment_brand,
                urgency=urgency,
                region=region,
                estimated_cost=estimated_cost
            )
            
            self.producer.send_event("analytics", event, key=str(request_id))
            logger.info(f"Request created event sent for request {request_id}")
            
        except Exception as e:
            logger.error(f"Failed to send request created event: {e}")
    
    def track_request_status_changed(
        self, 
        request_id: int, 
        old_status: str, 
        new_status: str,
        changed_by_user_id: int,
        changed_by_role: str,
        processing_time_hours: Optional[float] = None
    ):
        """Отправка события изменения статуса заявки"""
        try:
            event = RequestStatusChangedEvent(
                request_id=request_id,
                old_status=old_status,
                new_status=new_status,
                changed_by_user_id=changed_by_user_id,
                changed_by_role=changed_by_role,
                processing_time_hours=processing_time_hours
            )
            
            self.producer.send_event("analytics", event, key=str(request_id))
            logger.info(f"Request status changed event sent for request {request_id}")
            
        except Exception as e:
            logger.error(f"Failed to send request status changed event: {e}")
    
    def track_request_completed(
        self, 
        request_id: int, 
        customer_id: int,
        contractor_id: Optional[int] = None,
        completion_time_hours: Optional[float] = None,
        final_cost: Optional[int] = None,
        customer_rating: Optional[int] = None
    ):
        """Отправка события завершения заявки"""
        try:
            event = RequestCompletedEvent(
                request_id=request_id,
                customer_id=customer_id,
                contractor_id=contractor_id,
                completion_time_hours=completion_time_hours,
                final_cost=final_cost,
                customer_rating=customer_rating
            )
            
            self.producer.send_event("analytics", event, key=str(request_id))
            logger.info(f"Request completed event sent for request {request_id}")
            
        except Exception as e:
            logger.error(f"Failed to send request completed event: {e}")
    
    def track_contractor_assigned(
        self, 
        request_id: int, 
        contractor_id: int,
        assigned_by_user_id: int,
        assignment_method: str = "manual"
    ):
        """Отправка события назначения исполнителя"""
        try:
            event = ContractorAssignedEvent(
                request_id=request_id,
                contractor_id=contractor_id,
                assigned_by_user_id=assigned_by_user_id,
                assignment_method=assignment_method
            )
            
            self.producer.send_event("analytics", event, key=str(request_id))
            logger.info(f"Contractor assigned event sent for request {request_id}")
            
        except Exception as e:
            logger.error(f"Failed to send contractor assigned event: {e}")
    
    def track_page_view(
        self, 
        user_id: int, 
        user_role: str,
        page_path: str,
        page_title: Optional[str] = None,
        referrer: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Отправка события просмотра страницы"""
        try:
            event = PageViewEvent(
                user_id=user_id,
                user_role=user_role,
                page_path=page_path,
                page_title=page_title,
                referrer=referrer,
                session_id=session_id
            )
            
            self.producer.send_event("analytics", event, key=str(user_id))
            logger.info(f"Page view event sent for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send page view event: {e}")
    
    def track_action_performed(
        self, 
        user_id: int, 
        user_role: str,
        action_name: str,
        action_category: str,
        target_entity_type: Optional[str] = None,
        target_entity_id: Optional[int] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Отправка события выполнения действия"""
        try:
            event = ActionPerformedEvent(
                user_id=user_id,
                user_role=user_role,
                action_name=action_name,
                action_category=action_category,
                target_entity_type=target_entity_type,
                target_entity_id=target_entity_id,
                additional_data=additional_data
            )
            
            self.producer.send_event("analytics", event, key=str(user_id))
            logger.info(f"Action performed event sent for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send action performed event: {e}")


# Глобальный экземпляр сервиса
analytics_service = AnalyticsService()
