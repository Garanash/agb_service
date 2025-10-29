"""
API endpoints для службы безопасности
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, ContractorProfile
from api.v1.schemas import (
    SecurityVerificationCreate, SecurityVerificationResponse,
    SecurityVerificationUpdate
)
from api.v1.dependencies import get_current_user
from services.security_verification_service import get_security_verification_service, SecurityVerificationService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/pending", response_model=List[SecurityVerificationResponse])
async def get_pending_verifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение заявок на проверку, ожидающих рассмотрения"""
    if current_user.role not in ["security", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники службы безопасности могут просматривать заявки на проверку"
        )
    
    verification_service = get_security_verification_service(db)
    pending_verifications = verification_service.get_pending_verifications()
    
    result = []
    for ver in pending_verifications:
        # Получаем информацию об исполнителе
        contractor_profile = db.query(ContractorProfile).filter(
            ContractorProfile.id == ver.contractor_id
        ).first()
        
        contractor_name = None
        contractor_email = None
        contractor_phone = None
        contractor_data = None
        
        if contractor_profile:
            user = db.query(User).filter(User.id == contractor_profile.user_id).first()
            if user:
                contractor_name = f"{user.first_name} {user.last_name}"
                contractor_email = user.email
                contractor_phone = user.phone
                
                # Добавляем дополнительную информацию об исполнителе
                contractor_data = {
                    "id": contractor_profile.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone,
                    "email": user.email,
                    "specializations": contractor_profile.specializations or [],
                    "equipment_brands_experience": contractor_profile.equipment_brands_experience or [],
                    "certifications": contractor_profile.certifications or [],
                    "work_regions": contractor_profile.work_regions or [],
                    "hourly_rate": contractor_profile.hourly_rate,
                    "availability_status": contractor_profile.availability_status or "unknown",
                    "general_description": contractor_profile.general_description
                }
        
        # Создаем объект ответа с дополнительными полями
        verification_data = SecurityVerificationResponse(
            id=ver.id,
            contractor_id=ver.contractor_id,
            verification_status=ver.verification_status,
            verification_notes=ver.verification_notes,
            checked_by=ver.checked_by,
            created_at=ver.created_at,
            updated_at=ver.updated_at,
            contractor_name=contractor_name,
            contractor_email=contractor_email,
            contractor_phone=contractor_phone,
            contractor=contractor_data
        )
        
        result.append(verification_data)
    
    return result

@router.get("/verified", response_model=List[Dict[str, Any]])
async def get_verified_contractors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка проверенных исполнителей"""
    if current_user.role not in ["security", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники службы безопасности могут просматривать проверенных исполнителей"
        )
    
    from models import ContractorVerification
    
    # Получаем проверенных исполнителей через новую систему
    verifications = db.query(ContractorVerification).filter(
        ContractorVerification.security_check_passed == True
    ).all()
    
    result = []
    for verification in verifications:
        contractor = db.query(ContractorProfile).filter(
            ContractorProfile.id == verification.contractor_id
        ).first()
        
        if contractor:
            user = db.query(User).filter(User.id == contractor.user_id).first()
            result.append({
                "contractor_id": contractor.id,
                "name": f"{contractor.first_name or ''} {contractor.last_name or ''}".strip() or (user.username if user else 'Неизвестно'),
                "phone": contractor.phone or (user.phone if user else None),
                "email": contractor.email or (user.email if user else None),
                "specializations": contractor.specializations if contractor.specializations and isinstance(contractor.specializations, list) else [],
                "verified_at": verification.security_checked_at.isoformat() if verification.security_checked_at else None,
                "verified_by": verification.security_checked_by
            })
    
    return result

@router.get("/rejected", response_model=List[Dict[str, Any]])
async def get_rejected_contractors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка отклоненных исполнителей"""
    if current_user.role not in ["security", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники службы безопасности могут просматривать отклоненных исполнителей"
        )
    
    from models import ContractorVerification
    
    # Получаем отклоненных исполнителей через новую систему
    verifications = db.query(ContractorVerification).filter(
        ContractorVerification.security_check_passed == False,
        ContractorVerification.security_checked_at.isnot(None)
    ).all()
    
    result = []
    for verification in verifications:
        contractor = db.query(ContractorProfile).filter(
            ContractorProfile.id == verification.contractor_id
        ).first()
        
        if contractor:
            user = db.query(User).filter(User.id == contractor.user_id).first()
            result.append({
                "contractor_id": contractor.id,
                "name": f"{contractor.first_name or ''} {contractor.last_name or ''}".strip() or (user.username if user else 'Неизвестно'),
                "phone": contractor.phone or (user.phone if user else None),
                "email": contractor.email or (user.email if user else None),
                "rejection_reason": verification.security_notes,
                "rejected_at": verification.security_checked_at.isoformat() if verification.security_checked_at else None,
                "rejected_by": verification.security_checked_by
            })
    
    return result

