from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import re
from datetime import datetime

from database import get_db
from models import CustomerProfile, User, RepairRequest, ContractorResponse
from ..schemas import (
    CustomerProfileCreate, 
    CustomerProfileResponse,
    UserCreate,
    UserResponse
)
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/profiles", response_model=List[CustomerProfileResponse])
def get_all_customer_profiles(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех профилей заказчиков (только для администраторов и менеджеров)"""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам и менеджерам"
        )
    
    profiles = db.query(CustomerProfile).offset(offset).limit(limit).all()
    
    # Безопасная сериализация с дефолтными значениями для неполных профилей
    safe_profiles = []
    for p in profiles:
        # Заполняем обязательные поля дефолтными значениями если они пустые
        company_name = p.company_name if p.company_name and len(p.company_name.strip()) >= 1 else "Не указано"
        contact_person = p.contact_person if p.contact_person and len(p.contact_person.strip()) >= 1 else "Не указано"
        phone = p.phone if p.phone and len(p.phone) >= 10 else "0000000000"
        email = p.email if p.email else "unknown@example.com"
        
        safe_profiles.append({
            "id": p.id,
            "user_id": p.user_id,
            "company_name": company_name,
            "contact_person": contact_person,
            "phone": phone,
            "email": email,
            "address": p.address or "",
            "inn": p.inn or "",
            "kpp": p.kpp or "",
            "ogrn": p.ogrn or "",
            "equipment_brands": p.equipment_brands if isinstance(p.equipment_brands, list) else [],
            "equipment_types": p.equipment_types if isinstance(p.equipment_types, list) else [],
            "mining_operations": p.mining_operations if isinstance(p.mining_operations, list) else [],
            "service_history": p.service_history or "",
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        })
    
    return [CustomerProfileResponse(**prof) for prof in safe_profiles]

@router.post("/register", response_model=UserResponse)
def register_customer(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового заказчика"""
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
            "customer",
            True,
            False,
            "NOW()"
        ]).fetchone()
        
        user_id = result[0]
        
        # Создаем профиль заказчика
        profile_query = """
            INSERT INTO customer_profiles (user_id, company_name, contact_person, phone, email, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        db.execute(text(profile_query), [
            user_id,
            user_data.first_name or "Компания",  # Используем имя как название компании
            user_data.first_name or "Контактное лицо",
            user_data.phone or "",
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
        print(f"Ошибка в register_customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при регистрации заказчика: {str(e)}"
        )

@router.get("/profile", response_model=CustomerProfileResponse)
def get_customer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение профиля заказчика"""
    try:
        if current_user.role != "customer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )
        
        profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль заказчика не найден"
            )
        
        # Безопасные значения для соответствия схеме
        company_name = profile.company_name if profile.company_name and len(profile.company_name.strip()) >= 1 else "Не указано"
        contact_person = profile.contact_person if profile.contact_person and len(profile.contact_person.strip()) >= 1 else "Не указано"
        phone = profile.phone if profile.phone and len(profile.phone) >= 10 else "0000000000"
        email = profile.email if profile.email else (current_user.email or "unknown@example.com")
        
        profile_dict = {
            "id": profile.id,
            "user_id": profile.user_id,
            "company_name": company_name,
            "contact_person": contact_person,
            "phone": phone,
            "email": email,
            "address": profile.address or "",
            "inn": profile.inn or "",
            "kpp": profile.kpp or "",
            "ogrn": profile.ogrn or "",
            "equipment_brands": profile.equipment_brands if isinstance(profile.equipment_brands, list) else [],
            "equipment_types": profile.equipment_types if isinstance(profile.equipment_types, list) else [],
            "mining_operations": profile.mining_operations if isinstance(profile.mining_operations, list) else [],
            "service_history": profile.service_history or "",
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }
        
        return CustomerProfileResponse(**profile_dict)
        
    except Exception as e:
        print(f"Ошибка в get_customer_profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении профиля: {str(e)}"
        )

