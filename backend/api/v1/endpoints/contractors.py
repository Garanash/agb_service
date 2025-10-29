from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pathlib import Path
from datetime import datetime, date
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
        
        # Используем ORM для надежности
        profile = db.query(ContractorProfile).filter(ContractorProfile.user_id == current_user.id).first()
        
        if not profile:
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
            "specializations": profile.specializations if profile.specializations else [],
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
def update_contractor_profile(
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
        
        # Получаем профиль через ORM
        profile = db.query(ContractorProfile).filter(ContractorProfile.user_id == current_user.id).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль исполнителя не найден"
            )
        
        # Валидация паспортных данных
        if 'passport_series' in profile_data and profile_data['passport_series']:
            if not isinstance(profile_data['passport_series'], str) or not profile_data['passport_series'].isdigit() or len(profile_data['passport_series']) != 4:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Серия паспорта должна состоять из 4 цифр"
                )
        
        if 'passport_number' in profile_data and profile_data['passport_number']:
            if not isinstance(profile_data['passport_number'], str) or not profile_data['passport_number'].isdigit() or len(profile_data['passport_number']) != 6:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Номер паспорта должен состоять из 6 цифр"
                )
        
        if 'passport_issued_code' in profile_data and profile_data['passport_issued_code']:
            if not isinstance(profile_data['passport_issued_code'], str) or not profile_data['passport_issued_code'].isdigit() or len(profile_data['passport_issued_code']) != 6:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Код подразделения должен состоять из 6 цифр"
                )
        
        # Валидация ИНН
        if 'inn' in profile_data and profile_data['inn']:
            if not isinstance(profile_data['inn'], str) or not profile_data['inn'].isdigit() or len(profile_data['inn']) != 12:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ИНН должен состоять из 12 цифр"
                )
        
        # Валидация специализаций
        if 'specializations' in profile_data and profile_data['specializations'] is not None:
            valid_specializations = ['электрика', 'гидравлика', 'двс', 'агрегаты', 'перфораторы', 'другое']
            valid_levels = ['начальный', 'средний', 'продвинутый', 'эксперт']
            
            if not isinstance(profile_data['specializations'], list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Специализации должны быть списком"
                )
            
            for spec in profile_data['specializations']:
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
            except (ValueError, TypeError) as e:
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
        
        # Возвращаем обновленный профиль
        return get_contractor_profile(current_user, db)
        
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
