from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pathlib import Path
from datetime import datetime, date
import os
import json
import logging

from database import get_db
from models import ContractorProfile, User

logger = logging.getLogger(__name__)
from ..schemas import (
    ContractorProfileCreate, 
    ContractorProfileResponse,
    UserCreate,
    UserResponse
)
from ..dependencies import get_current_user
from pathlib import Path as PathLib

router = APIRouter()

# Константы
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/register", response_model=UserResponse)
def register_contractor(
    contractor_data: ContractorProfileCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового исполнителя"""
    try:
        # Проверяем, существует ли пользователь
        existing_user = db.query(User).filter(User.username == contractor_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует"
            )
        
        # Проверяем email
        existing_email = db.query(User).filter(User.email == contractor_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Создаем пользователя
        user = User(
            username=contractor_data.username,
            email=contractor_data.email,
            password_hash=contractor_data.password,  # В реальности здесь должен быть хеш
            role="contractor"
        )
        db.add(user)
        db.flush()  # Получаем user.id
        
        # Создаем профиль исполнителя
        contractor_profile = ContractorProfile(
            user_id=user.id,
            last_name=contractor_data.last_name,
            first_name=contractor_data.first_name,
            patronymic=contractor_data.patronymic,
            phone=contractor_data.phone,
            email=contractor_data.email,
            professional_info=contractor_data.professional_info if contractor_data.professional_info else [],
            bank_name=contractor_data.bank_name,
            bank_account=contractor_data.bank_account,
            bank_bik=contractor_data.bank_bik,
            telegram_username=contractor_data.telegram_username,
            website=contractor_data.website,
            general_description=contractor_data.general_description,
            specializations=contractor_data.specializations if contractor_data.specializations else [],
            equipment_brands_experience=contractor_data.equipment_brands_experience if contractor_data.equipment_brands_experience else [],
            certifications=contractor_data.certifications if contractor_data.certifications else [],
            work_regions=contractor_data.work_regions if contractor_data.work_regions else [],
            hourly_rate=contractor_data.hourly_rate
        )
        db.add(contractor_profile)
        db.commit()
        db.refresh(user)
        db.refresh(contractor_profile)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при регистрации исполнителя: {str(e)}"
        )

@router.get("/profile", response_model=ContractorProfileResponse)
async def get_contractor_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение профиля исполнителя"""
    try:
        if current_user.role not in ["contractor", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )
        
        # Используем ORM для надежности
        profile = db.query(ContractorProfile).filter(ContractorProfile.user_id == current_user.id).first()
        
        if not profile:
            # Автоматически создаем профиль, если его нет у исполнителя
            if current_user.role == "contractor":
                profile = ContractorProfile(
                    user_id=current_user.id,
                    first_name=current_user.first_name,
                    last_name=current_user.last_name,
                    phone=current_user.phone,
                    email=current_user.email,
                    profile_completion_status="incomplete"
                )
                db.add(profile)
                db.commit()
                db.refresh(profile)
                logger.info(f"✅ Автоматически создан профиль для исполнителя user_id={current_user.id}")
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Профиль исполнителя не найден"
                )
        
        # Формируем словарь из модели
        profile_dict = {
            "id": profile.id,
            "user_id": profile.user_id,
            "last_name": profile.last_name,
            "first_name": profile.first_name,
            "patronymic": profile.patronymic,
            "phone": profile.phone,
            "email": profile.email,
            "passport_series": profile.passport_series,
            "passport_number": profile.passport_number,
            "passport_issued_by": profile.passport_issued_by,
            "passport_issued_date": profile.passport_issued_date.isoformat() if profile.passport_issued_date and isinstance(profile.passport_issued_date, (datetime, date)) else (str(profile.passport_issued_date) if profile.passport_issued_date else None),
            "passport_issued_code": profile.passport_issued_code,
            "birth_date": profile.birth_date.isoformat() if profile.birth_date and isinstance(profile.birth_date, (datetime, date)) else (str(profile.birth_date) if profile.birth_date else None),
            "birth_place": profile.birth_place,
            "inn": profile.inn,
            "professional_info": profile.professional_info if profile.professional_info and isinstance(profile.professional_info, list) else [],
            "bank_name": profile.bank_name,
            "bank_account": profile.bank_account,
            "bank_bik": profile.bank_bik,
            "telegram_username": profile.telegram_username,
            "website": profile.website,
            "general_description": profile.general_description,
            "profile_photo_path": profile.profile_photo_path,
            "specializations": profile.specializations if profile.specializations and isinstance(profile.specializations, list) else [],
            "equipment_brands_experience": profile.equipment_brands_experience if profile.equipment_brands_experience else [],
            "certifications": profile.certifications if profile.certifications else [],
            "work_regions": profile.work_regions if profile.work_regions else [],
            "hourly_rate": float(profile.hourly_rate) if profile.hourly_rate is not None else None,
            "created_at": profile.created_at.isoformat() if profile.created_at and isinstance(profile.created_at, (datetime, date)) else (str(profile.created_at) if profile.created_at else None),
            "updated_at": profile.updated_at.isoformat() if profile.updated_at and isinstance(profile.updated_at, (datetime, date)) else (str(profile.updated_at) if profile.updated_at else None)
        }
        
        return profile_dict
        
    except Exception as e:
        print(f"Ошибка в get_contractor_profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении профиля: {str(e)}"
        )