@router.put("/profile", response_model=CustomerProfileResponse)
def update_customer_profile(
    profile_data: CustomerProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление профиля заказчика (ORM, безопасная валидация)."""
    try:
        if current_user.role != "customer":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")

        profile: Optional[CustomerProfile] = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Профиль заказчика не найден")

        # Телефон: принимаем только цифры, нормализуем к формату +7 (XXX) XXX - XX - XX
        def normalize_phone_ru(raw: str) -> str:
            digits = re.sub(r"\D", "", raw or "")
            if not digits:
                return ""
            # допускаем 10 (без кода страны), 11 (7/8 + 10)
            if len(digits) == 10:
                digits = "7" + digits
            elif len(digits) == 11 and digits[0] == "8":
                digits = "7" + digits[1:]
            if len(digits) != 11 or digits[0] != "7":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Телефон должен содержать 10-11 цифр РФ. Пример: +7 (929) 544 - 03 - 02"
                )
            a, b, c, d, e = digits[1:4], digits[4:7], digits[7:9], digits[9:11][:2], digits[9:11][2:]
            # формируем +7 (AAA) BBB - CC - DD
            return f"+7 ({a}) {b} - {digits[7:9]} - {digits[9:11]}"

        if profile_data.phone is not None:
            profile.phone = normalize_phone_ru(profile_data.phone)

        # Присваиваем скалярные поля если переданы
        if profile_data.company_name is not None:
            profile.company_name = profile_data.company_name
        if profile_data.contact_person is not None:
            profile.contact_person = profile_data.contact_person
        if profile_data.email is not None:
            profile.email = profile_data.email
        if profile_data.address is not None:
            profile.address = profile_data.address
        # Валидация ИНН, КПП, ОГРН
        if profile_data.inn is not None:
            inn_value = str(profile_data.inn).strip() if profile_data.inn else ""
            if inn_value:
                # Извлекаем только цифры
                inn_digits = re.sub(r"\D", "", inn_value)
                if len(inn_digits) not in [10, 12]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="ИНН должен содержать 10 (для ЮЛ) или 12 (для ИП) цифр"
                    )
                profile.inn = inn_digits
            else:
                profile.inn = None
        
        if profile_data.kpp is not None:
            kpp_value = str(profile_data.kpp).strip() if profile_data.kpp else ""
            if kpp_value:
                # Извлекаем только цифры
                kpp_digits = re.sub(r"\D", "", kpp_value)
                if len(kpp_digits) != 9:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="КПП должен содержать 9 цифр"
                    )
                profile.kpp = kpp_digits
            else:
                profile.kpp = None
        
        if profile_data.ogrn is not None:
            ogrn_value = str(profile_data.ogrn).strip() if profile_data.ogrn else ""
            if ogrn_value:
                # Извлекаем только цифры
                ogrn_digits = re.sub(r"\D", "", ogrn_value)
                if len(ogrn_digits) not in [13, 15]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="ОГРН должен содержать 13 (для ЮЛ) или 15 (для ИП) цифр"
                    )
                profile.ogrn = ogrn_digits
            else:
                profile.ogrn = None

        # Поля-списки: гарантируем массивы строк (JSON)
        def ensure_str_list(value):
            if value is None:
                return None
            if isinstance(value, list):
                return [str(v) for v in value]
            # если пришла строка через форму
            return [str(value)]

        eb = ensure_str_list(getattr(profile_data, "equipment_brands", None))
        et = ensure_str_list(getattr(profile_data, "equipment_types", None))
        mo = ensure_str_list(getattr(profile_data, "mining_operations", None))
        if eb is not None:
            profile.equipment_brands = eb
        if et is not None:
            profile.equipment_types = et
        if mo is not None:
            profile.mining_operations = mo

        # Прочее
        if getattr(profile_data, "service_history", None) is not None:
            profile.service_history = profile_data.service_history or ""

        profile.updated_at = datetime.utcnow()

        db.add(profile)
        db.commit()
        db.refresh(profile)

        # Возвращаем актуальные данные
        return get_customer_profile(current_user, db)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Ошибка в update_customer_profile: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при обновлении профиля: {str(e)}")

@router.get("/requests", response_model=List[dict])
def get_customer_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Получение заявок заказчика"""
    try:
        if current_user.role != "customer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )
        
        # Получаем профиль заказчика
        customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
        
        if not customer_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль заказчика не найден"
            )
        
        # Получаем заявки через ORM
        requests_query = db.query(RepairRequest).filter(RepairRequest.customer_id == customer_profile.id)
        requests = requests_query.order_by(RepairRequest.created_at.desc()).offset(skip).limit(limit).all()
        
        requests_list = []
        for request in requests:
            # Получаем количество откликов
            responses_count = db.query(ContractorResponse).filter(ContractorResponse.request_id == request.id).count()
            
            request_dict = {
                "id": request.id,
                "title": request.title,
                "description": request.description,
                "urgency": request.urgency,
                "preferred_date": request.preferred_date.isoformat() if request.preferred_date else None,
                "address": request.address,
                "city": request.city,
                "region": request.region,
                "status": request.status,
                "created_at": request.created_at.isoformat() if request.created_at else None,
                "updated_at": request.updated_at.isoformat() if request.updated_at else None,
                "processed_at": request.processed_at.isoformat() if request.processed_at else None,
                "assigned_at": request.assigned_at.isoformat() if request.assigned_at else None,
                "responses_count": responses_count
            }
            requests_list.append(request_dict)
        
        return requests_list
        
    except Exception as e:
        print(f"Ошибка в get_customer_requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении заявок: {str(e)}"
        )
