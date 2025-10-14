"""
Сервис для управления workflow заявок
Обрабатывает переходы между статусами заявок согласно бизнес-логике
"""

import logging
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models import RepairRequest, User, RequestStatus
from api.v1.schemas import RepairRequestUpdate

logger = logging.getLogger(__name__)

class RequestWorkflowService:
    """Сервис для управления workflow заявок"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_request(self, customer_id: int, request_data: dict) -> RepairRequest:
        """Создание новой заявки"""
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
        
        logger.info(f"✅ Создана новая заявка #{request.id} от заказчика {customer_id}")
        return request
    
    def assign_to_manager(self, request_id: int, manager_id: int) -> RepairRequest:
        """Назначение заявки менеджеру"""
        request = self.db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Заявка {request_id} не найдена")
        
        request.manager_id = manager_id
        request.status = RequestStatus.MANAGER_REVIEW
        request.processed_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(request)
        
        logger.info(f"✅ Заявка #{request_id} назначена менеджеру {manager_id}")
        return request
    
    def add_clarification(self, request_id: int, manager_id: int, clarification_details: str) -> RepairRequest:
        """Добавление уточнений от менеджера"""
        request = self.db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Заявка {request_id} не найдена")
        
        if request.manager_id != manager_id:
            raise ValueError("Только назначенный менеджер может добавлять уточнения")
        
        request.clarification_details = clarification_details
        request.status = RequestStatus.CLARIFICATION
        
        self.db.commit()
        self.db.refresh(request)
        
        logger.info(f"✅ Добавлены уточнения к заявке #{request_id}")
        return request
    
    def send_to_contractors(self, request_id: int, manager_id: int) -> RepairRequest:
        """Отправка заявки исполнителям"""
        request = self.db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Заявка {request_id} не найдена")
        
        if request.manager_id != manager_id:
            raise ValueError("Только назначенный менеджер может отправлять заявку исполнителям")
        
        request.status = RequestStatus.SENT_TO_CONTRACTORS
        request.sent_to_bot_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(request)
        
        logger.info(f"✅ Заявка #{request_id} отправлена исполнителям")
        return request
    
    def assign_contractor(self, request_id: int, contractor_id: int, manager_id: int) -> RepairRequest:
        """Назначение исполнителя на заявку"""
        request = self.db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Заявка {request_id} не найдена")
        
        if request.manager_id != manager_id:
            raise ValueError("Только назначенный менеджер может назначать исполнителя")
        
        # Проверяем, что исполнитель проверен службой безопасности
        from services.security_verification_service import get_security_verification_service
        security_service = get_security_verification_service(self.db)
        
        if not security_service.check_contractor_can_respond(contractor_id):
            raise ValueError("Исполнитель не может быть назначен: не прошел проверку службы безопасности")
        
        request.assigned_contractor_id = contractor_id
        request.status = RequestStatus.ASSIGNED
        request.assigned_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(request)
        
        logger.info(f"✅ Исполнитель {contractor_id} назначен на заявку #{request_id}")
        return request
    
    def start_work(self, request_id: int, contractor_id: int) -> RepairRequest:
        """Начало выполнения работ"""
        request = self.db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Заявка {request_id} не найдена")
        
        if request.assigned_contractor_id != contractor_id:
            raise ValueError("Только назначенный исполнитель может начинать работы")
        
        request.status = RequestStatus.IN_PROGRESS
        
        self.db.commit()
        self.db.refresh(request)
        
        logger.info(f"✅ Исполнитель {contractor_id} начал работы по заявке #{request_id}")
        return request
    
    def complete_work(self, request_id: int, contractor_id: int, final_price: Optional[int] = None) -> RepairRequest:
        """Завершение работ"""
        request = self.db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Заявка {request_id} не найдена")
        
        if request.assigned_contractor_id != contractor_id:
            raise ValueError("Только назначенный исполнитель может завершать работы")
        
        request.status = RequestStatus.COMPLETED
        if final_price:
            request.final_price = final_price
        
        self.db.commit()
        self.db.refresh(request)
        
        logger.info(f"✅ Работы по заявке #{request_id} завершены исполнителем {contractor_id}")
        return request
    
    def cancel_request(self, request_id: int, user_id: int, reason: str) -> RepairRequest:
        """Отмена заявки"""
        request = self.db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Заявка {request_id} не найдена")
        
        # Проверяем права на отмену
        can_cancel = (
            request.customer_id == user_id or  # Заказчик может отменить свою заявку
            request.manager_id == user_id or   # Менеджер может отменить назначенную заявку
            request.assigned_contractor_id == user_id  # Исполнитель может отменить назначенную заявку
        )
        
        if not can_cancel:
            raise ValueError("Недостаточно прав для отмены заявки")
        
        request.status = RequestStatus.CANCELLED
        request.manager_comment = f"Отменено: {reason}"
        
        self.db.commit()
        self.db.refresh(request)
        
        logger.info(f"✅ Заявка #{request_id} отменена пользователем {user_id}")
        return request
    
    def get_requests_for_manager(self, manager_id: int, status: Optional[str] = None) -> List[RepairRequest]:
        """Получение заявок для менеджера"""
        query = self.db.query(RepairRequest).filter(RepairRequest.manager_id == manager_id)
        
        if status:
            query = query.filter(RepairRequest.status == status)
        
        return query.order_by(RepairRequest.created_at.desc()).all()
    
    def get_available_requests(self) -> List[RepairRequest]:
        """Получение заявок, доступных для назначения менеджеру"""
        return self.db.query(RepairRequest).filter(
            RepairRequest.status == RequestStatus.NEW
        ).order_by(RepairRequest.created_at.desc()).all()
    
    def get_contractor_requests(self, contractor_id: int) -> List[RepairRequest]:
        """Получение заявок исполнителя"""
        return self.db.query(RepairRequest).filter(
            RepairRequest.assigned_contractor_id == contractor_id
        ).order_by(RepairRequest.created_at.desc()).all()
    
    def get_customer_requests(self, customer_id: int) -> List[RepairRequest]:
        """Получение заявок заказчика"""
        return self.db.query(RepairRequest).filter(
            RepairRequest.customer_id == customer_id
        ).order_by(RepairRequest.created_at.desc()).all()

def get_request_workflow_service(db: Session) -> RequestWorkflowService:
    """Получение экземпляра сервиса workflow заявок"""
    return RequestWorkflowService(db)
