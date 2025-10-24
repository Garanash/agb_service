#!/usr/bin/env python3
"""
Скрипт для исправления хешей паролей в базе данных
Конвертирует bcrypt хеши в sha256_crypt хеши
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

# Используем sha256_crypt для совместимости с кодом авторизации
pwd_context = CryptContext(schemes=['sha256_crypt'], deprecated='auto')

def fix_passwords():
    """Исправляем хеши паролей для всех пользователей"""
    db = SessionLocal()
    try:
        # Получаем всех пользователей
        users = db.query(User).all()
        
        if not users:
            logger.info('Пользователи не найдены')
            return
        
        logger.info(f'Найдено {len(users)} пользователей')
        
        # Исправляем пароли для каждого пользователя
        for user in users:
            logger.info(f'Исправляем пароль для пользователя: {user.username}')
            
            # Устанавливаем стандартные пароли в зависимости от роли
            if user.username == 'admin':
                password = 'admin123'
            else:
                password = 'password123'
            
            # Создаем новый хеш
            user.hashed_password = pwd_context.hash(password)
            user.is_password_changed = True
            
            logger.info(f'✅ Пароль обновлен для {user.username}')
        
        # Сохраняем изменения
        db.commit()
        logger.info('✅ Все пароли успешно обновлены!')
        
        # Выводим информацию о пользователях
        logger.info('🔑 Данные для входа:')
        for user in users:
            if user.username == 'admin':
                logger.info(f'   Админ: {user.username} / admin123')
            else:
                logger.info(f'   {user.username} / password123')
        
    except Exception as e:
        logger.error(f'❌ Ошибка исправления паролей: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    fix_passwords()
