"""
Consumer для Notification Service
"""
import logging
import asyncio
from typing import Dict, Any
from sqlalchemy.orm import Session
from kafka.kafka_consumer import KafkaEventConsumer
from kafka.kafka_events import EventType, RequestCreatedEvent, WorkflowContractorAssignedEvent
from services.telegram_bot_service import TelegramBotService

logger = logging.getLogger(__name__)

class NotificationServiceConsumer:
    """Consumer для обработки событий уведомлений"""
    
    def __init__(self, db: Session):
        self.db = db
        self.telegram_service = TelegramBotService(db)
        
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
            from models import CustomerProfile, User
            
            customer_profile = self.db.query(CustomerProfile).filter(
                CustomerProfile.id == event.customer_id
            ).first()
            
            if customer_profile and customer_profile.user.email:
                # Отправляем email подтверждение
                await self._send_email_confirmation(
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
            from models import User
            
            managers = self.db.query(User).filter(User.role == "manager").all()
            
            for manager in managers:
                if manager.email:
                    await self._send_email_notification(
                        email=manager.email,
                        subject=f"Новая заявка #{event.request_id}",
                        message=f"Создана новая заявка: {event.title}\nСрочность: {event.urgency}\nРегион: {event.region}"
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
            from models import RepairRequest
            
            request = self.db.query(RepairRequest).filter(
                RepairRequest.id == event.request_id
            ).first()
            
            if request and request.customer.user.email:
                # Отправляем email заказчику
                await self._send_email_notification(
                    email=request.customer.user.email,
                    subject=f"Исполнитель назначен на заявку #{event.request_id}",
                    message=f"На вашу заявку назначен исполнитель. Мы свяжемся с вами в ближайшее время."
                )
                
                logger.info(f"✅ Заказчик уведомлен о назначении исполнителя для заявки #{event.request_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка уведомления заказчика: {e}")
    
    async def _send_email_confirmation(self, email: str, request_id: int, title: str):
        """Отправка email подтверждения"""
        try:
            # Здесь должна быть интеграция с email сервисом
            # Пока просто логируем
            logger.info(f"📧 Email подтверждение отправлен на {email} для заявки #{request_id}: {title}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки email подтверждения: {e}")
    
    async def _send_email_notification(self, email: str, subject: str, message: str):
        """Отправка email уведомления"""
        try:
            # Здесь должна быть интеграция с email сервисом
            # Пока просто логируем
            logger.info(f"📧 Email уведомление отправлен на {email}: {subject}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки email уведомления: {e}")
    
    def start(self):
        """Запуск consumer"""
        logger.info("🚀 Запуск Notification Service Consumer")
        self.consumer.start_consuming()
