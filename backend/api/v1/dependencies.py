from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import os
import secrets
import hashlib

from database import get_db
from models import User

# Секретный ключ для JWT
SECRET_KEY = os.getenv("SECRET_KEY", "agregator_secret_key_2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 часа

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя по токену"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Получение текущего пользователя (опционально)"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
    return pwd_context.hash(password)

def generate_email_verification_token() -> str:
    """Генерация токена подтверждения email"""
    return secrets.token_urlsafe(32)

def verify_email_verification_token(token: str, db: Session) -> Optional[User]:
    """Проверка токена подтверждения email"""
    user = db.query(User).filter(User.email_verification_token == token).first()
    if not user:
        return None
    
    # Проверяем, что токен не истек (24 часа)
    if user.created_at:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        if user.created_at.tzinfo is None:
            # Если created_at без часового пояса, добавляем UTC
            user_created_at = user.created_at.replace(tzinfo=timezone.utc)
        else:
            user_created_at = user.created_at
            
        if now - user_created_at > timedelta(hours=24):
            return None
    
    return user

def require_role(allowed_roles: list):
    """Декоратор для проверки ролей пользователя"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуются роли: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker
