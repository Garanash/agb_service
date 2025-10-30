from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import RepairRequest, CustomerProfile, User, ContractorResponse, ContractorProfile
from ..schemas import (
    RepairRequestCreate, 
    RepairRequestUpdate, 
    RepairRequestResponse,
    ContractorResponseCreate,
    ContractorResponseResponse,
    RequestStatus
)
from ..dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=RepairRequestResponse)
def create_repair_request(
    request_data: RepairRequestCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание новой заявки на ремонт"""
    # Проверяем, что пользователь имеет профиль заказчика
    customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Профиль заказчика не найден. Создайте профиль заказчика."
        )
    
    # Проверка профиля клиента ДО создания заявки (иначе Pydantic 500)
    if not customer_profile.company_name or len(customer_profile.company_name.strip()) < 1:
        raise HTTPException(
            status_code=400,
            detail="В профиле заказчика не указано название компании. Перейдите в профиль и заполните поле 'Название организации' полностью."
        )
    if not customer_profile.phone or len(customer_profile.phone) < 10:
        raise HTTPException(
            status_code=400,
            detail="В профиле заказчика не указан корректный номер телефона. Перейдите в профиль и заполните телефон полностью."
        )
    
    # Создаем заявку
    db_request = RepairRequest(
        customer_id=customer_profile.id,
        title=request_data.title,
        description=request_data.description,
        urgency=request_data.urgency,
        preferred_date=request_data.preferred_date,
        address=request_data.address,
        city=request_data.city,
        region=request_data.region,
        status=RequestStatus.NEW
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Уведомляем менеджеров по email (best-effort, фоновая задача)
    def send_manager_notifications():
        try:
            from database import SessionLocal
            from models import User
            from services.email_service import email_service
            import asyncio
            
            # Создаем новую сессию для фоновой задачи
            db_bg = SessionLocal()
            try:
                managers = db_bg.query(User).filter(User.role == "manager").all()
                subject = f"Новая заявка #{db_request.id}: {db_request.title}"
                location_text = ", ".join(filter(None, [db_request.region, db_request.city, db_request.address]))
                message = (
                    f"Создана новая заявка #{db_request.id}.\n"
                    f"Название: {db_request.title}\n"
                    f"Срочность: {db_request.urgency or 'не указана'}\n"
                    f"Локация: {location_text or 'не указана'}\n"
                    f"Описание: {db_request.description}"
                )
                for m in managers:
                    if m.email:
                        try:
                            # Запускаем асинхронную функцию в новом event loop
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(email_service.send_notification_email(m.email, subject, message))
                            loop.close()
                        except Exception:
                            pass
            finally:
                db_bg.close()
        except Exception:
            pass
    
    background_tasks.add_task(send_manager_notifications)

    # Безопасная сериализация без вложенного customer
    resp = {
        "id": db_request.id,
        "customer_id": db_request.customer_id,
        "title": getattr(db_request, "title", ""),
        "description": getattr(db_request, "description", ""),
        "urgency": getattr(db_request, "urgency", None),
        "preferred_date": getattr(db_request, "preferred_date", None),
        "address": getattr(db_request, "address", None),
        "city": getattr(db_request, "city", None),
        "region": getattr(db_request, "region", None),
        "equipment_type": getattr(db_request, "equipment_type", None),
        "equipment_brand": getattr(db_request, "equipment_brand", None),
        "equipment_model": getattr(db_request, "equipment_model", None),
        "problem_description": getattr(db_request, "problem_description", None),
        "latitude": getattr(db_request, "latitude", None),
        "longitude": getattr(db_request, "longitude", None),
        "estimated_cost": getattr(db_request, "estimated_cost", None),
        "manager_comment": getattr(db_request, "manager_comment", None),
        "final_price": getattr(db_request, "final_price", None),
        "sent_to_bot_at": getattr(db_request, "sent_to_bot_at", None),
        "status": getattr(db_request, "status", "new"),
        "service_engineer_id": getattr(db_request, "service_engineer_id", None),
        "assigned_contractor_id": getattr(db_request, "assigned_contractor_id", None),
        "created_at": getattr(db_request, "created_at", None),
        "updated_at": getattr(db_request, "updated_at", None),
        "processed_at": getattr(db_request, "processed_at", None),
        "assigned_at": getattr(db_request, "assigned_at", None),
    }
    return RepairRequestResponse(**resp)

@router.get("/", response_model=List[RepairRequestResponse])
def get_repair_requests(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Получение списка заявок на ремонт"""
    try:
        # Базовый запрос
        query = db.query(RepairRequest)
        
        # Фильтрация по роли пользователя
        if current_user.role == "customer":
            # Заказчик видит только свои заявки
            customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
            if customer_profile:
                query = query.filter(RepairRequest.customer_id == customer_profile.id)
        elif current_user.role == "contractor":
            # Исполнитель видит заявки, на которые он откликнулся или которые ему назначены
            contractor_profile = db.query(ContractorProfile).filter(ContractorProfile.user_id == current_user.id).first()
            if contractor_profile:
                query = query.filter(
                    (RepairRequest.assigned_contractor_id == contractor_profile.id) |
                    (RepairRequest.id.in_(
                        db.query(ContractorResponse.request_id).filter(
                            ContractorResponse.contractor_id == contractor_profile.id
                        )
                    ))
                )
        elif current_user.role == "service_engineer":
            # Сервисный инженер видит все заявки
            pass
        elif current_user.role == "admin":
            # Администратор видит все заявки
            pass
        
        # Фильтрация по статусу
        if status_filter:
            query = query.filter(RepairRequest.status == status_filter)
        
        # Сортировка и пагинация
        requests = query.order_by(RepairRequest.created_at.desc()).offset(skip).limit(limit).all()
        
        # Безопасная сериализация без вложенного customer (избегаем ValidationError на неполных профилях)
        safe_responses = []
        for req in requests:
            resp = {
                "id": req.id,
                "customer_id": req.customer_id,
                "title": getattr(req, "title", ""),
                "description": getattr(req, "description", ""),
                "urgency": getattr(req, "urgency", None),
                "preferred_date": getattr(req, "preferred_date", None),
                "address": getattr(req, "address", None),
                "city": getattr(req, "city", None),
                "region": getattr(req, "region", None),
                "equipment_type": getattr(req, "equipment_type", None),
                "equipment_brand": getattr(req, "equipment_brand", None),
                "equipment_model": getattr(req, "equipment_model", None),
                "problem_description": getattr(req, "problem_description", None),
                "latitude": getattr(req, "latitude", None),
                "longitude": getattr(req, "longitude", None),
                "estimated_cost": getattr(req, "estimated_cost", None),
                "manager_comment": getattr(req, "manager_comment", None),
                "final_price": getattr(req, "final_price", None),
                "sent_to_bot_at": getattr(req, "sent_to_bot_at", None),
                "status": getattr(req, "status", "new"),
                "service_engineer_id": getattr(req, "service_engineer_id", None),
                "assigned_contractor_id": getattr(req, "assigned_contractor_id", None),
                "created_at": getattr(req, "created_at", None),
                "updated_at": getattr(req, "updated_at", None),
                "processed_at": getattr(req, "processed_at", None),
                "assigned_at": getattr(req, "assigned_at", None),
            }
            safe_responses.append(RepairRequestResponse(**resp))
        return safe_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении заявок: {str(e)}"
        )

