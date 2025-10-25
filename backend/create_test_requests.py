"""
Скрипт для создания тестовых заявок
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone, timedelta
import random

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from database import Base, get_db
from models import User, RepairRequest, CustomerProfile, ContractorProfile, ContractorResponse

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/agregator_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_test_requests():
    db = next(get_db_session())
    
    print("Создание тестовых заявок...")
    
    # Получаем заказчиков
    customers = db.query(CustomerProfile).join(User, CustomerProfile.user_id == User.id).filter(User.role == 'customer').all()
    if not customers:
        print("❌ Нет заказчиков для создания заявок")
        return
    
    # Получаем исполнителей
    contractors = db.query(ContractorProfile).join(User, ContractorProfile.user_id == User.id).filter(User.role == 'contractor').all()
    if not contractors:
        print("❌ Нет исполнителей для создания заявок")
        return
    
    print(f"📊 Найдено заказчиков: {len(customers)}")
    print(f"📊 Найдено исполнителей: {len(contractors)}")
    
    # Удаляем существующие тестовые заявки
    existing_requests = db.query(RepairRequest).filter(RepairRequest.title.like('Тестовая заявка%')).all()
    for request in existing_requests:
        db.delete(request)
    db.commit()
    print(f"🗑️ Удалено существующих тестовых заявок: {len(existing_requests)}")
    
    # Создаем тестовые заявки
    test_requests_data = [
        {
            "title": "Тестовая заявка - Ремонт буровой установки",
            "description": "Требуется ремонт буровой установки на участке №1. Обнаружены неисправности в гидравлической системе.",
            "equipment_type": "Буровая установка",
            "urgency": "high",
            "status": "pending",
            "address": "Участок №1, г. Москва",
            "city": "Москва",
            "region": "Московская область",
            "estimated_cost": 150000.0,
        },
        {
            "title": "Тестовая заявка - Техническое обслуживание",
            "description": "Плановое техническое обслуживание оборудования. Замена фильтров, проверка систем.",
            "equipment_type": "Оборудование",
            "urgency": "medium",
            "status": "in_progress",
            "address": "Склад №2, г. Санкт-Петербург",
            "city": "Санкт-Петербург",
            "region": "Ленинградская область",
            "estimated_cost": 75000.0,
        },
        {
            "title": "Тестовая заявка - Аварийный ремонт",
            "description": "Срочный ремонт насосного оборудования. Остановка производства.",
            "equipment_type": "Насосное оборудование",
            "urgency": "urgent",
            "status": "completed",
            "address": "Производство №3, г. Екатеринбург",
            "city": "Екатеринбург",
            "region": "Свердловская область",
            "estimated_cost": 200000.0,
        },
        {
            "title": "Тестовая заявка - Модернизация системы",
            "description": "Модернизация системы управления. Установка нового программного обеспечения.",
            "equipment_type": "Система управления",
            "urgency": "low",
            "status": "pending",
            "address": "Цех №4, г. Новосибирск",
            "city": "Новосибирск",
            "region": "Новосибирская область",
            "estimated_cost": 300000.0,
        },
        {
            "title": "Тестовая заявка - Диагностика оборудования",
            "description": "Комплексная диагностика всего оборудования на объекте. Составление отчета.",
            "equipment_type": "Диагностическое оборудование",
            "urgency": "medium",
            "status": "in_progress",
            "address": "Объект №5, г. Казань",
            "city": "Казань",
            "region": "Республика Татарстан",
            "estimated_cost": 120000.0,
        },
    ]
    
    created_requests = []
    
    for i, request_data in enumerate(test_requests_data):
        # Выбираем случайного заказчика
        customer = random.choice(customers)
        
        # Создаем заявку
        new_request = RepairRequest(
            title=request_data["title"],
            description=request_data["description"],
            customer_id=customer.id,
            urgency=request_data["urgency"],
            address=request_data["address"],
            city=request_data["city"],
            region=request_data["region"],
            equipment_type=request_data["equipment_type"],
            priority=request_data["urgency"],
            estimated_cost=request_data["estimated_cost"],
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
            updated_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 5)),
        )
        
        # Если заявка в работе или завершена, добавляем даты
        if request_data["status"] in ["in_progress", "completed"]:
            new_request.assigned_at = new_request.created_at + timedelta(days=random.randint(1, 3))
        
        if request_data["status"] == "completed":
            new_request.processed_at = new_request.assigned_at + timedelta(days=random.randint(1, 7))
        
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        created_requests.append(new_request)
        
        print(f"✅ Создана заявка: {new_request.title}")
        
        # Если заявка в работе или завершена, создаем отклики исполнителей
        if request_data["status"] in ["in_progress", "completed"]:
            # Выбираем случайного исполнителя
            contractor = random.choice(contractors)
            
            response = ContractorResponse(
                request_id=new_request.id,
                contractor_id=contractor.id,
                proposed_price=int(request_data["estimated_cost"] * random.uniform(0.8, 1.2)),
                estimated_time=f"{random.randint(1, 14)} дней",
                comment=f"Готов выполнить работу по заявке '{new_request.title}'. Имею опыт работы с данным типом оборудования.",
                is_accepted=True,
                created_at=new_request.created_at + timedelta(hours=random.randint(1, 24)),
            )
            
            db.add(response)
            db.commit()
            
            # Назначаем исполнителя на заявку (используем user_id из contractor_profile)
            new_request.assigned_contractor_id = contractor.user_id
            db.commit()
            
            print(f"  📝 Добавлен отклик исполнителя: {contractor.first_name} {contractor.last_name}")
    
    print(f"\n📊 Итого создано заявок: {len(created_requests)}")
    print("📋 Список созданных заявок:")
    for request in created_requests:
        print(f"  - {request.title} ({request.status}) - {request.priority}")
    
    db.close()

if __name__ == "__main__":
    create_test_requests()
