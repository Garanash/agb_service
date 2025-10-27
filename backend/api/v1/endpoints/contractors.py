from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pathlib import Path
import os
import json

from database import get_db
from models import ContractorProfile, User
from ..schemas import (
    ContractorProfileCreate, 
    ContractorProfileResponse,
    UserCreate,
    UserResponse
)
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/profiles", response_model=List[ContractorProfileResponse])
def get_all_contractor_profiles(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех профилей исполнителей (только для администраторов и менеджеров)"""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам и менеджерам"
        )
    
    profiles = db.query(ContractorProfile).offset(offset).limit(limit).all()
    return profiles

# Настройки загрузки файлов
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/register", response_model=UserResponse)
def register_contractor(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового исполнителя"""
    try:
        # Проверяем, что пользователь с таким username не существует
        existing_user = db.execute(text("SELECT id FROM users WHERE username = %s"), [user_data.username]).fetchone()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует"
            )
        
        # Проверяем, что пользователь с таким email не существует
        existing_email = db.execute(text("SELECT id FROM users WHERE email = %s"), [user_data.email]).fetchone()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Создаем пользователя
        from ..dependencies import get_password_hash
        
        hashed_password = get_password_hash(user_data.password)
        
        user_query = """
            INSERT INTO users (username, email, hashed_password, first_name, last_name, middle_name, 
                             phone, position, role, is_active, is_password_changed, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        result = db.execute(text(user_query), [
            user_data.username,
            user_data.email,
            hashed_password,
            user_data.first_name,
            user_data.last_name,
            user_data.middle_name,
            user_data.phone,
            user_data.position,
            "contractor",
            True,
            False,
            "NOW()"
        ]).fetchone()
        
        user_id = result[0]
        
        # Создаем профиль исполнителя
        profile_query = """
            INSERT INTO contractor_profiles (user_id, last_name, first_name, patronymic, phone, email, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        db.execute(text(profile_query), [
            user_id,
            user_data.last_name,
            user_data.first_name,
            user_data.middle_name,
            user_data.phone,
            user_data.email,
            "NOW()"
        ])
        
        db.commit()
        
        # Возвращаем созданного пользователя
        user_query = """
            SELECT id, username, email, first_name, last_name, middle_name, phone, position, 
                   role, is_active, is_password_changed, avatar_url, created_at, updated_at
            FROM users WHERE id = %s
        """
        
        user_result = db.execute(text(user_query), [user_id]).fetchone()
        
        user_dict = {
            "id": user_result[0],
            "username": user_result[1],
            "email": user_result[2],
            "first_name": user_result[3],
            "last_name": user_result[4],
            "middle_name": user_result[5],
            "phone": user_result[6],
            "position": user_result[7],
            "role": user_result[8],
            "is_active": user_result[9],
            "is_password_changed": user_result[10],
            "avatar_url": user_result[11],
            "created_at": user_result[12].isoformat() if user_result[12] else None,
            "updated_at": user_result[13].isoformat() if user_result[13] else None
        }
        
        return user_dict
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка в register_contractor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при регистрации исполнителя: {str(e)}"
        )

@router.get("/profile", response_model=ContractorProfileResponse)
def get_contractor_profile(
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
        
        query = """
            SELECT id, user_id, last_name, first_name, patronymic, phone, email,
                   professional_info, bank_name, bank_account, bank_bik,
                   telegram_username, website, general_description, profile_photo_path,
                   specializations, equipment_brands_experience, certifications, work_regions,
                   created_at, updated_at
            FROM contractor_profiles
            WHERE user_id = :user_id
        """
        
        result = db.execute(text(query), {"user_id": current_user.id}).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль исполнителя не найден"
            )
        
        profile_dict = {
            "id": result[0],
            "user_id": result[1],
            "last_name": result[2],
            "first_name": result[3],
            "patronymic": result[4],
            "phone": result[5],
            "email": result[6],
            "professional_info": result[7] if result[7] and isinstance(result[7], list) else [],
            "bank_name": result[8],
            "bank_account": result[9],
            "bank_bik": result[10],
            "telegram_username": result[11],
            "website": result[12],
            "general_description": result[13],
            "profile_photo_path": result[14],
            "specializations": result[15] if result[15] else [],
            "equipment_brands_experience": result[16] if result[16] else [],
            "certifications": result[17] if result[17] else [],
            "work_regions": result[18] if result[18] else [],
            "created_at": result[19].isoformat() if result[19] else None,
            "updated_at": result[20].isoformat() if result[20] else None
        }
        
        return profile_dict
        
    except Exception as e:
        print(f"Ошибка в get_contractor_profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении профиля: {str(e)}"
        )

