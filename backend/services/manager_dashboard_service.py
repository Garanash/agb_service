"""
Сервис для дашборда менеджера
Предоставляет статистику, метрики и данные для календаря
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from models import RepairRequest, User, RequestStatus, ContractorProfile, CustomerProfile

logger = logging.getLogger(__name__)

class ManagerDashboardService:
    """Сервис для дашборда менеджера"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self, manager_id: int) -> Dict[str, Any]:
        """Получение общей статистики для дашборда"""
        
        # Статистика по статусам заявок
        status_stats = self.db.query(
            RepairRequest.status,
            func.count(RepairRequest.id).label('count')
        ).filter(
            RepairRequest.manager_id == manager_id
        ).group_by(RepairRequest.status).all()
        
        status_counts = {status: count for status, count in status_stats}
        
        # Общее количество заявок
        total_requests = sum(status_counts.values()) if status_counts else 0
        
        # Заявки за последние 30 дней
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_requests = self.db.query(RepairRequest).filter(
            and_(
                RepairRequest.manager_id == manager_id,
                RepairRequest.created_at >= thirty_days_ago
            )
        ).count()
        
        # Заявки за сегодня
        today = datetime.now(timezone.utc).date()
        today_requests = self.db.query(RepairRequest).filter(
            and_(
                RepairRequest.manager_id == manager_id,
                func.date(RepairRequest.created_at) == today
            )
        ).count()
        
        # Среднее время обработки заявок
        completed_requests = self.db.query(RepairRequest).filter(
            and_(
                RepairRequest.manager_id == manager_id,
                RepairRequest.status == "completed",
                RepairRequest.processed_at.isnot(None),
                RepairRequest.assigned_at.isnot(None)
            )
        ).all()
        
        avg_processing_time = 0
        if completed_requests:
            total_time = sum([
                (req.assigned_at - req.processed_at).total_seconds() / 3600  # в часах
                for req in completed_requests
                if req.processed_at and req.assigned_at
            ])
            avg_processing_time = total_time / len(completed_requests)
        
        # Активные исполнители
        active_contractors = self.db.query(ContractorProfile).join(User, ContractorProfile.user_id == User.id).filter(
            and_(
                User.role == 'contractor',
                User.is_active == True,
                ContractorProfile.availability_status == 'available'
            )
        ).count()
        
        # Заказчики с активными заявками
        active_customers = self.db.query(CustomerProfile.id).join(
            RepairRequest, CustomerProfile.id == RepairRequest.customer_id
        ).filter(
            and_(
                RepairRequest.manager_id == manager_id,
                RepairRequest.status.in_([
                    "manager_review",
                    "clarification",
                    "sent_to_contractors",
                    "contractor_responses",
                    "assigned",
                    "in_progress"
                ])
            )
        ).distinct().count()
        
        return {
            'total_requests': total_requests,
            'recent_requests': recent_requests,
            'today_requests': today_requests,
            'status_counts': status_counts,
            'avg_processing_time_hours': round(avg_processing_time, 1),
            'active_contractors': active_contractors,
            'active_customers': active_customers,
            'completion_rate': round(
                (status_counts.get("completed", 0) / total_requests * 100) 
                if total_requests > 0 else 0, 1
            )
        }
    
    def get_calendar_events(self, manager_id: int, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Получение событий для календаря"""
        
        events = []
        
        # Заявки с запланированными датами
        scheduled_requests = self.db.query(RepairRequest).filter(
            and_(
                RepairRequest.manager_id == manager_id,
                RepairRequest.scheduled_date.isnot(None),
                RepairRequest.scheduled_date.between(start_date, end_date),
                RepairRequest.status.in_([
                    "assigned",
                    "in_progress"
                ])
            )
        ).all()
        
        for request in scheduled_requests:
            try:
                contractor_name = 'Не назначен'
                if request.assigned_contractor_id:
                    contractor = self.db.query(ContractorProfile).filter(
                        ContractorProfile.id == request.assigned_contractor_id
                    ).first()
                    if contractor:
                        contractor_name = f"{contractor.first_name or ''} {contractor.last_name or ''}".strip() or 'Не назначен'
                
                customer_name = 'Неизвестно'
                if request.customer_id:
                    customer = self.db.query(CustomerProfile).filter(
                        CustomerProfile.id == request.customer_id
                    ).first()
                    if customer:
                        customer_name = customer.company_name or customer.contact_name or 'Неизвестно'
                
                events.append({
                    'id': f"request_{request.id}",
                    'title': request.title or 'Без названия',
                    'start': request.scheduled_date.isoformat() if request.scheduled_date else start_date.isoformat(),
                    'end': (request.scheduled_date + timedelta(hours=8)).isoformat() if request.scheduled_date else (start_date + timedelta(hours=8)).isoformat(),
                    'type': 'request',
                    'status': request.status or 'unknown',
                    'contractor_name': contractor_name,
                    'customer_name': customer_name,
                    'equipment_type': request.equipment_type or 'Не указано',
                    'address': request.address or 'Не указано',
                    'color': self._get_status_color(request.status) if request.status else '#666666'
                })
            except Exception as e:
                logger.error(f"Ошибка обработки заявки {request.id} для календаря: {e}")
                continue
        
        # Заявки с предпочтительными датами
        preferred_requests = self.db.query(RepairRequest).filter(
            and_(
                RepairRequest.manager_id == manager_id,
                RepairRequest.preferred_date.isnot(None),
                RepairRequest.preferred_date.between(start_date, end_date),
                RepairRequest.status.in_([
                    "manager_review",
                    "clarification",
                    "sent_to_contractors"
                ])
            )
        ).all()
        
        for request in preferred_requests:
            try:
                customer_name = 'Неизвестно'
                if request.customer_id:
                    customer = self.db.query(CustomerProfile).filter(
                        CustomerProfile.id == request.customer_id
                    ).first()
                    if customer:
                        customer_name = customer.company_name or customer.contact_name or 'Неизвестно'
                
                events.append({
                    'id': f"preferred_{request.id}",
                    'title': f"📅 {request.title or 'Без названия'}",
                    'start': request.preferred_date.isoformat() if request.preferred_date else start_date.isoformat(),
                    'end': (request.preferred_date + timedelta(hours=1)).isoformat() if request.preferred_date else (start_date + timedelta(hours=1)).isoformat(),
                    'type': 'preferred',
                    'status': request.status or 'unknown',
                    'customer_name': customer_name,
                'equipment_type': request.equipment_type,
                'address': request.address,
                'color': '#ff9800'  # Оранжевый для предпочтительных дат
            })
        
        return events
    
    def get_contractor_workload(self, manager_id: int) -> List[Dict[str, Any]]:
        """Получение загрузки исполнителей"""
        
        try:
            contractors = self.db.query(ContractorProfile).join(User, ContractorProfile.user_id == User.id).filter(
                and_(
                    User.role == 'contractor',
                    User.is_active == True
                )
            ).all()
            
            workload_data = []
            
            for contractor in contractors:
                # Активные заявки исполнителя
                active_requests = self.db.query(RepairRequest).filter(
                    and_(
                        RepairRequest.assigned_contractor_id == contractor.user_id,
                        RepairRequest.status.in_([
                            "assigned",
                            "in_progress"
                        ])
                    )
                ).count()
                
                # Завершенные заявки за месяц
                month_ago = datetime.now(timezone.utc) - timedelta(days=30)
                completed_requests = self.db.query(RepairRequest).filter(
                    and_(
                        RepairRequest.assigned_contractor_id == contractor.user_id,
                        RepairRequest.status == "completed",
                        RepairRequest.assigned_at >= month_ago
                    )
                ).count()
                
                # Средняя оценка (пока заглушка)
                avg_rating = 4.5
                
                workload_data.append({
                    'contractor_id': contractor.user_id,
                    'name': f"{contractor.first_name} {contractor.last_name}",
                    'specializations': contractor.specializations or [],
                    'active_requests': active_requests,
                    'completed_requests': completed_requests,
                    'avg_rating': avg_rating,
                    'availability_status': contractor.availability_status,
                    'hourly_rate': contractor.hourly_rate,
                    'workload_percentage': min(active_requests * 20, 100)  # Простая формула загрузки
                })
            
            return sorted(workload_data, key=lambda x: x['workload_percentage'], reverse=True)
            
        except Exception as e:
            logger.error(f"Ошибка получения загрузки исполнителей: {e}")
            return []
    
    def get_recent_activity(self, manager_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение последней активности"""
        
        try:
            # Последние изменения в заявках
            recent_requests = self.db.query(RepairRequest).filter(
                RepairRequest.manager_id == manager_id
            ).order_by(RepairRequest.updated_at.desc()).limit(limit).all()
            
            activities = []
            
            for request in recent_requests:
                activity_type = self._get_activity_type(request)
                activities.append({
                    'id': request.id,
                    'type': activity_type,
                    'title': request.title,
                    'status': request.status,
                    'status_text': self._get_status_text(request.status),
                    'timestamp': request.updated_at.isoformat(),
                    'customer_name': request.customer.company_name if request.customer else 'Неизвестно',
                    'contractor_name': f"{request.assigned_contractor.first_name} {request.assigned_contractor.last_name}" 
                                     if request.assigned_contractor else None,
                    'icon': self._get_activity_icon(activity_type)
                })
            
            return activities
            
        except Exception as e:
            logger.error(f"Ошибка получения последней активности: {e}")
            return []
    
    def get_upcoming_deadlines(self, manager_id: int) -> List[Dict[str, Any]]:
        """Получение предстоящих дедлайнов"""
        
        try:
            # Заявки с предпочтительными датами в ближайшие 7 дней
            seven_days_later = datetime.now(timezone.utc) + timedelta(days=7)
            
            upcoming_requests = self.db.query(RepairRequest).filter(
                and_(
                    RepairRequest.manager_id == manager_id,
                    RepairRequest.preferred_date <= seven_days_later,
                    RepairRequest.preferred_date >= datetime.now(timezone.utc),
                    RepairRequest.status.in_([
                        "manager_review",
                        "clarification",
                        "sent_to_contractors"
                    ])
                )
            ).order_by(RepairRequest.preferred_date).all()
            
            deadlines = []
            
            for request in upcoming_requests:
                days_until = (request.preferred_date.date() - datetime.now(timezone.utc).date()).days
                
                deadlines.append({
                    'id': request.id,
                    'title': request.title,
                    'deadline': request.preferred_date.isoformat(),
                    'days_until': days_until,
                    'status': request.status,
                    'customer_name': request.customer.company_name if request.customer else 'Неизвестно',
                    'priority': request.priority or 'normal',
                    'urgency': 'high' if days_until <= 1 else 'medium' if days_until <= 3 else 'low'
                })
            
            return deadlines
            
        except Exception as e:
            logger.error(f"Ошибка получения предстоящих дедлайнов: {e}")
            return []
    
    def _get_status_color(self, status: str) -> str:
        """Получение цвета для статуса"""
        colors = {
            "new": '#2196f3',
            "manager_review": '#ff9800',
            "clarification": '#ff5722',
            "sent_to_contractors": '#9c27b0',
            "contractor_responses": '#673ab7',
            "assigned": '#4caf50',
            "in_progress": '#00bcd4',
            "completed": '#8bc34a',
            "cancelled": '#f44336'
        }
        return colors.get(status, '#757575')
    
    def _get_status_text(self, status: str) -> str:
        """Получение текста статуса"""
        texts = {
            "new": 'Новая',
            "manager_review": 'На рассмотрении',
            "clarification": 'Уточнение',
            "sent_to_contractors": 'Отправлена исполнителям',
            "contractor_responses": 'Отклики получены',
            "assigned": 'Назначена',
            "in_progress": 'В работе',
            "completed": 'Завершена',
            "cancelled": 'Отменена'
        }
        return texts.get(status, status)
    
    def _get_activity_type(self, request: RepairRequest) -> str:
        """Определение типа активности"""
        if request.status == "completed":
            return 'completed'
        elif request.status == "in_progress":
            return 'in_progress'
        elif request.status == "assigned":
            return 'assigned'
        elif request.status == "sent_to_contractors":
            return 'sent_to_contractors'
        elif request.status == "clarification":
            return 'clarification'
        else:
            return 'updated'
    
    def _get_activity_icon(self, activity_type: str) -> str:
        """Получение иконки для активности"""
        icons = {
            'completed': '✅',
            'in_progress': '🔄',
            'assigned': '👤',
            'sent_to_contractors': '📤',
            'clarification': '❓',
            'updated': '📝'
        }
        return icons.get(activity_type, '📝')

def get_manager_dashboard_service(db: Session) -> ManagerDashboardService:
    """Получение экземпляра сервиса дашборда менеджера"""
    return ManagerDashboardService(db)
