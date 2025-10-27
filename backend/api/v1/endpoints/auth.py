from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
from typing import Optional
import asyncio
import logging

from database import get_db
from models import User
from ..schemas import (
    LoginRequest, LoginResponse, UserCreate, UserResponse, 
    EmailVerificationRequest, EmailVerificationResponse,
    CustomerRegistrationRequest, ContractorRegistrationRequest,
    SimpleRegistrationRequest
)
from ..dependencies import (
    get_current_user, 
    create_access_token, 
    verify_password, 
    get_password_hash,
    generate_email_verification_token,
    verify_email_verification_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from services.analytics_service import analytics_service
from services.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Аутентификация пользователя"""
    # Проверяем пользователя в базе данных
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь деактивирован"
        )
    
    # Создаем токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Отправляем событие входа в аналитику
    try:
        analytics_service.track_user_login(
            user_id=user.id,
            user_role=user.role,
            login_method="web"
        )
    except Exception as e:
        logger.warning(f"Failed to track user login: {e}")
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.from_orm(user)
    )

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    # Проверяем, что пользователь с таким username не существует
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Проверяем, что пользователь с таким email не существует
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password)
    verification_token = generate_email_verification_token()
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        middle_name=user_data.middle_name,
        phone=user_data.phone,
        position=user_data.position,
        role=user_data.role.value,
        is_active=True,
        is_password_changed=False,
        email_verified=False,
        email_verification_token=verification_token
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Отправляем письмо подтверждения email асинхронно
    try:
        user_name = f"{user_data.first_name or ''} {user_data.last_name or ''}".strip() or user_data.username
        email_sent = await email_service.send_email_verification(
            user_email=user_data.email,
            user_name=user_name,
            verification_token=verification_token
        )
        
        if email_sent:
            logger.info(f"✅ Письмо подтверждения отправлено пользователю {user_data.email}")
        else:
            logger.warning(f"⚠️ Не удалось отправить письмо подтверждения пользователю {user_data.email}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки письма подтверждения: {e}")
        # Не прерываем регистрацию из-за ошибки отправки почты
    
    # Отправляем событие регистрации в аналитику
    try:
        analytics_service.track_user_registration(
            user_id=db_user.id,
            user_role=db_user.role,
            registration_source="web"
        )
    except Exception as e:
        logger.warning(f"Failed to track user registration: {e}")
    
    return UserResponse.from_orm(db_user)

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о текущем пользователе"""
    # Загружаем профиль исполнителя если он существует
    contractor_profile_id = None
    if current_user.contractor_profile:
        contractor_profile_id = current_user.contractor_profile.id
    
    # Создаем словарь с данными пользователя
    user_data = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "middle_name": current_user.middle_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_password_changed": current_user.is_password_changed,
        "email_verified": current_user.email_verified,
        "avatar_url": current_user.avatar_url,
        "phone": current_user.phone,
        "position": current_user.position,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "contractor_profile_id": contractor_profile_id
    }
    
    return UserResponse(**user_data)

