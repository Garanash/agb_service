"""
API endpoints для личного кабинета заказчика
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from database import get_db
from models import User, RepairRequest, CustomerProfile, RequestStatus
from api.v1.schemas import RepairRequestCreate, RepairRequestUpdate, RepairRequestResponse
from api.v1.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/profile", response_model=Dict[str, Any])
async def get_customer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение профиля заказчика"""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только заказчикам"
        )
    
    customer_profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль заказчика не найден"
        )
    
    return {
        "user_info": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "phone": current_user.phone,
            "created_at": current_user.created_at
        },
        "company_info": {
            "company_name": customer_profile.company_name,
            "contact_person": customer_profile.contact_person,
            "phone": customer_profile.phone,
            "email": customer_profile.email,
            "address": customer_profile.address,
            "inn": customer_profile.inn,
            "ogrn": customer_profile.ogrn
        },
        "equipment_info": {
            "equipment_brands": customer_profile.equipment_brands or [],
            "equipment_types": customer_profile.equipment_types or [],
            "mining_operations": customer_profile.mining_operations or [],
            "service_history": customer_profile.service_history
        }
    }

@router.put("/profile")
async def update_customer_profile(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление профиля заказчика"""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только заказчикам"
        )
    
    customer_profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль заказчика не найден"
        )
    
    # Обновляем информацию о пользователе
    if "first_name" in profile_data:
        current_user.first_name = profile_data["first_name"]
    if "last_name" in profile_data:
        current_user.last_name = profile_data["last_name"]
    if "phone" in profile_data:
        current_user.phone = profile_data["phone"]
    
    # Обновляем информацию о компании
    if "company_name" in profile_data:
        customer_profile.company_name = profile_data["company_name"]
    if "contact_person" in profile_data:
        customer_profile.contact_person = profile_data["contact_person"]
    if "address" in profile_data:
        customer_profile.address = profile_data["address"]
    if "inn" in profile_data:
        customer_profile.inn = profile_data["inn"]
    if "ogrn" in profile_data:
        customer_profile.ogrn = profile_data["ogrn"]
    
    # Обновляем информацию об оборудовании
    if "equipment_brands" in profile_data:
        customer_profile.equipment_brands = profile_data["equipment_brands"]
    if "equipment_types" in profile_data:
        customer_profile.equipment_types = profile_data["equipment_types"]
    if "mining_operations" in profile_data:
        customer_profile.mining_operations = profile_data["mining_operations"]
    if "service_history" in profile_data:
        customer_profile.service_history = profile_data["service_history"]
    
    db.commit()
    db.refresh(customer_profile)
    
    return {"message": "Профиль успешно обновлен"}

@router.get("/requests", response_model=List[RepairRequestResponse])
async def get_customer_requests(
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение заявок заказчика"""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только заказчикам"
        )
    
    customer_profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль заказчика не найден"
        )
    
    query = db.query(RepairRequest).filter(
        RepairRequest.customer_id == customer_profile.id
    )
    
    if status_filter:
        query = query.filter(RepairRequest.status == status_filter)
    
    requests = query.order_by(desc(RepairRequest.created_at)).offset(offset).limit(limit).all()
    
    return [RepairRequestResponse.from_orm(req) for req in requests]

