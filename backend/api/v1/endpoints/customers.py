from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

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
    return profiles

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
        
        query = """
            SELECT id, user_id, company_name, contact_person, phone, email,
                   address, inn, kpp, ogrn, created_at, updated_at
            FROM customer_profiles
            WHERE user_id = %s
        """
        
        result = db.execute(text(query), [current_user.id]).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль заказчика не найден"
            )
        
        profile_dict = {
            "id": result[0],
            "user_id": result[1],
            "company_name": result[2],
            "contact_person": result[3],
            "phone": result[4],
            "email": result[5],
            "address": result[6],
            "inn": result[7],
            "kpp": result[8],
            "ogrn": result[9],
            "created_at": result[10].isoformat() if result[10] else None,
            "updated_at": result[11].isoformat() if result[11] else None
        }
        
        return profile_dict
        
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
    """Обновление профиля заказчика"""
    try:
        if current_user.role != "customer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )
        
        # Проверяем, что профиль существует
        profile_query = "SELECT id FROM customer_profiles WHERE user_id = %s"
        profile_result = db.execute(text(profile_query), [current_user.id]).fetchone()
        
        if not profile_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль заказчика не найден"
            )
        
        # Строим запрос обновления
        update_fields = []
        params = []
        
        if profile_data.company_name is not None:
            update_fields.append("company_name = %s")
            params.append(profile_data.company_name)
        
        if profile_data.contact_person is not None:
            update_fields.append("contact_person = %s")
            params.append(profile_data.contact_person)
        
        if profile_data.phone is not None:
            update_fields.append("phone = %s")
            params.append(profile_data.phone)
        
        if profile_data.email is not None:
            update_fields.append("email = %s")
            params.append(profile_data.email)
        
        if profile_data.address is not None:
            update_fields.append("address = %s")
            params.append(profile_data.address)
        
        if profile_data.inn is not None:
            update_fields.append("inn = %s")
            params.append(profile_data.inn)
        
        if profile_data.kpp is not None:
            update_fields.append("kpp = %s")
            params.append(profile_data.kpp)
        
        if profile_data.ogrn is not None:
            update_fields.append("ogrn = %s")
            params.append(profile_data.ogrn)
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет данных для обновления"
            )
        
        update_query = f"""
            UPDATE customer_profiles 
            SET {', '.join(update_fields)}, updated_at = %s
            WHERE user_id = %s
        """
        
        params.extend(["NOW()", current_user.id])
        db.execute(text(update_query), params)
        db.commit()
        
        # Возвращаем обновленный профиль
        return get_customer_profile(current_user, db)
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка в update_customer_profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении профиля: {str(e)}"
        )

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
