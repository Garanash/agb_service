"""
API endpoints для управления workflow заявок
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import RepairRequest, User
from api.v1.schemas import (
    RepairRequestCreate, RepairRequestUpdate, RepairRequestResponse,
    RequestStatus
)
from api.v1.dependencies import get_current_user
from services.request_workflow_service import get_request_workflow_service, RequestWorkflowService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=RepairRequestResponse)
async def create_request(
    request_data: RepairRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание новой заявки заказчиком"""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только заказчики могут создавать заявки"
        )
    
    # Получаем профиль заказчика
    customer_profile = db.query(User).filter(User.id == current_user.id).first()
    if not customer_profile or not customer_profile.customer_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Профиль заказчика не найден"
        )
    
    workflow_service = get_request_workflow_service(db)
    request = workflow_service.create_request(
        customer_profile.customer_profile.id,
        request_data.dict()
    )
    
    return RepairRequestResponse.from_orm(request)

@router.get("/", response_model=List[RepairRequestResponse])
async def get_requests(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение заявок в зависимости от роли пользователя"""
    workflow_service = get_request_workflow_service(db)
    
    if current_user.role == "customer":
        customer_profile = current_user.customer_profile
        if not customer_profile:
            return []
        requests = workflow_service.get_customer_requests(customer_profile.id)
    elif current_user.role == "manager":
        requests = workflow_service.get_requests_for_manager(current_user.id, status_filter)
    elif current_user.role == "contractor":
        contractor_profile = current_user.contractor_profile
        if not contractor_profile:
            return []
        requests = workflow_service.get_contractor_requests(contractor_profile.id)
    elif current_user.role == "admin":
        # Админ видит все заявки
        query = db.query(RepairRequest)
        if status_filter:
            query = query.filter(RepairRequest.status == status_filter)
        requests = query.order_by(RepairRequest.created_at.desc()).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра заявок"
        )
    
    return [RepairRequestResponse.from_orm(req) for req in requests]

@router.get("/available", response_model=List[RepairRequestResponse])
async def get_available_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение доступных заявок для назначения менеджеру"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры и администраторы могут просматривать доступные заявки"
        )
    
    workflow_service = get_request_workflow_service(db)
    requests = workflow_service.get_available_requests()
    
    return [RepairRequestResponse.from_orm(req) for req in requests]

@router.post("/{request_id}/assign-manager")
async def assign_to_manager(
    request_id: int,
    manager_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Назначение заявки менеджеру"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры и администраторы могут назначать заявки"
        )
    
    workflow_service = get_request_workflow_service(db)
    
    try:
        request = workflow_service.assign_to_manager(request_id, manager_id)
        return {"message": f"Заявка #{request_id} назначена менеджеру", "request": RepairRequestResponse.from_orm(request)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{request_id}/clarify")
async def add_clarification(
    request_id: int,
    clarification_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавление уточнений к заявке"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут добавлять уточнения"
        )
    
    workflow_service = get_request_workflow_service(db)
    
    try:
        request = workflow_service.add_clarification(
            request_id,
            current_user.id,
            clarification_data.get("clarification_details", "")
        )
        return {"message": "Уточнения добавлены", "request": RepairRequestResponse.from_orm(request)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{request_id}/send-to-contractors")
async def send_to_contractors(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправка заявки исполнителям"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут отправлять заявки исполнителям"
        )
    
    workflow_service = get_request_workflow_service(db)
    
    try:
        request = workflow_service.send_to_contractors(request_id, current_user.id)
        return {"message": f"Заявка #{request_id} отправлена исполнителям", "request": RepairRequestResponse.from_orm(request)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{request_id}/assign-contractor")
async def assign_contractor(
    request_id: int,
    contractor_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Назначение исполнителя на заявку"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут назначать исполнителей"
        )
    
    workflow_service = get_request_workflow_service(db)
    
    try:
        request = workflow_service.assign_contractor(
            request_id,
            contractor_data.get("contractor_id"),
            current_user.id
        )
        return {"message": f"Исполнитель назначен на заявку #{request_id}", "request": RepairRequestResponse.from_orm(request)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{request_id}/start-work")
async def start_work(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Начало выполнения работ исполнителем"""
    if current_user.role not in ["contractor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только исполнители могут начинать работы"
        )
    
    workflow_service = get_request_workflow_service(db)
    
    try:
        request = workflow_service.start_work(request_id, current_user.id)
        return {"message": f"Работы по заявке #{request_id} начаты", "request": RepairRequestResponse.from_orm(request)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{request_id}/complete")
async def complete_work(
    request_id: int,
    completion_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Завершение работ исполнителем"""
    if current_user.role not in ["contractor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только исполнители могут завершать работы"
        )
    
    workflow_service = get_request_workflow_service(db)
    
    try:
        request = workflow_service.complete_work(
            request_id,
            current_user.id,
            completion_data.get("final_price")
        )
        return {"message": f"Работы по заявке #{request_id} завершены", "request": RepairRequestResponse.from_orm(request)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{request_id}/cancel")
async def cancel_request(
    request_id: int,
    cancellation_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отмена заявки"""
    workflow_service = get_request_workflow_service(db)
    
    try:
        request = workflow_service.cancel_request(
            request_id,
            current_user.id,
            cancellation_data.get("reason", "")
        )
        return {"message": f"Заявка #{request_id} отменена", "request": RepairRequestResponse.from_orm(request)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{request_id}", response_model=RepairRequestResponse)
async def get_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение конкретной заявки"""
    request = db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    # Проверяем права доступа
    can_view = (
        current_user.role == "admin" or
        (current_user.role == "customer" and request.customer_id == current_user.customer_profile.id) or
        (current_user.role == "manager" and request.manager_id == current_user.id) or
        (current_user.role == "contractor" and request.assigned_contractor_id == current_user.id)
    )
    
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра заявки"
        )
    
    return RepairRequestResponse.from_orm(request)