@router.get("/{request_id}", response_model=RepairRequestResponse)
def get_repair_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение конкретной заявки на ремонт"""
    request = db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    # Проверяем права доступа
    if current_user.role == "customer":
        customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
        if not customer_profile or request.customer_id != customer_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этой заявке"
            )
    elif current_user.role == "contractor":
        contractor_profile = db.query(ContractorProfile).filter(ContractorProfile.user_id == current_user.id).first()
        if not contractor_profile or (request.assigned_contractor_id != contractor_profile.id and 
                                     not db.query(ContractorResponse).filter(
                                         ContractorResponse.request_id == request_id,
                                         ContractorResponse.contractor_id == contractor_profile.id
                                     ).first()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этой заявке"
            )
    
    return RepairRequestResponse.from_orm(request)

@router.put("/{request_id}", response_model=RepairRequestResponse)
def update_repair_request(
    request_id: int,
    request_data: RepairRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление заявки на ремонт"""
    request = db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    # Проверяем права доступа
    if current_user.role == "customer":
        customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
        if not customer_profile or request.customer_id != customer_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этой заявке"
            )
    elif current_user.role not in ["admin", "manager", "service_engineer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления заявки"
        )
    
    # Обновляем поля
    for field, value in request_data.dict(exclude_unset=True).items():
        setattr(request, field, value)
    
    request.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(request)
    
    return RepairRequestResponse.from_orm(request)

@router.delete("/{request_id}")
def delete_repair_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление заявки на ремонт"""
    request = db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    # Проверяем права доступа
    if current_user.role == "customer":
        customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
        if not customer_profile or request.customer_id != customer_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этой заявке"
            )
    elif current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления заявки"
        )
    
    db.delete(request)
    db.commit()
    
    return {"message": "Заявка успешно удалена"}

@router.post("/{request_id}/responses", response_model=ContractorResponseResponse)
def create_contractor_response(
    request_id: int,
    response_data: ContractorResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание отклика исполнителя на заявку"""
    # Проверяем, что пользователь имеет профиль исполнителя
    contractor_profile = db.query(ContractorProfile).filter(ContractorProfile.user_id == current_user.id).first()
    
    if not contractor_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Профиль исполнителя не найден"
        )
    
    # Проверяем, что заявка существует
    request = db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    # Проверяем, что исполнитель еще не откликался на эту заявку
    existing_response = db.query(ContractorResponse).filter(
        ContractorResponse.request_id == request_id,
        ContractorResponse.contractor_id == contractor_profile.id
    ).first()
    
    if existing_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже откликались на эту заявку"
        )
    
    # Создаем отклик
    db_response = ContractorResponse(
        request_id=request_id,
        contractor_id=contractor_profile.id,
        proposed_price=response_data.proposed_price,
        estimated_time=response_data.estimated_time,
        comment=response_data.comment
    )
    
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    
    return ContractorResponseResponse.from_orm(db_response)

@router.get("/{request_id}/responses", response_model=List[ContractorResponseResponse])
def get_contractor_responses(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение откликов исполнителей на заявку"""
    # Проверяем, что заявка существует
    request = db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    # Проверяем права доступа
    if current_user.role == "customer":
        customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
        if not customer_profile or request.customer_id != customer_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этой заявке"
            )
    elif current_user.role not in ["admin", "manager", "service_engineer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра откликов"
        )
    
    responses = db.query(ContractorResponse).filter(ContractorResponse.request_id == request_id).all()
    
    return [ContractorResponseResponse.from_orm(response) for response in responses]
