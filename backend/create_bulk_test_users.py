"""
Скрипт для создания массовых тестовых пользователей и управления существующими
"""
import os
import sys
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base, get_db
from models import User, ContractorProfile, CustomerProfile

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agregator_user:agregator_password_2024@localhost:5432/agregator_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def delete_user_by_email(email: str):
    """Удаляет пользователя по email и все связанные данные"""
    db = next(get_db_session())
    
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"🗑️ Удаляем пользователя {email}")
            
            # Удаляем профили
            if user.role == "contractor":
                contractor_profile = db.query(ContractorProfile).filter(ContractorProfile.user_id == user.id).first()
                if contractor_profile:
                    db.delete(contractor_profile)
            
            if user.role == "customer":
                customer_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == user.id).first()
                if customer_profile:
                    db.delete(customer_profile)
            
            # Удаляем пользователя
            db.delete(user)
            db.commit()
            print(f"✅ Пользователь {email} удален")
            return True
        else:
            print(f"ℹ️ Пользователь {email} не найден")
            return False
    except Exception as e:
        print(f"❌ Ошибка удаления пользователя: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def create_test_users():
    """Создает 20 тестовых пользователей"""
    db = next(get_db_session())
    
    print("🚀 Создание 20 тестовых пользователей...")
    
    # Тестовые данные
    users_data = [
        # Исполнители (contractors)
        {"username": "contractor1", "email": "contractor1@test.com", "role": "contractor", "first_name": "Иван", "last_name": "Петров"},
        {"username": "contractor2", "email": "contractor2@test.com", "role": "contractor", "first_name": "Петр", "last_name": "Сидоров"},
        {"username": "contractor3", "email": "contractor3@test.com", "role": "contractor", "first_name": "Алексей", "last_name": "Иванов"},
        {"username": "contractor4", "email": "contractor4@test.com", "role": "contractor", "first_name": "Сергей", "last_name": "Козлов"},
        {"username": "contractor5", "email": "contractor5@test.com", "role": "contractor", "first_name": "Михаил", "last_name": "Смирнов"},
        {"username": "contractor6", "email": "contractor6@test.com", "role": "contractor", "first_name": "Дмитрий", "last_name": "Волков"},
        {"username": "contractor7", "email": "contractor7@test.com", "role": "contractor", "first_name": "Андрей", "last_name": "Медведев"},
        {"username": "contractor8", "email": "contractor8@test.com", "role": "contractor", "first_name": "Владимир", "last_name": "Егоров"},
        {"username": "contractor9", "email": "contractor9@test.com", "role": "contractor", "first_name": "Александр", "last_name": "Новиков"},
        {"username": "contractor10", "email": "contractor10@test.com", "role": "contractor", "first_name": "Николай", "last_name": "Соколов"},
        
        # Заказчики (customers)
        {"username": "customer1", "email": "customer1@test.com", "role": "customer", "first_name": "ООО", "last_name": "Рога и Копыта"},
        {"username": "customer2", "email": "customer2@test.com", "role": "customer", "first_name": "ОАО", "last_name": "Сильные Горы"},
        {"username": "customer3", "email": "customer3@test.com", "role": "customer", "first_name": "ЗАО", "last_name": "Северный Рубеж"},
        {"username": "customer4", "email": "customer4@test.com", "role": "customer", "first_name": "ИП", "last_name": "Горное Дело"},
        {"username": "customer5", "email": "customer5@test.com", "role": "customer", "first_name": "ООО", "last_name": "ГеоСтрой"},
        
        # Сотрудник безопасности
        {"username": "security1", "email": "security1@test.com", "role": "security", "first_name": "Безопасность", "last_name": "Сотрудник1"},
        
        # Сотрудник HR
        {"username": "hr1", "email": "hr1@test.com", "role": "hr", "first_name": "HR", "last_name": "Сотрудник1"},
        
        # Менеджер
        {"username": "manager1", "email": "manager1@test.com", "role": "manager", "first_name": "Менеджер", "last_name": "Один"},
        
        # Еще 2 заказчика
        {"username": "customer6", "email": "customer6@test.com", "role": "customer", "first_name": "ООО", "last_name": "Топ Строй"},
        {"username": "customer7", "email": "customer7@test.com", "role": "customer", "first_name": "ООО", "last_name": "Горный Проспект"},
    ]
    
    created_count = 0
    
    for user_data in users_data:
        try:
            # Проверяем, существует ли пользователь
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                print(f"⚠️ Пользователь {user_data['email']} уже существует, пропускаем")
                continue
            
            # Хешируем пароль
            hashed_password = pwd_context.hash("password123")
            
            # Создаем пользователя
            new_user = User(
                username=user_data["username"],
                email=user_data["email"],
                password=hashed_password,
                role=user_data["role"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                is_active=True,
                is_password_changed=False,
                email_verified=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Создаем профиль в зависимости от роли
            if user_data["role"] == "contractor":
                contractor_profile = ContractorProfile(
                    user_id=new_user.id,
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    phone=f"+7(999)000-{created_count + 1:02d}-{created_count + 2:02d}",
                    email=user_data["email"],
                    telegram_username=f"test_contractor_{created_count + 1}" if created_count < 5 else None,
                    availability_status="available" if created_count % 2 == 0 else "busy"
                )
                db.add(contractor_profile)
            
            if user_data["role"] == "customer":
                customer_profile = CustomerProfile(
                    user_id=new_user.id,
                    company_name=user_data["last_name"],
                    contact_person=user_data["first_name"],
                    phone=f"+7(999)100-{created_count + 1:02d}-{created_count + 2:02d}",
                    email=user_data["email"],
                    address="Москва, ул. Тестовая, 1"
                )
                db.add(customer_profile)
            
            db.commit()
            created_count += 1
            print(f"✅ Создан пользователь {user_data['username']} ({user_data['email']})")
            
        except Exception as e:
            print(f"❌ Ошибка создания пользователя {user_data['email']}: {e}")
            db.rollback()
    
    print(f"\n📊 Всего создано пользователей: {created_count}")
    print(f"\n📋 Данные для входа (все пользователи используют пароль 'password123'):")
    print("\nИсполнители:")
    for user_data in users_data[:10]:
        print(f"  - {user_data['username']} ({user_data['email']})")
    
    print("\nЗаказчики:")
    for user_data in users_data[10:15]:
        print(f"  - {user_data['username']} ({user_data['email']})")
    
    print("\nСпециальные роли:")
    for user_data in users_data[15:]:
        print(f"  - {user_data['username']} ({user_data['email']}) - {user_data['role']}")
    
    db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Управление тестовыми пользователями')
    parser.add_argument('--delete-email', type=str, help='Удалить пользователя по email')
    parser.add_argument('--create', action='store_true', help='Создать тестовых пользователей')
    
    args = parser.parse_args()
    
    if args.delete_email:
        delete_user_by_email(args.delete_email)
    elif args.create:
        create_test_users()
    else:
        print("Использование:")
        print("  python create_bulk_test_users.py --delete-email user@example.com  # Удалить пользователя")
        print("  python create_bulk_test_users.py --create  # Создать тестовых пользователей")