@router.put("/profile", response_model=ContractorProfileResponse)
async def update_contractor_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление профиля исполнителя"""
    try:
        if current_user.role not in ["contractor", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )

        profile = db.query(ContractorProfile).filter(ContractorProfile.user_id == current_user.id).first()

        if not profile:
            # Автоматически создаем профиль, если его нет у исполнителя
            if current_user.role == "contractor":
                profile = ContractorProfile(
                    user_id=current_user.id,
                    first_name=current_user.first_name,
                    last_name=current_user.last_name,
                    phone=current_user.phone,
                    email=current_user.email,
                    profile_completion_status="incomplete"
                )
                db.add(profile)
                db.commit()
                db.refresh(profile)
                logger.info(f"✅ Автоматически создан профиль для исполнителя user_id={current_user.id} при обновлении")
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Профиль исполнителя не найден"
                )
        
        # Валидация паспортных данных
        if 'passport_series' in profile_data and profile_data['passport_series']:
            if not profile_data['passport_series'].isdigit() or len(profile_data['passport_series']) != 4:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Серия паспорта должна состоять из 4 цифр"
                )
        
        if 'passport_number' in profile_data and profile_data['passport_number']:
            if not profile_data['passport_number'].isdigit() or len(profile_data['passport_number']) != 6:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Номер паспорта должен состоять из 6 цифр"
                )
        
        if 'passport_issued_code' in profile_data and profile_data['passport_issued_code']:
            if not profile_data['passport_issued_code'].isdigit() or len(profile_data['passport_issued_code']) != 6:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Код подразделения должен состоять из 6 цифр"
                )
        
        # Обрабатываем hourly_rate - убеждаемся что это число
        if 'hourly_rate' in profile_data and profile_data['hourly_rate'] is not None:
            try:
                if isinstance(profile_data['hourly_rate'], str):
                    profile_data['hourly_rate'] = float(profile_data['hourly_rate'])
                elif not isinstance(profile_data['hourly_rate'], (int, float)):
                    raise ValueError("hourly_rate должен быть числом")
                if profile_data['hourly_rate'] < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Почасовая ставка не может быть отрицательной"
                    )
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Почасовая ставка должна быть числом"
                )
        
        # Обновляем поля напрямую через ORM
        from datetime import datetime
        for field, value in profile_data.items():
            if hasattr(profile, field) and value is not None:
                # Для JSON полей значения уже должны быть в правильном формате
                setattr(profile, field, value)
        
        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        
        # Проверяем полноту профиля и обновляем статус верификации
        try:
            from api.v1.endpoints.contractor_verification import check_profile_completion
            await check_profile_completion(profile.id, db)
            db.commit()
        except Exception as e:
            print(f"Ошибка при проверке полноты профиля: {e}")
            # Не прерываем сохранение профиля из-за ошибки проверки
        
        # Возвращаем обновленный профиль
        return await get_contractor_profile(current_user, db)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Ошибка в update_contractor_profile: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении профиля: {str(e)}"
        )

@router.post("/upload-file")
def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form(...),  # "portfolio" или "document"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Загрузка файла для профиля исполнителя"""
    try:
        if current_user.role not in ["contractor", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )
        
        if file_type not in ["portfolio", "document"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный тип файла"
            )
        
        # Проверяем размер файла
        file_content = file.file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл слишком большой"
            )
        
        # Создаем директорию для файлов
        file_dir = UPLOAD_DIR / file_type
        file_dir.mkdir(exist_ok=True)
        
        # Генерируем уникальное имя файла
        file_extension = Path(file.filename).suffix
        file_name = f"{current_user.id}_{file.filename}"
        file_path = file_dir / file_name
        
        # Сохраняем файл
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Обновляем профиль исполнителя
        profile_query = f"""
            SELECT {file_type}_files FROM contractor_profiles WHERE user_id = %s
        """
        
        result = db.execute(text(profile_query), [current_user.id]).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль исполнителя не найден"
            )
        
        # Получаем текущий список файлов
        current_files = result[0] or []
        if not isinstance(current_files, list):
            current_files = []
        
        # Добавляем новый файл
        file_url = f"/uploads/{file_type}/{file_name}"
        current_files.append(file_url)
        
        # Обновляем профиль
        update_query = f"""
            UPDATE contractor_profiles 
            SET {file_type}_files = %s 
            WHERE user_id = %s
        """
        db.execute(text(update_query), [json.dumps(current_files), current_user.id])
        db.commit()
        
        return {"file_url": file_url, "message": "Файл успешно загружен"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Ошибка при загрузке файла: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )


