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
    
    return RepairRequestResponse.from_orm(db_request)

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
        
        return [RepairRequestResponse.from_orm(req) for req in requests]
        
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
        estimated_duration=response_data.estimated_duration,
        message=response_data.message,
        status="pending"
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
