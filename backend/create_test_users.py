#!/usr/bin/env python3
"""
Скрипт для создания тестовых пользователей
"""
from database import get_db
from models import User, ContractorProfile, CustomerProfile
from api.v1.dependencies import get_password_hash, generate_email_verification_token
import logging

logger = logging.getLogger(__name__)

def create_test_users():
    db = next(get_db())
    
    # Список тестовых пользователей
    test_users = [
        # Исполнители
        {'username': 'contractor2', 'email': 'contractor2@test.com', 'role': 'contractor', 'first_name': 'Петр', 'last_name': 'Петров'},
        {'username': 'contractor3', 'email': 'contractor3@test.com', 'role': 'contractor', 'first_name': 'Сергей', 'last_name': 'Сергеев'},
        
        # Заказчики
        {'username': 'customer1', 'email': 'customer1@test.com', 'role': 'customer', 'first_name': 'Анна', 'last_name': 'Аннова'},
        {'username': 'customer2', 'email': 'customer2@test.com', 'role': 'customer', 'first_name': 'Мария', 'last_name': 'Марьева'},
        
        # СБ специалист
        {'username': 'security1', 'email': 'security1@test.com', 'role': 'security', 'first_name': 'Алексей', 'last_name': 'Алексеев'},
        
        # HR специалист
        {'username': 'hr1', 'email': 'hr1@test.com', 'role': 'hr', 'first_name': 'Елена', 'last_name': 'Еленова'},
        
        # Менеджер по сервису
        {'username': 'manager1', 'email': 'manager1@test.com', 'role': 'manager', 'first_name': 'Дмитрий', 'last_name': 'Дмитриев'},
    ]
    
    created_users = []
    
    for user_data in test_users:
        try:
            # Проверяем, существует ли пользователь
            existing_user = db.query(User).filter(User.username == user_data['username']).first()
            if existing_user:
                print(f'⚠️ Пользователь {user_data["username"]} уже существует, пропускаем')
                continue
            
            # Создаем пользователя
            verification_token = generate_email_verification_token()
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                hashed_password=get_password_hash('password123'),
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                is_active=True,
                email_verified=True,  # Подтвержденные пользователи
                email_verification_token=verification_token
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Создаем профили в зависимости от роли
            if user_data['role'] == 'contractor':
                contractor_profile = ContractorProfile(
                    user_id=user.id,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    patronymic='',
                    phone='+7(999)123-45-67',
                    email=user_data['email'],
                    telegram_username=f'@{user_data["username"]}',
                    specializations=['Бурение', 'Ремонт оборудования'],
                    equipment_brands_experience=['Atlas Copco', 'Sandvik'],
                    certifications=['Сертификат безопасности'],
                    work_regions=['Москва', 'Санкт-Петербург'],
                    hourly_rate=1500,
                    availability_status='available'
                )
                db.add(contractor_profile)
                
            elif user_data['role'] == 'customer':
                customer_profile = CustomerProfile(
                    user_id=user.id,
                    company_name=f'ООО {user_data["first_name"]} {user_data["last_name"]}',
                    contact_person=f'{user_data["first_name"]} {user_data["last_name"]}',
                    phone='+7(999)123-45-67',
                    email=user_data['email'],
                    address='г. Москва, ул. Тестовая, д. 1',
                    inn='1234567890',
                    kpp='123456789',
                    ogrn='1234567890123',
                    equipment_brands=['Atlas Copco'],
                    equipment_types=['Буровые установки'],
                    mining_operations=['Открытые работы'],
                    service_history='Работаем с 2020 года'
                )
                db.add(customer_profile)
            
            db.commit()
            created_users.append(user)
            print(f'✅ Создан пользователь: {user.username} ({user.email}) - {user.role}')
            
        except Exception as e:
            print(f'❌ Ошибка создания пользователя {user_data["username"]}: {e}')
            db.rollback()
    
    print(f'\n📊 Итого создано пользователей: {len(created_users)}')
    print('📋 Список созданных пользователей:')
    for user in created_users:
        print(f'  - {user.username} ({user.email}) - {user.role}')

if __name__ == "__main__":
    create_test_users()
