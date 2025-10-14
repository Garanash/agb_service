#!/usr/bin/env python3
"""
Скрипт для создания администратора
"""

import sys
import os
sys.path.append('/app')

from database import SessionLocal
from models import User
from passlib.context import CryptContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=['sha256_crypt'], deprecated='auto')

def create_admin():
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже админ
        admin = db.query(User).filter(User.username == 'admin').first()
        if admin:
            logger.info('✅ Администратор уже существует')
            return
        
        # Создаем админа
        admin = User(
            username='admin',
            email='admin@agregator.com',
            hashed_password=pwd_context.hash('admin123'),
            first_name='Администратор',
            last_name='Система',
            middle_name='admin',
            role='admin',
            is_active=True,
            email_verified=True
        )
        db.add(admin)
        db.commit()
        logger.info('✅ Администратор создан успешно')
        
    except Exception as e:
        logger.error(f'❌ Ошибка создания администратора: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_admin()