@router.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Смена пароля"""
    # Проверяем текущий пароль
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль"
        )
    
    # Обновляем пароль
    current_user.hashed_password = get_password_hash(new_password)
    current_user.is_password_changed = True
    db.commit()
    
    return {"message": "Пароль успешно изменен"}

@router.post("/verify-email", response_model=EmailVerificationResponse)
def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """Подтверждение email адреса"""
    user = verify_email_verification_token(verification_data.token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недействительный или истекший токен подтверждения"
        )
    
    if user.email_verified:
        return EmailVerificationResponse(
            message="Email уже подтвержден",
            verified=True
        )
    
    # Подтверждаем email
    user.email_verified = True
    user.email_verification_token = None  # Удаляем токен после использования
    db.commit()
    
    logger.info(f"✅ Email подтвержден для пользователя {user.username}")
    
    return EmailVerificationResponse(
        message="Email успешно подтвержден! Теперь вы можете войти в систему.",
        verified=True
    )

@router.post("/register-customer", response_model=UserResponse)
async def register_customer(
    customer_data: CustomerRegistrationRequest,
    db: Session = Depends(get_db)
):
    """Регистрация нового заказчика с полями для горнодобывающей техники"""
    # Проверяем, что пользователь с таким username не существует
    existing_user = db.query(User).filter(User.username == customer_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Проверяем, что пользователь с таким email не существует
    existing_email = db.query(User).filter(User.email == customer_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(customer_data.password)
    verification_token = generate_email_verification_token()
    
    db_user = User(
        username=customer_data.username,
        email=customer_data.email,
        hashed_password=hashed_password,
        first_name=customer_data.first_name,
        last_name=customer_data.last_name,
        middle_name=customer_data.middle_name,
        phone=customer_data.phone,
        position=customer_data.position,
        role="customer",
        is_active=True,
        is_password_changed=False,
        email_verified=False,
        email_verification_token=verification_token
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Создаем профиль заказчика
    from models import CustomerProfile
    customer_profile = CustomerProfile(
        user_id=db_user.id,
        company_name=customer_data.company_name,
        contact_person=customer_data.first_name or customer_data.username,
        phone=customer_data.phone or "",
        email=customer_data.email,
        address=customer_data.region,
        inn=customer_data.inn_or_ogrn if customer_data.inn_or_ogrn.isdigit() and len(customer_data.inn_or_ogrn) == 10 else None,
        ogrn=customer_data.inn_or_ogrn if len(customer_data.inn_or_ogrn) == 13 else None,
        equipment_brands=customer_data.equipment_brands,
        equipment_types=customer_data.equipment_types,
        mining_operations=customer_data.mining_operations,
        service_history=customer_data.service_history
    )
    
    db.add(customer_profile)
    db.commit()
    
    # Отправляем письмо подтверждения email асинхронно
    try:
        user_name = f"{customer_data.first_name or ''} {customer_data.last_name or ''}".strip() or customer_data.username
        email_sent = await email_service.send_email_verification(
            user_email=customer_data.email,
            user_name=user_name,
            verification_token=verification_token
        )
        
        if email_sent:
            logger.info(f"✅ Письмо подтверждения отправлено заказчику {customer_data.email}")
        else:
            logger.warning(f"⚠️ Не удалось отправить письмо подтверждения заказчику {customer_data.email}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки письма подтверждения: {e}")
        # Не прерываем регистрацию из-за ошибки отправки почты
    
    return UserResponse.from_orm(db_user)

@router.post("/register-contractor", response_model=UserResponse)
async def register_contractor(
    contractor_data: ContractorRegistrationRequest,
    db: Session = Depends(get_db)
):
    """Регистрация нового исполнителя с полями специализации"""
    # Проверяем, что пользователь с таким username не существует
    existing_user = db.query(User).filter(User.username == contractor_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Проверяем, что пользователь с таким email не существует
    existing_email = db.query(User).filter(User.email == contractor_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(contractor_data.password)
    verification_token = generate_email_verification_token()
    
    db_user = User(
        username=contractor_data.username,
        email=contractor_data.email,
        hashed_password=hashed_password,
        first_name=contractor_data.first_name,
        last_name=contractor_data.last_name,
        middle_name=contractor_data.middle_name,
        phone=contractor_data.phone,
        position=contractor_data.position,
        role="contractor",
        is_active=True,
        is_password_changed=False,
        email_verified=False,
        email_verification_token=verification_token
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Создаем профиль исполнителя
    from models import ContractorProfile
    contractor_profile = ContractorProfile(
        user_id=db_user.id,
        first_name=contractor_data.first_name,
        last_name=contractor_data.last_name,
        patronymic=contractor_data.middle_name,
        phone=contractor_data.phone,
        email=contractor_data.email,
        telegram_username=contractor_data.telegram_username,
        specializations=contractor_data.specializations,
        equipment_brands_experience=contractor_data.equipment_brands_experience,
        certifications=contractor_data.certifications,
        work_regions=contractor_data.work_regions,
        hourly_rate=contractor_data.hourly_rate,
        availability_status="available"
    )
    
    db.add(contractor_profile)
    db.commit()
    
    # Создаем заявку на проверку службой безопасности
    try:
        from services.security_verification_service import get_security_verification_service
        security_service = get_security_verification_service(db)
        security_service.create_verification_request(contractor_profile.id)
        logger.info(f"✅ Создана заявка на проверку для исполнителя {contractor_profile.id}")
    except Exception as e:
        logger.error(f"❌ Ошибка создания заявки на проверку: {e}")
        # Не прерываем регистрацию из-за ошибки создания заявки на проверку
    
    # Отправляем письмо подтверждения email асинхронно
    try:
        user_name = f"{contractor_data.first_name or ''} {contractor_data.last_name or ''}".strip() or contractor_data.username
        email_sent = await email_service.send_email_verification(
            user_email=contractor_data.email,
            user_name=user_name,
            verification_token=verification_token
        )
        
        if email_sent:
            logger.info(f"✅ Письмо подтверждения отправлено исполнителю {contractor_data.email}")
        else:
            logger.warning(f"⚠️ Не удалось отправить письмо подтверждения исполнителю {contractor_data.email}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки письма подтверждения: {e}")
        # Не прерываем регистрацию из-за ошибки отправки почты
    
    return UserResponse.from_orm(db_user)

@router.post("/resend-verification/{user_id}")
async def resend_email_verification(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Повторная отправка письма подтверждения email"""
    
    # Получаем пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Если email уже подтвержден, не отправляем письмо
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже подтвержден"
        )
    
    # Генерируем новый токен подтверждения
    verification_token = generate_email_verification_token()
    user.email_verification_token = verification_token
    db.commit()
    
    # Отправляем письмо подтверждения
    try:
        email_sent = await email_service.send_email_verification(
            user_email=user.email,
            user_name=user.username,
            verification_token=verification_token
        )
        
        if email_sent:
            logger.info(f"✅ Письмо подтверждения повторно отправлено пользователю {user.email}")
            return {"message": "Письмо подтверждения отправлено"}
        else:
            logger.warning(f"⚠️ Не удалось повторно отправить письмо подтверждения пользователю {user.email}")
            return {"message": "Письмо подтверждения отправлено (возможны проблемы с доставкой)"}
            
    except Exception as e:
        logger.error(f"❌ Ошибка повторной отправки письма подтверждения: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка отправки письма подтверждения"
        )

