"""
API endpoints для системы верификации исполнителей
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
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
    
    # Создаем словарь из contractor, исключая поля которые передаются отдельно
    contractor_data = contractor.__dict__.copy()
    contractor_data.pop('education_records', None)
    contractor_data.pop('documents', None)
    
    return ContractorProfileExtended(
        **contractor_data,
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
    return verifications

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

async def update_overall_verification_status(contractor_id: int, db: Session):
    """Обновляет общий статус верификации исполнителя"""
    
    verification = db.query(ContractorVerification).filter(
        ContractorVerification.contractor_id == contractor_id
    ).first()
    
    if not verification:
        return
    
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
