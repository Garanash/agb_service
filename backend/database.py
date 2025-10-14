"""
Agregator Service - Подключение к базе данных
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL подключения к базе данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agregator_user:agregator_password_2024@localhost:15433/agregator_db")

# Создание движка базы данных
engine = create_engine(DATABASE_URL, echo=False)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_session():
    """Возвращает сессию для работы с БД"""
    return SessionLocal()