@router.post("/register-simple", response_model=UserResponse)
async def register_simple(
    registration_data: SimpleRegistrationRequest,
    db: Session = Depends(get_db)
):
    """Упрощенная регистрация пользователя (только основные поля)"""
    
    # Проверяем совпадение паролей
    if registration_data.password != registration_data.confirmPassword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароли не совпадают"
        )
    
    # Проверяем, что пользователь с таким username не существует
    existing_user = db.query(User).filter(User.username == registration_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Проверяем, что пользователь с таким email не существует
    existing_email = db.query(User).filter(User.email == registration_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(registration_data.password)
    verification_token = generate_email_verification_token()
    
    db_user = User(
        username=registration_data.username,
        email=registration_data.email,
        hashed_password=hashed_password,
        first_name="",  # Пустые поля, будут заполнены позже
        last_name="",
        middle_name="",
        phone="",
        position="",
        role=registration_data.role,
        is_active=True,
        is_password_changed=False,
        email_verified=False,
        email_verification_token=verification_token
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Создаем профиль в зависимости от роли
    if registration_data.role == "contractor":
        from models import ContractorProfile
        contractor_profile = ContractorProfile(
            user_id=db_user.id,
            first_name="",
            last_name="",
            patronymic="",
            phone="",
            email=registration_data.email,
            telegram_username="",
            specializations=[],
            equipment_brands_experience=[],
            certifications=[],
            work_regions=[],
            hourly_rate=0,
            availability_status="available"
        )
        db.add(contractor_profile)
        
        # Создаем заявку на проверку службой безопасности
        try:
            from services.security_verification_service import get_security_verification_service
            security_service = get_security_verification_service(db)
            security_service.create_verification_request(contractor_profile.id)
            logger.info(f"✅ Создана заявка на проверку для исполнителя {contractor_profile.id}")
        except Exception as e:
            logger.error(f"❌ Ошибка создания заявки на проверку: {e}")
    
    elif registration_data.role == "customer":
        from models import CustomerProfile
        customer_profile = CustomerProfile(
            user_id=db_user.id,
            company_name="",
            contact_person=registration_data.username,
            phone="",
            email=registration_data.email,
            address="",
            inn=None,
            kpp=None,
            ogrn=None,
            equipment_brands=[],
            equipment_types=[],
            mining_operations=[],
            service_history=""
        )
        db.add(customer_profile)
    
    db.commit()
    
    # Отправляем письмо подтверждения email асинхронно
    try:
        email_sent = await email_service.send_email_verification(
            user_email=registration_data.email,
            user_name=registration_data.username,
            verification_token=verification_token
        )
        
        if email_sent:
            logger.info(f"✅ Письмо подтверждения отправлено пользователю {registration_data.email}")
        else:
            logger.warning(f"⚠️ Не удалось отправить письмо подтверждения пользователю {registration_data.email}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки письма подтверждения: {e}")
        # Не прерываем регистрацию из-за ошибки отправки почты
    
    return UserResponse.from_orm(db_user)
