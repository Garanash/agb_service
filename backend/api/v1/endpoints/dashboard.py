"""
API endpoints для главной страницы (дашборда)
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from models import User, CustomerProfile, ContractorProfile, RepairRequest, RequestStatus
from api.v1.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/analytics", response_model=Dict[str, Any])
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение аналитики для главной страницы"""
    
    # Общая статистика заявок
    total_requests = db.query(RepairRequest).count()
    
    # Статистика по статусам заявок
    requests_by_status = db.query(
        RepairRequest.status, 
        func.count(RepairRequest.id)
    ).group_by(RepairRequest.status).all()
    status_stats = {status: count for status, count in requests_by_status}
    
    # Активные заявки (в работе или ожидающие обработки)
    active_statuses = [
        RequestStatus.MANAGER_REVIEW,
        RequestStatus.CLARIFICATION,
        RequestStatus.SENT_TO_CONTRACTORS,
        RequestStatus.CONTRACTOR_RESPONSES,
        RequestStatus.ASSIGNED,
        RequestStatus.IN_PROGRESS
    ]
    active_requests = db.query(RepairRequest).filter(
        RepairRequest.status.in_(active_statuses)
    ).count()
    
    # Статистика пользователей
    total_contractors = db.query(ContractorProfile).count()
    total_customers = db.query(CustomerProfile).count()
    
    # Статистика за последние 7 дней
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_requests = db.query(RepairRequest).filter(
        RepairRequest.created_at >= seven_days_ago
    ).count()
    
    # Статистика за последние 30 дней
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    monthly_requests = db.query(RepairRequest).filter(
        RepairRequest.created_at >= thirty_days_ago
    ).count()
    
    # Топ исполнители по количеству выполненных заявок
    top_contractors = db.query(
        ContractorProfile.id,
        ContractorProfile.first_name,
        ContractorProfile.last_name,
        func.count(RepairRequest.id).label('completed_count')
    ).join(RepairRequest, RepairRequest.assigned_contractor_id == ContractorProfile.id).filter(
        RepairRequest.status == RequestStatus.COMPLETED
    ).group_by(ContractorProfile.id).order_by(
        desc('completed_count')
    ).limit(5).all()
    
    # Топ заказчики по количеству заявок
    top_customers = db.query(
        CustomerProfile.id,
        CustomerProfile.company_name,
        func.count(RepairRequest.id).label('request_count')
    ).join(RepairRequest, RepairRequest.customer_id == CustomerProfile.id).group_by(
        CustomerProfile.id
    ).order_by(desc('request_count')).limit(5).all()
    
    # Статистика по типам оборудования
    equipment_stats = db.query(
        RepairRequest.equipment_type,
        func.count(RepairRequest.id).label('count')
    ).filter(RepairRequest.equipment_type.isnot(None)).group_by(
        RepairRequest.equipment_type
    ).order_by(desc('count')).limit(10).all()
    
    # Статистика по регионам
    region_stats = db.query(
        RepairRequest.region,
        func.count(RepairRequest.id).label('count')
    ).filter(RepairRequest.region.isnot(None)).group_by(
        RepairRequest.region
    ).order_by(desc('count')).limit(10).all()
    
    return {
        "overview": {
            "total_requests": total_requests,
            "active_requests": active_requests,
            "total_contractors": total_contractors,
            "total_customers": total_customers,
            "recent_requests_7d": recent_requests,
            "recent_requests_30d": monthly_requests
        },
        "requests_by_status": status_stats,
        "top_contractors": [
            {
                "id": contractor.id,
                "name": f"{contractor.first_name} {contractor.last_name}",
                "completed_count": contractor.completed_count
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
        ],
        "equipment_stats": [
            {
                "equipment_type": stat.equipment_type,
                "count": stat.count
            }
            for stat in equipment_stats
        ],
        "region_stats": [
            {
                "region": stat.region,
                "count": stat.count
            }
            for stat in region_stats
        ],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
