"""
API endpoints для системы верификации исполнителей
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
import logging
import os
import shutil
from datetime import datetime

from database import get_db
from models import (
    User, ContractorProfile, ContractorEducation, ContractorDocument, 
    ContractorVerification, UserRole
)
from ..schemas import (
    ContractorProfileExtended, ContractorProfileUpdate,
    ContractorEducationCreate, ContractorEducationResponse,
    ContractorDocumentCreate, ContractorDocumentResponse,
    ContractorVerificationResponse, DocumentVerificationRequest,
    ContractorVerificationRequest, VerificationStatus, DocumentType
)
from ..dependencies import get_current_user, require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contractor-verification", tags=["Contractor Verification"])

# Константы
UPLOAD_DIR = "/app/uploads/contractor_documents"
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def ensure_upload_dir():
    """Создает директорию для загрузки файлов если её нет"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/profile/{contractor_id}", response_model=ContractorProfileExtended)
async def get_contractor_profile_extended(
    contractor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить расширенный профиль исполнителя с образованием и документами"""
    
    # Проверяем права доступа
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.SECURITY]:
        if current_user.contractor_profile and current_user.contractor_profile.id != contractor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав для просмотра этого профиля"
            )
    
    contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Исполнитель не найден"
        )
    
    # Получаем образование
    education_records = db.query(ContractorEducation).filter(
        ContractorEducation.contractor_id == contractor_id
    ).all()
    
    # Получаем документы
    documents = db.query(ContractorDocument).filter(
        ContractorDocument.contractor_id == contractor_id
    ).all()
    
    # Получаем верификацию
    verification = db.query(ContractorVerification).filter(
        ContractorVerification.contractor_id == contractor_id
    ).first()
    
    # Преобразуем даты в строки для корректной сериализации
    from datetime import date, datetime
    
    contractor_dict = {
        "id": contractor.id,
        "user_id": contractor.user_id,
        "first_name": contractor.first_name,
        "last_name": contractor.last_name,
        "patronymic": contractor.patronymic,
        "phone": contractor.phone,
        "email": contractor.email,
        "passport_series": contractor.passport_series,
        "passport_number": contractor.passport_number,
        "passport_issued_by": contractor.passport_issued_by,
        "passport_issued_date": contractor.passport_issued_date.isoformat() if contractor.passport_issued_date and isinstance(contractor.passport_issued_date, (date, datetime)) else contractor.passport_issued_date,
        "passport_issued_code": contractor.passport_issued_code,
        "birth_date": contractor.birth_date.isoformat() if contractor.birth_date and isinstance(contractor.birth_date, (date, datetime)) else contractor.birth_date,
        "birth_place": contractor.birth_place,
        "inn": contractor.inn,
        "professional_info": contractor.professional_info if contractor.professional_info and isinstance(contractor.professional_info, list) else [],
        "bank_name": contractor.bank_name,
        "bank_account": contractor.bank_account,
        "bank_bik": contractor.bank_bik,
        "telegram_username": contractor.telegram_username,
        "website": contractor.website,
        "general_description": contractor.general_description,
        "profile_photo_path": contractor.profile_photo_path,
        "specializations": contractor.specializations if contractor.specializations and isinstance(contractor.specializations, list) else [],
        "equipment_brands_experience": contractor.equipment_brands_experience if contractor.equipment_brands_experience else [],
        "certifications": contractor.certifications if contractor.certifications else [],
        "work_regions": contractor.work_regions if contractor.work_regions else [],
        "hourly_rate": float(contractor.hourly_rate) if contractor.hourly_rate is not None else None,
        "availability_status": contractor.availability_status or "unknown",
        "profile_completion_status": contractor.profile_completion_status,
        "security_verified": contractor.security_verified,
        "manager_verified": contractor.manager_verified,
        "security_verified_at": contractor.security_verified_at.isoformat() if contractor.security_verified_at and isinstance(contractor.security_verified_at, (date, datetime)) else contractor.security_verified_at,
        "manager_verified_at": contractor.manager_verified_at.isoformat() if contractor.manager_verified_at and isinstance(contractor.manager_verified_at, (date, datetime)) else contractor.manager_verified_at,
        "security_verified_by": contractor.security_verified_by,
        "manager_verified_by": contractor.manager_verified_by,
        "created_at": contractor.created_at.isoformat() if contractor.created_at and isinstance(contractor.created_at, (date, datetime)) else contractor.created_at,
        "updated_at": contractor.updated_at.isoformat() if contractor.updated_at and isinstance(contractor.updated_at, (date, datetime)) else contractor.updated_at,
    }
    
    return ContractorProfileExtended(
        **contractor_dict,
        education_records=education_records,
        documents=documents,
        verification=verification
    )

@router.put("/profile/{contractor_id}", response_model=ContractorProfileExtended)
async def update_contractor_profile(
    contractor_id: int,
    profile_data: ContractorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить профиль исполнителя"""
    
    # Проверяем права доступа
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        if current_user.contractor_profile and current_user.contractor_profile.id != contractor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав для редактирования этого профиля"
            )
    
    contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Исполнитель не найден"
        )
    
    # Обновляем поля профиля
    update_data = profile_data.dict(exclude_unset=True)
    
    # Обрабатываем валидацию паспортных данных
    if 'passport_series' in update_data and update_data['passport_series']:
        if not update_data['passport_series'].isdigit() or len(update_data['passport_series']) != 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Серия паспорта должна состоять из 4 цифр"
            )
    
    if 'passport_number' in update_data and update_data['passport_number']:
        if not update_data['passport_number'].isdigit() or len(update_data['passport_number']) != 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Номер паспорта должен состоять из 6 цифр"
            )
    
    if 'passport_issued_code' in update_data and update_data['passport_issued_code']:
        if not update_data['passport_issued_code'].isdigit() or len(update_data['passport_issued_code']) != 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Код подразделения должен состоять из 6 цифр"
            )
    
    # Валидация специализаций
    if 'specializations' in update_data and update_data['specializations'] is not None:
        valid_specializations = ['электрика', 'гидравлика', 'двс', 'агрегаты', 'перфораторы', 'другое']
        valid_levels = ['начальный', 'средний', 'продвинутый', 'эксперт']
        
        if not isinstance(update_data['specializations'], list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Специализации должны быть списком"
            )
        
        for spec in update_data['specializations']:
            if isinstance(spec, dict):
                if 'specialization' not in spec or 'level' not in spec:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Каждая специализация должна содержать поля 'specialization' и 'level'"
                    )
                if spec['specialization'] not in valid_specializations:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Неверная специализация: {spec['specialization']}. Доступные: {', '.join(valid_specializations)}"
                    )
                if spec['level'] not in valid_levels:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Неверный уровень владения: {spec['level']}. Доступные: {', '.join(valid_levels)}"
                    )
    
    # Обрабатываем hourly_rate - убеждаемся что это число
    if 'hourly_rate' in update_data and update_data['hourly_rate'] is not None:
        try:
            if isinstance(update_data['hourly_rate'], str):
                update_data['hourly_rate'] = float(update_data['hourly_rate'])
            elif not isinstance(update_data['hourly_rate'], (int, float)):
                raise ValueError("hourly_rate должен быть числом")
            if update_data['hourly_rate'] < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Почасовая ставка не может быть отрицательной"
                )
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Почасовая ставка должна быть числом"
            )
    
    for field, value in update_data.items():
        setattr(contractor, field, value)
    
    contractor.updated_at = datetime.utcnow()
    
    # Проверяем полноту профиля
    await check_profile_completion(contractor_id, db)
    
    db.commit()
    db.refresh(contractor)
    
    # Возвращаем обновленный профиль
    return await get_contractor_profile_extended(contractor_id, db, current_user)

