#!/bin/bash

# Скрипт для инициализации базы данных на сервере

echo "🗄️ Инициализация базы данных..."

# Создаем таблицы
echo "📋 Создаем таблицы в базе данных..."
docker-compose exec agregator-backend python -c "
from database import engine
from models import Base
print('Создаем таблицы в базе данных...')
Base.metadata.create_all(bind=engine)
print('Таблицы созданы успешно!')
"

# Создаем администратора
echo "👤 Создаем администратора..."
docker-compose exec agregator-backend python -c "
from database import SessionLocal
from models import User, UserRole
import bcrypt

db = SessionLocal()

# Проверяем, есть ли уже админ
admin = db.query(User).filter(User.username == 'admin').first()
if admin:
    print('Администратор уже существует')
else:
    # Создаем хеш пароля
    password = 'admin123'
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Создаем администратора
    admin_user = User(
        username='admin',
        email='admin@agb-service.com',
        hashed_password=hashed_password,
        first_name='Администратор',
        last_name='Системы',
        role=UserRole.ADMIN,
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

# Создаем тестовых пользователей
echo "👥 Создаем тестовых пользователей..."
docker-compose exec agregator-backend python -c "
from database import SessionLocal
from models import User, UserRole
import bcrypt

db = SessionLocal()

# Создаем тестовых пользователей
users_data = [
    {'username': 'customer1', 'email': 'customer1@test.com', 'first_name': 'Иван', 'last_name': 'Петров', 'role': UserRole.CUSTOMER},
    {'username': 'customer2', 'email': 'customer2@test.com', 'first_name': 'Мария', 'last_name': 'Сидорова', 'role': UserRole.CUSTOMER},
    {'username': 'contractor1', 'email': 'contractor1@test.com', 'first_name': 'Алексей', 'last_name': 'Козлов', 'role': UserRole.CONTRACTOR},
    {'username': 'contractor2', 'email': 'contractor2@test.com', 'first_name': 'Елена', 'last_name': 'Морозова', 'role': UserRole.CONTRACTOR},
    {'username': 'manager1', 'email': 'manager1@test.com', 'first_name': 'Дмитрий', 'last_name': 'Волков', 'role': UserRole.MANAGER},
    {'username': 'security1', 'email': 'security1@test.com', 'first_name': 'Андрей', 'last_name': 'Лебедев', 'role': UserRole.SECURITY},
    {'username': 'hr1', 'email': 'hr1@test.com', 'first_name': 'Ольга', 'last_name': 'Новикова', 'role': UserRole.HR},
]

password = 'password123'
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

for user_data in users_data:
    existing_user = db.query(User).filter(User.username == user_data['username']).first()
    if not existing_user:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            hashed_password=hashed_password,
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            is_active=True,
            is_password_changed=True,
            email_verified=True
        )
        db.add(user)
        print(f'Создан пользователь: {user_data[\"username\"]}')

db.commit()
print('Тестовые пользователи созданы!')
print('Пароль для всех: password123')

db.close()
"

echo "✅ База данных инициализирована успешно!"
echo "🔑 Данные для входа:"
echo "   Админ: admin / admin123"
echo "   Тестовые пользователи: customer1, contractor1, manager1, security1, hr1 / password123"