@router.get("/contractor/{contractor_id}/details")
async def get_contractor_details(
    contractor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение детальной информации об исполнителе для проверки"""
    if current_user.role not in ["security", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники службы безопасности могут просматривать детальную информацию"
        )
    
    verification_service = get_security_verification_service(db)
    
    try:
        details = verification_service.get_contractor_detailed_info(contractor_id)
        return details
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/contractor/{contractor_id}/status")
async def get_contractor_verification_status(
    contractor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статуса проверки исполнителя"""
    verification_service = get_security_verification_service(db)
    
    try:
        status_info = verification_service.get_contractor_verification_status(contractor_id)
        return status_info
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/contractor/{contractor_id}/approve")
async def approve_contractor(
    contractor_id: int,
    approval_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Одобрение исполнителя службой безопасности"""
    if current_user.role not in ["security", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники службы безопасности могут одобрять исполнителей"
        )
    
    verification_service = get_security_verification_service(db)
    
    try:
        verification = verification_service.approve_contractor(
            contractor_id=contractor_id,
            security_officer_id=current_user.id,
            verification_notes=approval_data.get("verification_notes")
        )
        
        return {
            "message": f"Исполнитель {contractor_id} одобрен",
            "verification": SecurityVerificationResponse.from_orm(verification)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/contractor/{contractor_id}/reject")
async def reject_contractor(
    contractor_id: int,
    rejection_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отклонение исполнителя службой безопасности"""
    if current_user.role not in ["security", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники службы безопасности могут отклонять исполнителей"
        )
    
    verification_service = get_security_verification_service(db)
    
    verification_notes = rejection_data.get("verification_notes")
    if not verification_notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Обязательно указать причину отклонения"
        )
    
    try:
        verification = verification_service.reject_contractor(
            contractor_id=contractor_id,
            security_officer_id=current_user.id,
            verification_notes=verification_notes
        )
        
        return {
            "message": f"Исполнитель {contractor_id} отклонен",
            "verification": SecurityVerificationResponse.from_orm(verification)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/contractor/{contractor_id}/create-verification")
async def create_verification_request(
    contractor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание заявки на проверку исполнителя"""
    if current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут создавать заявки на проверку"
        )
    
    verification_service = get_security_verification_service(db)
    
    try:
        verification = verification_service.create_verification_request(contractor_id)
        
        return {
            "message": f"Заявка на проверку исполнителя {contractor_id} создана",
            "verification": SecurityVerificationResponse.from_orm(verification)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/statistics")
async def get_security_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики для службы безопасности"""
    if current_user.role not in ["security", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники службы безопасности могут просматривать статистику"
        )
    
    verification_service = get_security_verification_service(db)
    stats = verification_service.get_security_statistics()
    
    return stats

@router.get("/check-contractor-access/{contractor_id}")
async def check_contractor_access(
    contractor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Проверка доступа исполнителя к ответам на заявки"""
    verification_service = get_security_verification_service(db)
    
    can_respond = verification_service.check_contractor_can_respond(contractor_id)
    status_info = verification_service.get_contractor_verification_status(contractor_id)
    
    return {
        "contractor_id": contractor_id,
        "can_respond": can_respond,
        "status_info": status_info
    }

@router.get("/contractor/{contractor_id}/details")
async def get_contractor_details(
    contractor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение детальной информации об исполнителе для службы безопасности"""
    if current_user.role not in ["security", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники службы безопасности могут просматривать детали исполнителей"
        )
    
    verification_service = get_security_verification_service(db)
    
    # Получаем профиль исполнителя
    contractor_profile = db.query(ContractorProfile).filter(
        ContractorProfile.id == contractor_id
    ).first()
    
    if not contractor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Исполнитель не найден"
        )
    
    # Получаем пользователя
    user = db.query(User).filter(User.id == contractor_profile.user_id).first()
    
    # Получаем информацию о проверке
    verification = verification_service.get_verification_by_contractor(contractor_id)
    
    # Получаем статистику заявок
    requests_count = db.query(RepairRequest).filter(
        RepairRequest.assigned_contractor_id == contractor_profile.user_id
    ).count()
    
    return {
        "contractor_id": contractor_id,
        "user_id": contractor_profile.user_id,
        "personal_info": {
            "first_name": contractor_profile.first_name or user.first_name,
            "last_name": contractor_profile.last_name or user.last_name,
            "patronymic": contractor_profile.patronymic,
            "phone": contractor_profile.phone or user.phone,
            "email": contractor_profile.email or user.email,
            "telegram_username": contractor_profile.telegram_username
        },
        "professional_info": {
            "specializations": contractor_profile.specializations or [],
            "equipment_brands_experience": contractor_profile.equipment_brands_experience or [],
            "certifications": contractor_profile.certifications or [],
            "work_regions": contractor_profile.work_regions or [],
            "hourly_rate": contractor_profile.hourly_rate,
            "availability_status": contractor_profile.availability_status or "unknown",
            "general_description": contractor_profile.general_description
        },
        "verification_info": {
            "status": verification.verification_status if verification else "not_verified",
            "created_at": verification.created_at.isoformat() if verification and verification.created_at else None,
            "checked_at": verification.checked_at.isoformat() if verification and verification.checked_at else None,
            "checked_by": verification.checked_by,
            "verification_notes": verification.verification_notes if verification else None
        },
        "activity_info": {
            "requests_count": requests_count,
            "registration_date": user.created_at.isoformat(),
            "is_active": user.is_active
        }
    }

@router.get("/statistics")
async def get_security_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики службы безопасности"""
    if current_user.role not in ["security", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только сотрудники службы безопасности могут просматривать статистику"
        )
    
    verification_service = get_security_verification_service(db)
    stats = verification_service.get_security_statistics()
    
    return stats