@router.post("/education/{contractor_id}", response_model=ContractorEducationResponse)
async def add_education_record(
    contractor_id: int,
    education_data: ContractorEducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Добавить запись об образовании"""
    
    # Проверяем права доступа
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        if current_user.contractor_profile and current_user.contractor_profile.id != contractor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав для добавления образования"
            )
    
    contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Исполнитель не найден"
        )
    
    education_record = ContractorEducation(
        contractor_id=contractor_id,
        **education_data.dict()
    )
    
    db.add(education_record)
    db.commit()
    db.refresh(education_record)
    
    logger.info(f"✅ Добавлена запись об образовании для исполнителя {contractor_id}")
    
    return education_record

@router.put("/education/{education_id}", response_model=ContractorEducationResponse)
async def update_education_record(
    education_id: int,
    education_data: ContractorEducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить запись об образовании"""
    
    education_record = db.query(ContractorEducation).filter(
        ContractorEducation.id == education_id
    ).first()
    
    if not education_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись об образовании не найдена"
        )
    
    # Проверяем права доступа
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        if current_user.contractor_profile and current_user.contractor_profile.id != education_record.contractor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав для редактирования этой записи"
            )
    
    # Обновляем поля
    update_data = education_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(education_record, field, value)
    
    db.commit()
    db.refresh(education_record)
    
    logger.info(f"✅ Обновлена запись об образовании {education_id}")
    
    return education_record

@router.delete("/education/{education_id}")
async def delete_education_record(
    education_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить запись об образовании"""
    
    education_record = db.query(ContractorEducation).filter(
        ContractorEducation.id == education_id
    ).first()
    
    if not education_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись об образовании не найдена"
        )
    
    # Проверяем права доступа
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        if current_user.contractor_profile and current_user.contractor_profile.id != education_record.contractor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав для удаления этой записи"
            )
    
    db.delete(education_record)
    db.commit()
    
    logger.info(f"✅ Удалена запись об образовании {education_id}")
    
    return {"message": "Запись об образовании удалена"}

@router.post("/documents/{contractor_id}/upload", response_model=ContractorDocumentResponse)
async def upload_document(
    contractor_id: int,
    document_type: DocumentType = Form(...),
    document_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Загрузить документ исполнителя"""
    
    # Проверяем права доступа
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        if current_user.contractor_profile and current_user.contractor_profile.id != contractor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав для загрузки документов"
            )
    
    contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Исполнитель не найден"
        )
    
    # Проверяем расширение файла
    file_extension = os.path.splitext(file.filename)[1].lower() if file.filename else ''
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Читаем содержимое файла для проверки размера
    file_content = await file.read()
    file_size = len(file_content)
    
    # Проверяем размер файла
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Создаем директорию для файлов
    ensure_upload_dir()
    
    # Генерируем уникальное имя файла
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{contractor_id}_{document_type.value}_{timestamp}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Сохраняем файл
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения файла: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сохранения файла"
        )
    
    # Создаем запись в базе данных
    document = ContractorDocument(
        contractor_id=contractor_id,
        document_type=document_type.value,
        document_name=document_name,
        document_path=file_path,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream"
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    logger.info(f"✅ Загружен документ {document_name} для исполнителя {contractor_id}")
    
    return document

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить документ исполнителя"""
    
    document = db.query(ContractorDocument).filter(
        ContractorDocument.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден"
        )
    
    # Проверяем права доступа
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        if current_user.contractor_profile and current_user.contractor_profile.id != document.contractor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав для удаления этого документа"
            )
    
    # Удаляем файл с диска
    try:
        if os.path.exists(document.document_path):
            os.remove(document.document_path)
    except Exception as e:
        logger.warning(f"⚠️ Не удалось удалить файл {document.document_path}: {e}")
    
    # Удаляем запись из базы данных
    db.delete(document)
    db.commit()
    
    logger.info(f"✅ Удален документ {document_id}")
    
    return {"message": "Документ удален"}

@router.put("/documents/{document_id}/verify", response_model=ContractorDocumentResponse)
async def verify_document(
    document_id: int,
    verification_data: DocumentVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECURITY, UserRole.MANAGER]))
):
    """Проверить документ (только для СБ, менеджеров и админов)"""
    
    document = db.query(ContractorDocument).filter(
        ContractorDocument.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден"
        )
    
    # Обновляем статус проверки
    document.verification_status = verification_data.verification_status
    document.verification_notes = verification_data.verification_notes
    document.verified_by = current_user.id
    document.verified_at = datetime.utcnow()
    
    db.commit()
    db.refresh(document)
    
    logger.info(f"✅ Документ {document_id} проверен: {verification_data.verification_status}")
    
    return document

@router.put("/contractor/{contractor_id}/verify", response_model=ContractorVerificationResponse)
async def verify_contractor(
    contractor_id: int,
    verification_data: ContractorVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECURITY, UserRole.MANAGER]))
):
    """Проверить исполнителя (СБ или менеджер)"""
    
    contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Исполнитель не найден"
        )
    
    verification = db.query(ContractorVerification).filter(
        ContractorVerification.contractor_id == contractor_id
    ).first()
    
    if not verification:
        verification = ContractorVerification(contractor_id=contractor_id)
        db.add(verification)
    
    # Обновляем статус проверки в зависимости от типа
    if verification_data.verification_type == "security":
        if current_user.role not in [UserRole.ADMIN, UserRole.SECURITY]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только служба безопасности может проводить проверку СБ"
            )
        
        verification.security_check_passed = verification_data.approved
        verification.security_notes = verification_data.notes
        verification.security_checked_by = current_user.id
        verification.security_checked_at = datetime.utcnow()
        
        # Обновляем статус в профиле
        contractor.security_verified = verification_data.approved
        contractor.security_verified_by = current_user.id
        contractor.security_verified_at = datetime.utcnow()
        
        # Если отклонено - блокируем пользователя
        if not verification_data.approved:
            user = db.query(User).filter(User.id == contractor.user_id).first()
            if user:
                user.is_active = False
    elif verification_data.verification_type == "manager":
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только менеджеры могут проводить проверку менеджера"
            )
        
        verification.manager_approval = verification_data.approved
        verification.manager_notes = verification_data.notes
        verification.manager_checked_by = current_user.id
        verification.manager_checked_at = datetime.utcnow()
        
        # Обновляем статус в профиле
        contractor.manager_verified = verification_data.approved
        contractor.manager_verified_by = current_user.id
        contractor.manager_verified_at = datetime.utcnow()
    
    # Обновляем общий статус
    await update_overall_verification_status(contractor_id, db)
    
    db.commit()
    db.refresh(verification)
    
    # Отправляем email уведомления
    try:
        if verification_data.verification_type == "security":
            if verification_data.approved:
                # Отправляем уведомление об одобрении СБ
                await send_security_approval_email(contractor_id, db, verification_data.notes)
            else:
                # Отправляем уведомление об отклонении СБ
                await send_security_rejection_email(contractor_id, db, verification_data.notes)
    except Exception as e:
        logger.error(f"❌ Ошибка отправки email уведомления: {e}")
    
    logger.info(f"✅ Исполнитель {contractor_id} проверен {verification_data.verification_type}: {verification_data.approved}")
    
    return verification

@router.get("/pending", response_model=List[ContractorVerificationResponse])
async def get_pending_verifications(
    verification_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECURITY, UserRole.MANAGER]))
):
    """Получить список исполнителей, ожидающих проверки"""
    
    query = db.query(ContractorVerification)
    
    if verification_type == "security":
        query = query.filter(
            ContractorVerification.security_check_passed == False,
            ContractorVerification.profile_completed == True,
            ContractorVerification.documents_uploaded == True
        )
    elif verification_type == "manager":
        query = query.filter(
            ContractorVerification.manager_approval == False,
            ContractorVerification.security_check_passed == True
        )
    else:
        query = query.filter(
            ContractorVerification.overall_status.in_([
                VerificationStatus.PENDING_SECURITY,
                VerificationStatus.PENDING_MANAGER
            ])
        )
    
    verifications = query.all()
    
    # Добавляем данные профилей исполнителей к каждой верификации
    result = []
    for verification in verifications:
        contractor = db.query(ContractorProfile).filter(
            ContractorProfile.id == verification.contractor_id
        ).first()
        
        if contractor:
            user = db.query(User).filter(User.id == contractor.user_id).first()
            
            # Преобразуем verification в словарь и добавляем данные профиля
            # Получаем overall_status как строку
            overall_status_str = None
            if verification.overall_status:
                if hasattr(verification.overall_status, 'value'):
                    overall_status_str = verification.overall_status.value
                elif isinstance(verification.overall_status, str):
                    overall_status_str = verification.overall_status.lower()
                else:
                    overall_status_str = str(verification.overall_status).lower()
            
            verification_dict = {
                "id": verification.id,
                "contractor_id": verification.contractor_id,
                "profile_completed": verification.profile_completed,
                "documents_uploaded": verification.documents_uploaded,
                "security_check_passed": verification.security_check_passed,
                "manager_approval": verification.manager_approval,
                "overall_status": overall_status_str,
                "security_notes": verification.security_notes,
                "manager_notes": verification.manager_notes,
                "security_checked_by": verification.security_checked_by,
                "manager_checked_by": verification.manager_checked_by,
                "security_checked_at": verification.security_checked_at.isoformat() if verification.security_checked_at else None,
                "manager_checked_at": verification.manager_checked_at.isoformat() if verification.manager_checked_at else None,
                "created_at": verification.created_at.isoformat() if verification.created_at else None,
                "updated_at": verification.updated_at.isoformat() if verification.updated_at else None,
                "contractor": {
                    "id": contractor.id,
                    "first_name": contractor.first_name or (user.first_name if user else None) or "",
                    "last_name": contractor.last_name or (user.last_name if user else None) or "",
                    "patronymic": contractor.patronymic or "",
                    "phone": contractor.phone or (user.phone if user else None) or "",
                    "email": contractor.email or (user.email if user else None) or "",
                    "telegram_username": contractor.telegram_username or "",
                    "inn": contractor.inn or "",
                    "specializations": contractor.specializations if contractor.specializations and isinstance(contractor.specializations, list) else [],
                    "equipment_brands_experience": contractor.equipment_brands_experience if contractor.equipment_brands_experience else [],
                    "certifications": contractor.certifications if contractor.certifications else [],
                    "work_regions": contractor.work_regions if contractor.work_regions else [],
                    "hourly_rate": float(contractor.hourly_rate) if contractor.hourly_rate is not None else None,
                    "availability_status": contractor.availability_status or "unknown"
                },
                "verification_status": "pending" if not verification.security_check_passed else ("approved" if verification.security_check_passed and verification.manager_approval else "pending_manager"),
                "security_check_passed": verification.security_check_passed
            }
            result.append(verification_dict)
        else:
            # Если профиль не найден, все равно возвращаем верификацию
            verification_dict = {
                "id": verification.id,
                "contractor_id": verification.contractor_id,
                "profile_completed": verification.profile_completed,
                "documents_uploaded": verification.documents_uploaded,
                "security_check_passed": verification.security_check_passed,
                "manager_approval": verification.manager_approval,
                "overall_status": verification.overall_status,
                "security_notes": verification.security_notes,
                "manager_notes": verification.manager_notes,
                "security_checked_by": verification.security_checked_by,
                "manager_checked_by": verification.manager_checked_by,
                "security_checked_at": verification.security_checked_at.isoformat() if verification.security_checked_at else None,
                "manager_checked_at": verification.manager_checked_at.isoformat() if verification.manager_checked_at else None,
                "created_at": verification.created_at.isoformat() if verification.created_at else None,
                "updated_at": verification.updated_at.isoformat() if verification.updated_at else None,
                "contractor": None,
                "verification_status": "pending"
            }
            result.append(verification_dict)
    
    return result

@router.post("/contractor/{contractor_id}/request-clarification")
async def request_clarification(
    contractor_id: int,
    clarification_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECURITY]))
):
    """Запросить уточнение данных у исполнителя"""
    
    contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Исполнитель не найден"
        )
    
    notes = clarification_data.get("notes", "")
    if not notes or not notes.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать, какие данные требуют уточнения"
        )
    
    # Отправляем email уведомление
    await send_clarification_request_email(contractor_id, db, notes)
    
    # Обновляем заметки в верификации
    verification = db.query(ContractorVerification).filter(
        ContractorVerification.contractor_id == contractor_id
    ).first()
    
    if verification:
        verification.security_notes = f"Запрос на уточнение данных: {notes}"
        db.commit()
    
    return {"message": "Запрос на уточнение данных отправлен исполнителю", "contractor_id": contractor_id}

async def check_profile_completion(contractor_id: int, db: Session):
    """Проверяет полноту профиля исполнителя"""
    
    contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
    if not contractor:
        return
    
    verification = db.query(ContractorVerification).filter(
        ContractorVerification.contractor_id == contractor_id
    ).first()
    
    if not verification:
        verification = ContractorVerification(contractor_id=contractor_id)
        db.add(verification)
    
    # Проверяем заполненность основных полей
    required_fields = [
        contractor.first_name, contractor.last_name, contractor.phone, contractor.email,
        contractor.passport_series, contractor.passport_number, contractor.inn,
        contractor.specializations, contractor.equipment_brands_experience
    ]
    
    profile_completed = all(field is not None and field != "" for field in required_fields)
    
    # Проверяем наличие документов
    documents_count = db.query(ContractorDocument).filter(
        ContractorDocument.contractor_id == contractor_id
    ).count()
    
    documents_uploaded = documents_count > 0
    
    # Проверяем наличие образования
    education_count = db.query(ContractorEducation).filter(
        ContractorEducation.contractor_id == contractor_id
    ).count()
    
    education_completed = education_count > 0
    
    # Обновляем статусы
    verification.profile_completed = profile_completed and education_completed
    verification.documents_uploaded = documents_uploaded
    
    # Обновляем статус в профиле
    contractor.profile_completion_status = "complete" if verification.profile_completed else "incomplete"
    
    # Обновляем общий статус
    await update_overall_verification_status(contractor_id, db)

async def send_verification_notification_to_security(contractor_id: int, db: Session):
    """Отправка email уведомления сотрудникам службы безопасности"""
    try:
        from services.email_service import email_service
        
        # Получаем информацию об исполнителе
        contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
        if not contractor:
            return
        
        user = db.query(User).filter(User.id == contractor.user_id).first()
        if not user:
            return
        
        contractor_name = f"{contractor.first_name or ''} {contractor.last_name or ''}".strip() or user.username
        
        # Получаем всех сотрудников службы безопасности и админов
        security_users = db.query(User).filter(
            User.role.in_(["security", "admin"])
        ).filter(User.email.isnot(None)).all()
        
        if not security_users:
            logger.warning(f"⚠️ Не найдено сотрудников СБ с email для уведомления о проверке исполнителя {contractor_id}")
            return
        
        # Формируем ссылку на страницу проверки
        base_url = "http://91.222.236.58:3000"
        verification_url = f"{base_url}/security-verification/{contractor_id}"
        
        # Отправляем уведомление каждому сотруднику СБ
        for security_user in security_users:
            if security_user.email:
                subject = f"Новый исполнитель ожидает проверки СБ - {contractor_name}"
                message_html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #1976d2;">Новый исполнитель ожидает проверки СБ</h2>
                        <p>В системе появился новый исполнитель, который заполнил профиль и готов к проверке службой безопасности.</p>
                        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p><strong>Исполнитель:</strong> {contractor_name}</p>
                            <p><strong>Email:</strong> {user.email}</p>
                            <p><strong>Телефон:</strong> {contractor.phone or 'не указан'}</p>
                        </div>
                        <p style="margin-top: 30px;">
                            <a href="{verification_url}" style="background: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Перейти к проверке
                            </a>
                        </p>
                        <p style="color: #666; font-size: 12px; margin-top: 30px;">
                            Если кнопка не работает, скопируйте ссылку: {verification_url}
                        </p>
                    </div>
                </body>
                </html>
                """
                
                message_text = f"""
Новый исполнитель ожидает проверки СБ

Исполнитель: {contractor_name}
Email: {user.email}
Телефон: {contractor.phone or 'не указан'}

Ссылка на проверку: {verification_url}
                """
                
                await email_service.send_notification_email(
                    user_email=security_user.email,
                    subject=subject,
                    message=message_html
                )
                logger.info(f"📧 Уведомление отправлено сотруднику СБ {security_user.email} о проверке исполнителя {contractor_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки уведомления сотрудникам СБ: {e}")

async def send_verification_notification_to_managers(contractor_id: int, db: Session):
    """Отправка email уведомления менеджерам"""
    try:
        from services.email_service import email_service
        
        # Получаем информацию об исполнителе
        contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
        if not contractor:
            return
        
        user = db.query(User).filter(User.id == contractor.user_id).first()
        if not user:
            return
        
        contractor_name = f"{contractor.first_name or ''} {contractor.last_name or ''}".strip() or user.username
        
        # Получаем всех менеджеров и админов
        manager_users = db.query(User).filter(
            User.role.in_(["manager", "admin"])
        ).filter(User.email.isnot(None)).all()
        
        if not manager_users:
            logger.warning(f"⚠️ Не найдено менеджеров с email для уведомления о проверке исполнителя {contractor_id}")
            return
        
        # Формируем ссылку на страницу проверки
        base_url = "http://91.222.236.58:3000"
        verification_url = f"{base_url}/manager/verification/{contractor_id}"
        
        # Отправляем уведомление каждому менеджеру
        for manager_user in manager_users:
            if manager_user.email:
                subject = f"Исполнитель прошел проверку СБ и ожидает одобрения - {contractor_name}"
                message_html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #1976d2;">Исполнитель ожидает одобрения менеджера</h2>
                        <p>Исполнитель прошел проверку службой безопасности и готов к одобрению менеджером.</p>
                        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p><strong>Исполнитель:</strong> {contractor_name}</p>
                            <p><strong>Email:</strong> {user.email}</p>
                            <p><strong>Телефон:</strong> {contractor.phone or 'не указан'}</p>
                            <p><strong>Специализации:</strong> {', '.join([s.get('specialization', '') if isinstance(s, dict) else str(s) for s in contractor.specializations]) if contractor.specializations and isinstance(contractor.specializations, list) else 'не указаны'}</p>
                        </div>
                        <p style="margin-top: 30px;">
                            <a href="{verification_url}" style="background: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Перейти к проверке
                            </a>
                        </p>
                        <p style="color: #666; font-size: 12px; margin-top: 30px;">
                            Если кнопка не работает, скопируйте ссылку: {verification_url}
                        </p>
                    </div>
                </body>
                </html>
                """
                
                message_text = f"""
Исполнитель ожидает одобрения менеджера

Исполнитель: {contractor_name}
Email: {user.email}
Телефон: {contractor.phone or 'не указан'}

Ссылка на проверку: {verification_url}
                """
                
                await email_service.send_notification_email(
                    user_email=manager_user.email,
                    subject=subject,
                    message=message_html
                )
                logger.info(f"📧 Уведомление отправлено менеджеру {manager_user.email} о проверке исполнителя {contractor_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки уведомления менеджерам: {e}")

async def send_security_approval_email(contractor_id: int, db: Session, notes: Optional[str] = None):
    """Отправляет email уведомление об одобрении СБ"""
    try:
        from services.email_service import email_service
        
        contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
        if not contractor:
            return
        
        user = db.query(User).filter(User.id == contractor.user_id).first()
        if not user or not user.email:
            return
        
        contractor_name = f"{contractor.first_name or ''} {contractor.last_name or ''}".strip() or user.username
        base_url = os.getenv("FRONTEND_URL", "http://91.222.236.58:3000")
        dashboard_url = f"{base_url}/contractor/dashboard"
        
        subject = f"Ваш профиль активен - Добро пожаловать!"
        message_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2e7d32;">Ваш профиль успешно проверен и активирован!</h2>
                <p>Здравствуйте, {contractor_name}!</p>
                <p>Поздравляем! Ваш профиль прошел проверку службой безопасности и теперь активен.</p>
                <div style="background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #2e7d32;">
                    <p><strong>Что это означает:</strong></p>
                    <ul>
                        <li>Вы можете просматривать доступные заявки</li>
                        <li>Вы можете откликаться на заявки</li>
                        <li>Ваш профиль виден менеджерам и заказчикам</li>
                    </ul>
                </div>
                <p style="margin-top: 30px;">
                    <a href="{dashboard_url}" style="background: #2e7d32; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Перейти к заявкам
                    </a>
                </p>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Если кнопка не работает, скопируйте ссылку: {dashboard_url}
                </p>
            </div>
        </body>
        </html>
        """
        
        await email_service.send_notification_email(
            user_email=user.email,
            subject=subject,
            message=message_html
        )
        logger.info(f"📧 Email об одобрении СБ отправлен исполнителю {contractor_id} ({user.email})")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки email об одобрении СБ: {e}")

async def send_security_rejection_email(contractor_id: int, db: Session, reason: Optional[str] = None):
    """Отправляет email уведомление об отклонении СБ"""
    try:
        from services.email_service import email_service
        
        contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
        if not contractor:
            return
        
        user = db.query(User).filter(User.id == contractor.user_id).first()
        if not user or not user.email:
            return
        
        contractor_name = f"{contractor.first_name or ''} {contractor.last_name or ''}".strip() or user.username
        
        subject = f"Результат проверки профиля"
        message_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #d32f2f;">Результат проверки профиля</h2>
                <p>Здравствуйте, {contractor_name}!</p>
                <p>Спасибо за интерес, проявленный к нашей платформе.</p>
                <p>К сожалению, после проверки службой безопасности мы не готовы продолжить работу с Вами на данный момент.</p>
                {f'<div style="background: #ffebee; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #d32f2f;"><p><strong>Причина:</strong> {reason}</p></div>' if reason else ''}
                <p>Если у Вас возникнут вопросы, пожалуйста, свяжитесь с нашей службой поддержки.</p>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    С уважением,<br>
                    Команда платформы
                </p>
            </div>
        </body>
        </html>
        """
        
        await email_service.send_notification_email(
            user_email=user.email,
            subject=subject,
            message=message_html
        )
        logger.info(f"📧 Email об отклонении СБ отправлен исполнителю {contractor_id} ({user.email})")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки email об отклонении СБ: {e}")

async def send_clarification_request_email(contractor_id: int, db: Session, notes: str):
    """Отправляет email с запросом на уточнение данных"""
    try:
        from services.email_service import email_service
        
        contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
        if not contractor:
            return
        
        user = db.query(User).filter(User.id == contractor.user_id).first()
        if not user or not user.email:
            return
        
        contractor_name = f"{contractor.first_name or ''} {contractor.last_name or ''}".strip() or user.username
        base_url = os.getenv("FRONTEND_URL", "http://91.222.236.58:3000")
        profile_url = f"{base_url}/contractor/profile"
        
        subject = f"Требуется уточнение данных профиля"
        message_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #ed6c02;">Требуется уточнение данных</h2>
                <p>Здравствуйте, {contractor_name}!</p>
                <p>Для завершения проверки вашего профиля службой безопасности необходимо дополнить следующие данные:</p>
                <div style="background: #fff3e0; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ed6c02;">
                    <p>{notes}</p>
                </div>
                <p style="margin-top: 30px;">
                    <a href="{profile_url}" style="background: #ed6c02; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Перейти к профилю
                    </a>
                </p>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Если кнопка не работает, скопируйте ссылку: {profile_url}
                </p>
            </div>
        </body>
        </html>
        """
        
        await email_service.send_notification_email(
            user_email=user.email,
            subject=subject,
            message=message_html
        )
        logger.info(f"📧 Email с запросом уточнения данных отправлен исполнителю {contractor_id} ({user.email})")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки email с запросом уточнения: {e}")

async def update_overall_verification_status(contractor_id: int, db: Session):
    """Обновляет общий статус верификации исполнителя"""
    
    verification = db.query(ContractorVerification).filter(
        ContractorVerification.contractor_id == contractor_id
    ).first()
    
    if not verification:
        return
    
    # Сохраняем предыдущий статус для определения изменений
    previous_status = verification.overall_status
    
    # Определяем общий статус
    if not verification.profile_completed or not verification.documents_uploaded:
        overall_status = VerificationStatus.INCOMPLETE
    elif not verification.security_check_passed:
        overall_status = VerificationStatus.PENDING_SECURITY
    elif not verification.manager_approval:
        overall_status = VerificationStatus.PENDING_MANAGER
    elif verification.security_check_passed and verification.manager_approval:
        overall_status = VerificationStatus.APPROVED
    else:
        overall_status = VerificationStatus.INCOMPLETE
    
    verification.overall_status = overall_status
    
    # Обновляем статус в профиле
    contractor = db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first()
    if contractor:
        contractor.profile_completion_status = overall_status
    
    # Отправляем уведомления при переходе статуса на проверку
    if previous_status != overall_status:
        if overall_status == VerificationStatus.PENDING_SECURITY:
            # Отправляем уведомление сотрудникам СБ
            await send_verification_notification_to_security(contractor_id, db)
        elif overall_status == VerificationStatus.PENDING_MANAGER:
            # Отправляем уведомление менеджерам
            await send_verification_notification_to_managers(contractor_id, db)
