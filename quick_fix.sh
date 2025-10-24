#!/bin/bash
# Скрипт для быстрого исправления паролей на сервере
# Скопируйте и вставьте этот код в терминал сервера

echo "🔧 Исправляем пароли в базе данных..."

# Создаем скрипт исправления
cat > /tmp/fix_passwords.py << 'EOF'
#!/usr/bin/env python3
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

def fix_passwords():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        if not users:
            logger.info('Пользователи не найдены')
            return
        
        logger.info(f'Найдено {len(users)} пользователей')
        
        for user in users:
            logger.info(f'Исправляем пароль для пользователя: {user.username}')
            
            if user.username == 'admin':
                password = 'admin123'
            else:
                password = 'password123'
            
            user.hashed_password = pwd_context.hash(password)
            user.is_password_changed = True
            
            logger.info(f'✅ Пароль обновлен для {user.username}')
        
        db.commit()
        logger.info('✅ Все пароли успешно обновлены!')
        
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
EOF

# Копируем скрипт в контейнер
echo "📋 Копируем скрипт в контейнер..."
docker cp /tmp/fix_passwords.py agregator-backend:/app/fix_passwords.py

# Запускаем исправление
echo "🚀 Запускаем исправление паролей..."
docker-compose exec agregator-backend python /app/fix_passwords.py

# Очищаем временный файл
rm /tmp/fix_passwords.py

echo "✅ Исправление завершено!"
echo "🔑 Теперь можно войти с данными:"
echo "   Админ: admin / admin123"
echo "   Остальные пользователи: username / password123"
