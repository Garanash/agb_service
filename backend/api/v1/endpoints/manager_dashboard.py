"""
API endpoints для дашборда менеджера
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from database import get_db
from models import User
from api.v1.dependencies import get_current_user
from api.v1.schemas import UserResponse
from services.manager_dashboard_service import get_manager_dashboard_service, ManagerDashboardService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики для дашборда менеджера"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут просматривать статистику дашборда"
        )
    
    dashboard_service = get_manager_dashboard_service(db)
    stats = dashboard_service.get_dashboard_stats(current_user.id)
    
    return stats

@router.get("/calendar-events")
async def get_calendar_events(
    start_date: str = Query(..., description="Начальная дата в формате ISO"),
    end_date: str = Query(..., description="Конечная дата в формате ISO"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение событий для календаря"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут просматривать календарь"
        )
    
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат даты. Используйте ISO формат"
        )
    
    dashboard_service = get_manager_dashboard_service(db)
    events = dashboard_service.get_calendar_events(current_user.id, start_dt, end_dt)
    
    return events

@router.get("/contractor-workload")
async def get_contractor_workload(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение загрузки исполнителей"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут просматривать загрузку исполнителей"
        )
    
    dashboard_service = get_manager_dashboard_service(db)
    workload = dashboard_service.get_contractor_workload(current_user.id)
    
    return workload

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="Количество записей"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение последней активности"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут просматривать активность"
        )
    
    dashboard_service = get_manager_dashboard_service(db)
    activity = dashboard_service.get_recent_activity(current_user.id, limit)
    
    return activity

@router.get("/upcoming-deadlines")
async def get_upcoming_deadlines(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение предстоящих дедлайнов"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут просматривать дедлайны"
        )
    
    dashboard_service = get_manager_dashboard_service(db)
    deadlines = dashboard_service.get_upcoming_deadlines(current_user.id)
    
    return deadlines

@router.post("/schedule-request")
async def schedule_request(
    request_id: int,
    scheduled_date: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Планирование заявки на определенную дату"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут планировать заявки"
        )
    
    try:
        scheduled_dt = datetime.fromisoformat(scheduled_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат даты. Используйте ISO формат"
        )
    
    # Проверяем, что заявка принадлежит менеджеру
    from models import RepairRequest
    request = db.query(RepairRequest).filter(
        RepairRequest.id == request_id,
        RepairRequest.manager_id == current_user.id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена или не принадлежит менеджеру"
        )
    
    # Обновляем дату планирования
    request.scheduled_date = scheduled_dt
    db.commit()
    
    logger.info(f"✅ Заявка #{request_id} запланирована на {scheduled_date} менеджером {current_user.id}")
    
    return {
        "message": f"Заявка #{request_id} запланирована на {scheduled_date}",
        "request_id": request_id,
        "scheduled_date": scheduled_date
    }

@router.get("/performance-metrics")
async def get_performance_metrics(
    period_days: int = Query(30, ge=7, le=365, description="Период в днях"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение метрик производительности"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут просматривать метрики производительности"
        )
    
    dashboard_service = get_manager_dashboard_service(db)
    
    # Получаем статистику за указанный период
    period_start = datetime.now(timezone.utc) - timedelta(days=period_days)
    
    from models import RepairRequest, RequestStatus
    from sqlalchemy import and_
    
    # Заявки за период
    period_requests = db.query(RepairRequest).filter(
        and_(
            RepairRequest.manager_id == current_user.id,
            RepairRequest.created_at >= period_start
        )
    ).all()
    
    # Метрики
    total_requests = len(period_requests)
    completed_requests = len([r for r in period_requests if r.status == RequestStatus.COMPLETED])
    cancelled_requests = len([r for r in period_requests if r.status == RequestStatus.CANCELLED])
    
    # Среднее время обработки
    completed_with_times = [
        r for r in period_requests 
        if r.status == RequestStatus.COMPLETED and r.processed_at and r.assigned_at
    ]
    
    avg_processing_time = 0
    if completed_with_times:
        total_time = sum([
            (req.assigned_at - req.processed_at).total_seconds() / 3600
            for req in completed_with_times
        ])
        avg_processing_time = total_time / len(completed_with_times)
    
    # Тренды по дням
    daily_stats = {}
    for i in range(period_days):
        day = datetime.now(timezone.utc).date() - timedelta(days=i)
        day_requests = [
            r for r in period_requests 
            if r.created_at.date() == day
        ]
        daily_stats[day.isoformat()] = {
            'total': len(day_requests),
            'completed': len([r for r in day_requests if r.status == RequestStatus.COMPLETED]),
            'cancelled': len([r for r in day_requests if r.status == RequestStatus.CANCELLED])
        }
    
    return {
        'period_days': period_days,
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'cancelled_requests': cancelled_requests,
        'completion_rate': round((completed_requests / total_requests * 100) if total_requests > 0 else 0, 1),
        'cancellation_rate': round((cancelled_requests / total_requests * 100) if total_requests > 0 else 0, 1),
        'avg_processing_time_hours': round(avg_processing_time, 1),
        'daily_stats': daily_stats
    }

@router.get("/users", response_model=List[UserResponse])
async def get_manager_users(
    role_filter: Optional[str] = Query(None, description="Фильтр по роли"),
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу (active/inactive)"),
    search: Optional[str] = Query(None, description="Поиск по имени, email или username"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка пользователей для менеджера"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут просматривать пользователей"
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
