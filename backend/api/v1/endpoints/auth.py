from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
from typing import Optional
import asyncio
import logging

from database import get_db
from models import User
from ..schemas import LoginRequest, LoginResponse, UserCreate, UserResponse, EmailVerificationRequest, EmailVerificationResponse
from ..dependencies import (
    get_current_user, 
    create_access_token, 
    verify_password, 
    get_password_hash,
    generate_email_verification_token,
    verify_email_verification_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
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
    
    return UserResponse.from_orm(db_user)

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return UserResponse.from_orm(current_user)

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
