# Инструкция по исправлению ошибки авторизации на сервере

## Проблема
Ошибка 500 при авторизации из-за несоответствия схем хеширования паролей.

## Решение (выполните на сервере)

### Шаг 1: Подключитесь к серверу
```bash
ssh root@91.222.236.58
cd /root/agregator-service
```

### Шаг 2: Создайте скрипт исправления
Создайте файл `fix_passwords.py`:
```bash
cat > fix_passwords.py << 'EOF'
#!/usr/bin/env python3
"""
Скрипт для исправления хешей паролей в базе данных
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
EOF
```

### Шаг 3: Запустите исправление
```bash
# Копируем скрипт в контейнер
docker cp fix_passwords.py agregator-backend:/app/fix_passwords.py

# Запускаем исправление
docker-compose exec agregator-backend python /app/fix_passwords.py
```

### Шаг 4: Проверьте результат
```bash
# Проверьте статус контейнеров
docker-compose ps

# Проверьте логи бэкенда
docker-compose logs agregator-backend --tail 20
```

### Шаг 5: Тестирование
Попробуйте войти в систему:
- URL: http://91.222.236.58:3000/login
- Логин: admin
- Пароль: admin123

## Альтернативное решение (если первое не работает)

### Пересоздание базы данных:
```bash
# Остановите контейнеры
docker-compose down

# Удалите данные базы данных
docker volume rm agregator-service_agregator_postgres_data

# Запустите контейнеры заново
docker-compose up -d

# Подождите запуска
sleep 30

# Создайте таблицы
docker-compose exec agregator-backend python -c "
from database import engine
from models import Base
print('Создаем таблицы в базе данных...')
Base.metadata.create_all(bind=engine)
print('Таблицы созданы успешно!')
"

# Создайте администратора с правильным хешем
docker-compose exec agregator-backend python -c "
from database import SessionLocal
from models import User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['sha256_crypt'], deprecated='auto')
db = SessionLocal()

# Проверяем, есть ли уже админ
admin = db.query(User).filter(User.username == 'admin').first()
if admin:
    print('Администратор уже существует')
else:
    # Создаем хеш пароля
    password = 'admin123'
    hashed_password = pwd_context.hash(password)
    
    # Создаем администратора
    admin_user = User(
        username='admin',
        email='admin@agb-service.com',
        hashed_password=hashed_password,
        first_name='Администратор',
        last_name='Системы',
        role=UserRole.ADMIN.value,
        is_active=True,
        is_password_changed=True,
        email_verified=True
    )
    
    db.add(admin_user)
    db.commit()
    print('Администратор создан успешно!')
    print('Логин: admin')
    print('Пароль: admin123')

db.close()
"
```

## После исправления
Попробуйте войти в систему с данными admin/admin123. Проблема должна быть решена!