@router.get("/profiles")
def list_contractor_profiles(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Список профилей исполнителей для админ-панели.
    Возвращает массив объектов `ContractorProfile`.
    """
    if limit < 1:
        limit = 20
    if offset < 0:
        offset = 0

    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")

    try:
        profiles = (
            db.query(ContractorProfile)
            .order_by(ContractorProfile.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        result = []
        for p in profiles:
            # Получаем расширенную верификацию, если она есть
            verification = db.query(text("select * from contractor_verifications where contractor_id=:cid")).params(cid=p.id).fetchone()
            verification_dict = {}
            if verification:
                verification_dict = {
                    "manager_approval": verification.manager_approval,
                    "security_check_passed": verification.security_check_passed,
                    "overall_status": str(getattr(verification, "overall_status", "")),
                    "security_notes": verification.security_notes,
                    "manager_notes": verification.manager_notes,
                    "security_checked_by": verification.security_checked_by,
                    "manager_checked_by": verification.manager_checked_by,
                    "security_checked_at": verification.security_checked_at.isoformat() if verification.security_checked_at else None,
                    "manager_checked_at": verification.manager_checked_at.isoformat() if verification.manager_checked_at else None,
                }
            result.append({
                "id": p.id,
                "user_id": p.user_id,
                "last_name": p.last_name or "",
                "first_name": p.first_name or "",
                "patronymic": p.patronymic or "",
                "phone": p.phone or "",
                "email": p.email or "",
                "professional_info": p.professional_info if isinstance(p.professional_info, list) else [],
                "education": p.education if isinstance(getattr(p, "education", None), list) else [],
                "bank_name": p.bank_name or "",
                "bank_account": p.bank_account or "",
                "bank_bik": p.bank_bik or "",
                "telegram_username": p.telegram_username or "",
                "website": p.website or "",
                "general_description": p.general_description or "",
                "profile_photo_path": p.profile_photo_path or "",
                "portfolio_files": p.portfolio_files if isinstance(p.portfolio_files, list) else [],
                "document_files": p.document_files if isinstance(p.document_files, list) else [],
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                "manager_verified": getattr(p, "manager_verified", False),
                "manager_verified_at": p.manager_verified_at.isoformat() if getattr(p, "manager_verified_at", None) else None,
                "manager_verified_by": getattr(p, "manager_verified_by", None),
                "profile_completion_status": getattr(p, "profile_completion_status", None),
                "security_verified": getattr(p, "security_verified", False),
                "security_verified_at": p.security_verified_at.isoformat() if getattr(p, "security_verified_at", None) else None,
                "security_verified_by": getattr(p, "security_verified_by", None),
                "verification": verification_dict
            })

        return result
    except Exception as e:
        print(f"Ошибка при получении списка исполнителей: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить список исполнителей"
        )