@router.post("/requests", response_model=RepairRequestResponse)
async def create_customer_request(
    request_data: RepairRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание новой заявки заказчиком"""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только заказчикам"
        )
    
    customer_profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль заказчика не найден"
        )
    
    # Создаем новую заявку
    new_request = RepairRequest(
        customer_id=customer_profile.id,
        title=request_data.title,
        description=request_data.description,
        urgency=request_data.urgency,
        preferred_date=request_data.preferred_date,
        address=request_data.address,
        city=request_data.city,
        region=request_data.region,
        equipment_type=request_data.equipment_type,
        equipment_brand=request_data.equipment_brand,
        equipment_model=request_data.equipment_model,
        problem_description=request_data.problem_description,
        latitude=request_data.latitude,
        longitude=request_data.longitude,
        priority=request_data.priority or "normal",
        status=RequestStatus.NEW
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    logger.info(f"✅ Новая заявка #{new_request.id} создана заказчиком {current_user.id}")
    
    return RepairRequestResponse.from_orm(new_request)

@router.get("/requests/{request_id}", response_model=RepairRequestResponse)
async def get_customer_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение конкретной заявки заказчика"""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только заказчикам"
        )
    
    customer_profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль заказчика не найден"
        )
    
    request = db.query(RepairRequest).filter(
        and_(
            RepairRequest.id == request_id,
            RepairRequest.customer_id == customer_profile.id
        )
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    return RepairRequestResponse.from_orm(request)

@router.put("/requests/{request_id}")
async def update_customer_request(
    request_id: int,
    request_data: RepairRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление заявки заказчиком (только если статус NEW)"""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только заказчикам"
        )
    
    customer_profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль заказчика не найден"
        )
    
    request = db.query(RepairRequest).filter(
        and_(
            RepairRequest.id == request_id,
            RepairRequest.customer_id == customer_profile.id
        )
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    # Заказчик может обновлять только заявки со статусом NEW
    if request.status != RequestStatus.NEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заявка уже находится в обработке и не может быть изменена"
        )
    
    # Обновляем поля заявки
    if request_data.title is not None:
        request.title = request_data.title
    if request_data.description is not None:
        request.description = request_data.description
    if request_data.urgency is not None:
        request.urgency = request_data.urgency
    if request_data.preferred_date is not None:
        request.preferred_date = request_data.preferred_date
    if request_data.address is not None:
        request.address = request_data.address
    if request_data.city is not None:
        request.city = request_data.city
    if request_data.region is not None:
        request.region = request_data.region
    if request_data.equipment_type is not None:
        request.equipment_type = request_data.equipment_type
    if request_data.equipment_brand is not None:
        request.equipment_brand = request_data.equipment_brand
    if request_data.equipment_model is not None:
        request.equipment_model = request_data.equipment_model
    if request_data.problem_description is not None:
        request.problem_description = request_data.problem_description
    if request_data.priority is not None:
        request.priority = request_data.priority
    
    db.commit()
    db.refresh(request)
    
    logger.info(f"✅ Заявка #{request_id} обновлена заказчиком {current_user.id}")
    
    return RepairRequestResponse.from_orm(request)

@router.delete("/requests/{request_id}")
async def cancel_customer_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отмена заявки заказчиком"""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только заказчикам"
        )
    
    customer_profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль заказчика не найден"
        )
    
    request = db.query(RepairRequest).filter(
        and_(
            RepairRequest.id == request_id,
            RepairRequest.customer_id == customer_profile.id
        )
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    # Заказчик может отменить только заявки со статусом NEW или MANAGER_REVIEW
    if request.status not in [RequestStatus.NEW, RequestStatus.MANAGER_REVIEW]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заявка уже находится в работе и не может быть отменена"
        )
    
    request.status = RequestStatus.CANCELLED
    db.commit()
    
    logger.info(f"✅ Заявка #{request_id} отменена заказчиком {current_user.id}")
    
    return {"message": "Заявка успешно отменена"}

@router.get("/statistics")
async def get_customer_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики заказчика"""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только заказчикам"
        )
    
    customer_profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль заказчика не найден"
        )
    
    # Общее количество заявок
    total_requests = db.query(RepairRequest).filter(
        RepairRequest.customer_id == customer_profile.id
    ).count()
    
    # Заявки по статусам
    status_counts = {}
    for status in RequestStatus:
        count = db.query(RepairRequest).filter(
            and_(
                RepairRequest.customer_id == customer_profile.id,
                RepairRequest.status == status.value
            )
        ).count()
        status_counts[status.value] = count
    
    # Заявки за последние 30 дней
    from datetime import datetime, timedelta, timezone
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_requests = db.query(RepairRequest).filter(
        and_(
            RepairRequest.customer_id == customer_profile.id,
            RepairRequest.created_at >= thirty_days_ago
        )
    ).count()
    
    # Среднее время обработки заявок
    completed_requests = db.query(RepairRequest).filter(
        and_(
            RepairRequest.customer_id == customer_profile.id,
            RepairRequest.status == RequestStatus.COMPLETED,
            RepairRequest.processed_at.isnot(None)
        )
    ).all()
    
    avg_processing_time = 0
    if completed_requests:
        total_time = sum([
            (req.processed_at - req.created_at).total_seconds() / 3600  # в часах
            for req in completed_requests
            if req.processed_at and req.created_at
        ])
        avg_processing_time = total_time / len(completed_requests)
    
    return {
        "total_requests": total_requests,
        "status_counts": status_counts,
        "recent_requests": recent_requests,
        "avg_processing_time_hours": round(avg_processing_time, 1),
        "completion_rate": round(
            (status_counts.get("completed", 0) / total_requests * 100) if total_requests > 0 else 0, 1
        )
    }
