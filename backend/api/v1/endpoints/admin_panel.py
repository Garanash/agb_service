"""
API endpoints для расширенной админ панели
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from datetime import datetime, timezone, timedelta

from database import get_db
from models import User, CustomerProfile, ContractorProfile, RepairRequest, SecurityVerification, HRDocument, RequestStatus, UserRole
from api.v1.schemas import RepairRequestResponse, UserResponse
from api.v1.dependencies import get_current_user
from services.file_email_service import file_email_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение данных для админ дашборда"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    # Общая статистика пользователей
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    verified_users = db.query(User).filter(User.email_verified == True).count()
    
    # Статистика по ролям
    users_by_role = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    role_stats = {role: count for role, count in users_by_role}
    
    # Общая статистика заявок
    total_requests = db.query(RepairRequest).count()
    requests_by_status = db.query(RepairRequest.status, func.count(RepairRequest.id)).group_by(RepairRequest.status).all()
    status_stats = {status: count for status, count in requests_by_status}
    
    # Статистика за последние 30 дней
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_users = db.query(User).filter(User.created_at >= thirty_days_ago).count()
    recent_requests = db.query(RepairRequest).filter(RepairRequest.created_at >= thirty_days_ago).count()
    
    # Статистика проверок безопасности
    total_verifications = db.query(SecurityVerification).count()
    pending_verifications = db.query(SecurityVerification).filter(
        SecurityVerification.verification_status == "pending"
    ).count()
    approved_verifications = db.query(SecurityVerification).filter(
        SecurityVerification.verification_status == "approved"
    ).count()
    
    # Статистика HR документов
    total_documents = db.query(HRDocument).count()
    pending_documents = db.query(HRDocument).filter(
        HRDocument.document_status == "pending"
    ).count()
    completed_documents = db.query(HRDocument).filter(
        HRDocument.document_status == "completed"
    ).count()
    
    # Топ исполнители по количеству заявок
    top_contractors = db.query(
        ContractorProfile.id,
        ContractorProfile.first_name,
        ContractorProfile.last_name,
        func.count(RepairRequest.id).label('request_count')
    ).join(RepairRequest, RepairRequest.assigned_contractor_id == ContractorProfile.id).group_by(
        ContractorProfile.id
    ).order_by(desc('request_count')).limit(5).all()
    
    # Топ заказчики по количеству заявок
    top_customers = db.query(
        CustomerProfile.id,
        CustomerProfile.company_name,
        func.count(RepairRequest.id).label('request_count')
    ).join(RepairRequest, RepairRequest.customer_id == CustomerProfile.id).group_by(
        CustomerProfile.id
    ).order_by(desc('request_count')).limit(5).all()
    
    return {
        "user_stats": {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "recent_users": recent_users,
            "users_by_role": role_stats
        },
        "request_stats": {
            "total_requests": total_requests,
            "recent_requests": recent_requests,
            "requests_by_status": status_stats
        },
        "verification_stats": {
            "total_verifications": total_verifications,
            "pending_verifications": pending_verifications,
            "approved_verifications": approved_verifications
        },
        "document_stats": {
            "total_documents": total_documents,
            "pending_documents": pending_documents,
            "completed_documents": completed_documents
        },
        "top_contractors": [
            {
                "id": contractor.id,
                "name": f"{contractor.first_name} {contractor.last_name}",
                "request_count": contractor.request_count
            }
            for contractor in top_contractors
        ],
        "top_customers": [
            {
                "id": customer.id,
                "company_name": customer.company_name,
                "request_count": customer.request_count
            }
            for customer in top_customers
        ]
    }

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    role_filter: Optional[str] = Query(None, description="Фильтр по роли"),
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу (active/inactive)"),
    search: Optional[str] = Query(None, description="Поиск по имени, email или username"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка всех пользователей с фильтрацией"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    query = db.query(User)
    
    # Фильтр по роли
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    # Фильтр по статусу
    if status_filter == "active":
        query = query.filter(User.is_active == True)
    elif status_filter == "inactive":
        query = query.filter(User.is_active == False)
    
    # Поиск
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    users = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()
    
    return [UserResponse.from_orm(user) for user in users]

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_details(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение детальной информации о пользователе"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return UserResponse.from_orm(user)

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание нового пользователя администратором"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    try:
        # Проверяем, что обязательные поля заполнены
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if not user_data.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Поле '{field}' обязательно для заполнения"
                )
        
        # Проверяем уникальность username и email
        existing_user = db.query(User).filter(
            or_(User.username == user_data['username'], User.email == user_data['email'])
        ).first()
        
        if existing_user:
            if existing_user.username == user_data['username']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким именем уже существует"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже существует"
                )
        
        # Проверяем валидность роли
        valid_roles = [role.value for role in UserRole]
        if user_data['role'] not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недопустимая роль. Доступные роли: {', '.join(valid_roles)}"
            )
        
        # Хешируем пароль
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=['sha256_crypt'], deprecated='auto')
        hashed_password = pwd_context.hash(user_data['password'])
        
        # Создаем пользователя
        new_user = User(
            username=user_data['username'],
            email=user_data['email'],
            hashed_password=hashed_password,
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            middle_name=user_data.get('middle_name', ''),
            phone=user_data.get('phone', ''),
            role=user_data['role'],
            is_active=user_data.get('is_active', True),
            email_verified=user_data.get('email_verified', False),
            is_password_changed=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"✅ Администратор {current_user.id} создал пользователя {new_user.username} с ролью {new_user.role}")
        
        return UserResponse.from_orm(new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Ошибка создания пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания пользователя: {str(e)}"
        )

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление статуса пользователя"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Обновляем статус активности
    if "is_active" in status_data:
        user.is_active = status_data["is_active"]
    
    # Обновляем статус верификации email
    if "email_verified" in status_data:
        user.email_verified = status_data["email_verified"]
    
    # Обновляем роль
    if "role" in status_data:
        if status_data["role"] not in [role.value for role in UserRole]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недопустимая роль"
            )
        user.role = status_data["role"]
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"✅ Статус пользователя {user_id} обновлен администратором {current_user.id}")
    
    return {"message": "Статус пользователя успешно обновлен"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление пользователя"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    # Нельзя удалить самого себя
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить самого себя"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Проверяем, есть ли связанные данные
    if user.role == "customer":
        customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == user_id).first()
        if customer_profile:
            requests_count = db.query(RepairRequest).filter(RepairRequest.customer_id == customer_profile.id).count()
            if requests_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Нельзя удалить пользователя с {requests_count} заявками"
                )
    
    elif user.role == "contractor":
        contractor_profile = db.query(ContractorProfile).filter(ContractorProfile.user_id == user_id).first()
        if contractor_profile:
            assigned_requests = db.query(RepairRequest).filter(RepairRequest.assigned_contractor_id == user_id).count()
            if assigned_requests > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Нельзя удалить исполнителя с {assigned_requests} назначенными заявками"
                )
    
    # Удаляем связанные профили
    if user.role == "customer":
        db.query(CustomerProfile).filter(CustomerProfile.user_id == user_id).delete()
    elif user.role == "contractor":
        db.query(ContractorProfile).filter(ContractorProfile.user_id == user_id).delete()
        db.query(SecurityVerification).filter(SecurityVerification.contractor_id == user_id).delete()
        db.query(HRDocument).filter(HRDocument.contractor_id == user_id).delete()
    
    # Удаляем пользователя
    db.delete(user)
    db.commit()
    
    logger.info(f"✅ Пользователь {user_id} удален администратором {current_user.id}")
    
    return {"message": "Пользователь успешно удален"}

@router.put("/contractors/{user_id}/profile")
async def update_contractor_profile_by_admin(
    user_id: int,
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление профиля исполнителя администратором"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    # Проверяем, что пользователь существует и является исполнителем
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    if user.role != "contractor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не является исполнителем"
        )
    
    # Получаем профиль исполнителя
    contractor_profile = db.query(ContractorProfile).filter(
        ContractorProfile.user_id == user_id
    ).first()
    
    if not contractor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль исполнителя не найден"
        )
    
    # Обновляем поля профиля
    for field, value in profile_data.items():
        if hasattr(contractor_profile, field) and value is not None:
            setattr(contractor_profile, field, value)
    
    contractor_profile.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(contractor_profile)
    
    logger.info(f"✅ Профиль исполнителя {user_id} обновлен администратором {current_user.id}")
    
    return {"message": "Профиль исполнителя успешно обновлен"}

@router.get("/requests", response_model=List[RepairRequestResponse])
async def get_all_requests(
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу"),
    priority_filter: Optional[str] = Query(None, description="Фильтр по приоритету"),
    urgency_filter: Optional[str] = Query(None, description="Фильтр по срочности"),
    search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка всех заявок с фильтрацией"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    query = db.query(RepairRequest)
    
    # Фильтр по статусу
    if status_filter:
        query = query.filter(RepairRequest.status == status_filter)
    
    # Фильтр по приоритету
    if priority_filter:
        query = query.filter(RepairRequest.priority == priority_filter)
    
    # Фильтр по срочности
    if urgency_filter:
        query = query.filter(RepairRequest.urgency == urgency_filter)
    
    # Поиск
    if search:
        search_filter = or_(
            RepairRequest.title.ilike(f"%{search}%"),
            RepairRequest.description.ilike(f"%{search}%"),
            RepairRequest.problem_description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    requests = query.order_by(desc(RepairRequest.created_at)).offset(offset).limit(limit).all()
    
    return [RepairRequestResponse.from_orm(req) for req in requests]

@router.get("/requests/{request_id}", response_model=RepairRequestResponse)
async def get_request_details(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение детальной информации о заявке"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    request = db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    return RepairRequestResponse.from_orm(request)

@router.put("/requests/{request_id}/status")
async def update_request_status(
    request_id: int,
    status_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление статуса заявки администратором"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    request = db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    # Обновляем статус
    if "status" in status_data:
        if status_data["status"] not in [status.value for status in RequestStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недопустимый статус"
            )
        request.status = status_data["status"]
        
        # Устанавливаем время обработки для завершенных заявок
        if status_data["status"] == RequestStatus.COMPLETED:
            request.processed_at = datetime.now(timezone.utc)
    
    # Обновляем приоритет
    if "priority" in status_data:
        request.priority = status_data["priority"]
    
    # Обновляем срочность
    if "urgency" in status_data:
        request.urgency = status_data["urgency"]
    
    db.commit()
    db.refresh(request)
    
    logger.info(f"✅ Статус заявки {request_id} обновлен администратором {current_user.id}")
    
    return {"message": "Статус заявки успешно обновлен"}

@router.get("/statistics")
async def get_admin_statistics(
    period: str = Query("30d", description="Период для статистики (7d, 30d, 90d, 1y)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение детальной статистики для админа"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    # Определяем период
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = days_map.get(period, 30)
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Статистика пользователей по дням
    users_by_day = db.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= start_date).group_by(
        func.date(User.created_at)
    ).order_by('date').all()
    
    # Статистика заявок по дням
    requests_by_day = db.query(
        func.date(RepairRequest.created_at).label('date'),
        func.count(RepairRequest.id).label('count')
    ).filter(RepairRequest.created_at >= start_date).group_by(
        func.date(RepairRequest.created_at)
    ).order_by('date').all()
    
    # Статистика по типам оборудования
    equipment_stats = db.query(
        RepairRequest.equipment_type,
        func.count(RepairRequest.id).label('count')
    ).filter(RepairRequest.created_at >= start_date).group_by(
        RepairRequest.equipment_type
    ).all()
    
    # Статистика по регионам
    region_stats = db.query(
        RepairRequest.region,
        func.count(RepairRequest.id).label('count')
    ).filter(RepairRequest.created_at >= start_date).group_by(
        RepairRequest.region
    ).all()
    
    # Среднее время обработки заявок
    completed_requests = db.query(RepairRequest).filter(
        and_(
            RepairRequest.status == RequestStatus.COMPLETED,
            RepairRequest.processed_at.isnot(None),
            RepairRequest.created_at >= start_date
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
        "period": period,
        "users_by_day": [{"date": str(day.date), "count": day.count} for day in users_by_day],
        "requests_by_day": [{"date": str(day.date), "count": day.count} for day in requests_by_day],
        "equipment_stats": [{"type": stat.equipment_type, "count": stat.count} for stat in equipment_stats],
        "region_stats": [{"region": stat.region, "count": stat.count} for stat in region_stats],
        "avg_processing_time_hours": round(avg_processing_time, 1),
        "total_completed_requests": len(completed_requests)
    }

@router.get("/emails")
async def get_emails(
    current_user: User = Depends(get_current_user)
):
    """Получить список отправленных писем"""
    try:
        # Проверяем права доступа
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра писем"
            )
        
        emails = file_email_service.get_emails()
        logger.info(f"Получено {len(emails)} писем")
        return {"emails": emails}
        
    except Exception as e:
        logger.error(f"Ошибка получения писем: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения списка писем"
        )