@router.put("/profile", response_model=ContractorProfileResponse)
def update_contractor_profile(
    profile_data: ContractorProfileCreate,
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
        
        # Проверяем, что профиль существует
        profile_query = "SELECT id FROM contractor_profiles WHERE user_id = :user_id"
        profile_result = db.execute(text(profile_query), {"user_id": current_user.id}).fetchone()
        
        if not profile_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль исполнителя не найден"
            )
        
        # Строим запрос обновления
        update_fields = []
        params = []
        
        if profile_data.last_name is not None:
            update_fields.append("last_name = %s")
            params.append(profile_data.last_name)
        
        if profile_data.first_name is not None:
            update_fields.append("first_name = %s")
            params.append(profile_data.first_name)
        
        if profile_data.patronymic is not None:
            update_fields.append("patronymic = %s")
            params.append(profile_data.patronymic)
        
        if profile_data.phone is not None:
            update_fields.append("phone = %s")
            params.append(profile_data.phone)
        
        if profile_data.email is not None:
            update_fields.append("email = %s")
            params.append(profile_data.email)
        
        if profile_data.professional_info is not None:
            update_fields.append("professional_info = %s")
            params.append(json.dumps(profile_data.professional_info))
        
        if profile_data.education is not None:
            update_fields.append("education = %s")
            params.append(json.dumps(profile_data.education))
        
        if profile_data.bank_name is not None:
            update_fields.append("bank_name = %s")
            params.append(profile_data.bank_name)
        
        if profile_data.bank_account is not None:
            update_fields.append("bank_account = %s")
            params.append(profile_data.bank_account)
        
        if profile_data.bank_bik is not None:
            update_fields.append("bank_bik = %s")
            params.append(profile_data.bank_bik)
        
        if profile_data.telegram_username is not None:
            update_fields.append("telegram_username = %s")
            params.append(profile_data.telegram_username)
        
        if profile_data.website is not None:
            update_fields.append("website = %s")
            params.append(profile_data.website)
        
        if profile_data.general_description is not None:
            update_fields.append("general_description = %s")
            params.append(profile_data.general_description)
        
        if profile_data.profile_photo_path is not None:
            update_fields.append("profile_photo_path = %s")
            params.append(profile_data.profile_photo_path)
        
        if profile_data.portfolio_files is not None:
            update_fields.append("portfolio_files = %s")
            params.append(json.dumps(profile_data.portfolio_files))
        
        if profile_data.document_files is not None:
            update_fields.append("document_files = %s")
            params.append(json.dumps(profile_data.document_files))
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет данных для обновления"
            )
        
        update_query = f"""
            UPDATE contractor_profiles 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE user_id = :user_id
        """
        
        params.append(current_user.id)
        db.execute(text(update_query), dict(zip(range(len(params)), params)) | {"user_id": current_user.id})
        db.commit()
        
        # Возвращаем обновленный профиль
        return get_contractor_profile(current_user, db)
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка в update_contractor_profile: {e}")
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
        current_files = json.loads(result[0]) if result[0] else []
        
        # Добавляем новый файл
        file_info = {
            "filename": file.filename,
            "path": str(file_path.relative_to(UPLOAD_DIR)),
            "size": len(file_content),
            "uploaded_at": "NOW()"
        }
        current_files.append(file_info)
        
        # Обновляем профиль
        update_query = f"""
            UPDATE contractor_profiles 
            SET {file_type}_files = %s, updated_at = %s
            WHERE user_id = %s
        """
        
        db.execute(text(update_query), [
            json.dumps(current_files),
            "NOW()",
            current_user.id
        ])
        db.commit()
        
        return {
            "message": "Файл успешно загружен",
            "file_info": file_info
        }
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка в upload_file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )

@router.get("/telegram-link")
def get_telegram_link(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение ссылки для подключения Telegram бота"""
    try:
        if current_user.role not in ["contractor", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )
        
        # Здесь должна быть логика генерации ссылки для Telegram бота
        # Пока возвращаем заглушку
        bot_username = "agregator_service_bot"  # Замените на реальное имя бота
        
        return {
            "telegram_link": f"https://t.me/{bot_username}?start={current_user.id}",
            "bot_username": bot_username,
            "instructions": "Перейдите по ссылке и отправьте команду /start для подключения уведомлений"
        }
        
    except Exception as e:
        print(f"Ошибка в get_telegram_link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении ссылки: {str(e)}"
        )
