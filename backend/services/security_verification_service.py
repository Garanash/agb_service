"""
Сервис для проверки исполнителей службой безопасности
Управляет процессом верификации новых исполнителей
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import (
    SecurityVerification, ContractorProfile, User, 
    RepairRequest, RequestStatus
)

logger = logging.getLogger(__name__)

class SecurityVerificationService:
    """Сервис для проверки исполнителей службой безопасности"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_pending_verifications(self) -> List[SecurityVerification]:
        """Получение заявок на проверку, ожидающих рассмотрения"""
        return self.db.query(SecurityVerification).filter(
            SecurityVerification.verification_status == "pending"
        ).order_by(SecurityVerification.created_at.desc()).all()
    
    def get_verification_by_contractor(self, contractor_id: int) -> Optional[SecurityVerification]:
        """Получение проверки конкретного исполнителя"""
        return self.db.query(SecurityVerification).filter(
            SecurityVerification.contractor_id == contractor_id
        ).first()
    
    def create_verification_request(self, contractor_id: int) -> SecurityVerification:
        """Создание заявки на проверку исполнителя"""
        
        # Проверяем, что исполнитель существует
        contractor = self.db.query(ContractorProfile).filter(
            ContractorProfile.id == contractor_id
        ).first()
        
        if not contractor:
            raise ValueError(f"Исполнитель с ID {contractor_id} не найден")
        
        # Проверяем, что проверка еще не создана
        existing_verification = self.get_verification_by_contractor(contractor_id)
        if existing_verification:
            raise ValueError(f"Проверка для исполнителя {contractor_id} уже существует")
        
        # Создаем новую проверку
        verification = SecurityVerification(
            contractor_id=contractor_id,
            verification_status="pending"
        )
        
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        
        logger.info(f"✅ Создана заявка на проверку для исполнителя {contractor_id}")
        return verification
    
    def approve_contractor(
        self, 
        contractor_id: int, 
        security_officer_id: int,
        verification_notes: Optional[str] = None
    ) -> SecurityVerification:
        """Одобрение исполнителя службой безопасности"""
        
        verification = self.get_verification_by_contractor(contractor_id)
        if not verification:
            raise ValueError(f"Проверка для исполнителя {contractor_id} не найдена")
        
        if verification.verification_status != "pending":
            raise ValueError(f"Проверка для исполнителя {contractor_id} уже обработана")
        
        # Обновляем статус проверки
        verification.verification_status = "approved"
        verification.checked_by = security_officer_id
        verification.checked_at = datetime.now(timezone.utc)
        verification.verification_notes = verification_notes
        
        # Обновляем статус доступности исполнителя
        contractor = self.db.query(ContractorProfile).filter(
            ContractorProfile.id == contractor_id
        ).first()
        
        if contractor:
            contractor.availability_status = "available"
        
        self.db.commit()
        self.db.refresh(verification)
        
        logger.info(f"✅ Исполнитель {contractor_id} одобрен службой безопасности")
        return verification
    
    def reject_contractor(
        self, 
        contractor_id: int, 
        security_officer_id: int,
        verification_notes: str
    ) -> SecurityVerification:
        """Отклонение исполнителя службой безопасности"""
        
        verification = self.get_verification_by_contractor(contractor_id)
        if not verification:
            raise ValueError(f"Проверка для исполнителя {contractor_id} не найдена")
        
        if verification.verification_status != "pending":
            raise ValueError(f"Проверка для исполнителя {contractor_id} уже обработана")
        
        # Обновляем статус проверки
        verification.verification_status = "rejected"
        verification.checked_by = security_officer_id
        verification.checked_at = datetime.now(timezone.utc)
        verification.verification_notes = verification_notes
        
        # Обновляем статус доступности исполнителя
        contractor = self.db.query(ContractorProfile).filter(
            ContractorProfile.id == contractor_id
        ).first()
        
        if contractor:
            contractor.availability_status = "blocked"
        
        # Деактивируем пользователя
        user = self.db.query(User).filter(User.id == contractor.user_id).first()
        if user:
            user.is_active = False
        
        self.db.commit()
        self.db.refresh(verification)
        
        logger.info(f"❌ Исполнитель {contractor_id} отклонен службой безопасности")
        return verification
    
    def get_verified_contractors(self) -> List[ContractorProfile]:
        """Получение списка проверенных исполнителей"""
        verified_contractors = self.db.query(ContractorProfile).join(SecurityVerification).filter(
            SecurityVerification.verification_status == "approved"
        ).all()
        
        return verified_contractors
    
    def get_rejected_contractors(self) -> List[ContractorProfile]:
        """Получение списка отклоненных исполнителей"""
        rejected_contractors = self.db.query(ContractorProfile).join(SecurityVerification).filter(
            SecurityVerification.verification_status == "rejected"
        ).all()
        
        return rejected_contractors
    
    def get_contractor_verification_status(self, contractor_id: int) -> Dict[str, Any]:
        """Получение статуса проверки исполнителя"""
        verification = self.get_verification_by_contractor(contractor_id)
        
        if not verification:
            return {
                "status": "not_verified",
                "message": "Проверка не проводилась",
                "can_respond": False
            }
        
        status_mapping = {
            "pending": {
                "status": "pending",
                "message": "Ожидает проверки службой безопасности",
                "can_respond": False
            },
            "approved": {
                "status": "approved",
                "message": "Проверен и одобрен",
                "can_respond": True
            },
            "rejected": {
                "status": "rejected",
                "message": "Отклонен службой безопасности",
                "can_respond": False
            }
        }
        
        result = status_mapping.get(verification.verification_status, {
            "status": "unknown",
            "message": "Неизвестный статус",
            "can_respond": False
        })
        
        result.update({
            "verification_id": verification.id,
            "checked_by": verification.checked_by,
            "checked_at": verification.checked_at.isoformat() if verification.checked_at else None,
            "verification_notes": verification.verification_notes
        })
        
        return result
    
    def check_contractor_can_respond(self, contractor_id: int) -> bool:
        """Проверка, может ли исполнитель отвечать на заявки"""
        status = self.get_contractor_verification_status(contractor_id)
        return status["can_respond"]
    
    def get_security_statistics(self) -> Dict[str, Any]:
        """Получение статистики для службы безопасности"""
        
        # Общее количество проверок
        total_verifications = self.db.query(SecurityVerification).count()
        
        # Проверки по статусам
        pending_count = self.db.query(SecurityVerification).filter(
            SecurityVerification.verification_status == "pending"
        ).count()
        
        approved_count = self.db.query(SecurityVerification).filter(
            SecurityVerification.verification_status == "approved"
        ).count()
        
        rejected_count = self.db.query(SecurityVerification).filter(
            SecurityVerification.verification_status == "rejected"
        ).count()
        
        # Проверки за последние 30 дней
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_verifications = self.db.query(SecurityVerification).filter(
            SecurityVerification.created_at >= thirty_days_ago
        ).count()
        
        # Среднее время обработки проверки
        processed_verifications = self.db.query(SecurityVerification).filter(
            and_(
                SecurityVerification.checked_at.isnot(None),
                SecurityVerification.created_at.isnot(None)
            )
        ).all()
        
        avg_processing_time = 0
        if processed_verifications:
            total_time = sum([
                (ver.checked_at - ver.created_at).total_seconds() / 3600  # в часах
                for ver in processed_verifications
                if ver.checked_at and ver.created_at
            ])
            avg_processing_time = total_time / len(processed_verifications)
        
        return {
            "total_verifications": total_verifications,
            "pending_count": pending_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "recent_verifications": recent_verifications,
            "avg_processing_time_hours": round(avg_processing_time, 1),
            "approval_rate": round(
                (approved_count / total_verifications * 100) if total_verifications > 0 else 0, 1
            )
        }
    
    def get_contractor_detailed_info(self, contractor_id: int) -> Dict[str, Any]:
        """Получение детальной информации об исполнителе для проверки"""
        
        contractor = self.db.query(ContractorProfile).filter(
            ContractorProfile.id == contractor_id
        ).first()
        
        if not contractor:
            raise ValueError(f"Исполнитель с ID {contractor_id} не найден")
        
        user = self.db.query(User).filter(User.id == contractor.user_id).first()
        
        # Получаем информацию о проверке
        verification = self.get_verification_by_contractor(contractor_id)
        
        # Получаем историю заявок (если есть)
        requests_history = self.db.query(RepairRequest).filter(
            RepairRequest.assigned_contractor_id == contractor.user_id
        ).count()
        
        return {
            "contractor_id": contractor.id,
            "user_id": contractor.user_id,
            "personal_info": {
                "first_name": contractor.first_name,
                "last_name": contractor.last_name,
                "patronymic": contractor.patronymic,
                "phone": contractor.phone,
                "email": contractor.email,
                "telegram_username": contractor.telegram_username
            },
            "professional_info": {
                "specializations": contractor.specializations or [],
                "equipment_brands_experience": contractor.equipment_brands_experience or [],
                "certifications": contractor.certifications or [],
                "work_regions": contractor.work_regions or [],
                "hourly_rate": contractor.hourly_rate,
                "availability_status": contractor.availability_status
            },
            "verification_info": {
                "status": verification.verification_status if verification else "not_verified",
                "created_at": verification.created_at.isoformat() if verification else None,
                "checked_at": verification.checked_at.isoformat() if verification and verification.checked_at else None,
                "checked_by": verification.checked_by if verification else None,
                "verification_notes": verification.verification_notes if verification else None
            },
            "activity_info": {
                "requests_count": requests_history,
                "registration_date": user.created_at.isoformat() if user else None,
                "is_active": user.is_active if user else False
            }
        }

def get_security_verification_service(db: Session) -> SecurityVerificationService:
    """Получение экземпляра сервиса проверки безопасности"""
    return SecurityVerificationService(db)
