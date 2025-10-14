"""
Конфигурация для тестов
"""

import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Устанавливаем тестовую базу данных
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["TESTING"] = "true"

from database import get_db, Base
from main import app
from models import User, CustomerProfile, ContractorProfile, RepairRequest, SecurityVerification, HRDocument

# Создаем тестовую базу данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Переопределяем зависимость базы данных для тестов"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop для всей сессии тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Фикстура для сессии базы данных"""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Удаляем таблицы после теста
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Фикстура для тестового клиента FastAPI"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
async def async_client(db_session: Session) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для асинхронного тестового клиента"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """Фикстура для тестового пользователя"""
    from api.v1.dependencies import get_password_hash
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        first_name="Test",
        last_name="User",
        role="customer",
        is_active=True,
        email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_customer_profile(db_session: Session, test_user: User) -> CustomerProfile:
    """Фикстура для тестового профиля заказчика"""
    profile = CustomerProfile(
        user_id=test_user.id,
        company_name="Test Company",
        contact_person="Test Person",
        phone="+1234567890",
        email="test@example.com",
        address="Test Address",
        inn="1234567890",
        ogrn="1234567890123",
        equipment_brands=["Caterpillar", "Komatsu"],
        equipment_types=["Excavator", "Bulldozer"],
        mining_operations=["Open pit mining", "Quarrying"]
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile

@pytest.fixture(scope="function")
def test_contractor_profile(db_session: Session) -> ContractorProfile:
    """Фикстура для тестового профиля исполнителя"""
    from api.v1.dependencies import get_password_hash
    
    # Создаем пользователя-исполнителя
    contractor_user = User(
        username="contractor",
        email="contractor@example.com",
        hashed_password=get_password_hash("testpassword"),
        first_name="Contractor",
        last_name="User",
        role="contractor",
        is_active=True,
        email_verified=True
    )
    db_session.add(contractor_user)
    db_session.commit()
    db_session.refresh(contractor_user)
    
    # Создаем профиль исполнителя
    profile = ContractorProfile(
        user_id=contractor_user.id,
        first_name="Contractor",
        last_name="User",
        phone="+1234567890",
        email="contractor@example.com",
        telegram_username="contractor_user",
        specializations=["Hydraulic repair", "Engine maintenance"],
        equipment_brands_experience=["Caterpillar", "Komatsu"],
        certifications=["Certified technician"],
        work_regions=["Moscow", "St. Petersburg"],
        hourly_rate=1500.0,
        availability_status="available"
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile

@pytest.fixture(scope="function")
def test_repair_request(db_session: Session, test_customer_profile: CustomerProfile) -> RepairRequest:
    """Фикстура для тестовой заявки на ремонт"""
    request = RepairRequest(
        customer_id=test_customer_profile.id,
        title="Test Repair Request",
        description="Test description",
        urgency="medium",
        address="Test Address",
        city="Test City",
        region="Test Region",
        equipment_type="Excavator",
        equipment_brand="Caterpillar",
        equipment_model="CAT 320",
        problem_description="Test problem",
        priority="normal",
        status="new"
    )
    db_session.add(request)
    db_session.commit()
    db_session.refresh(request)
    return request

@pytest.fixture(scope="function")
def auth_headers(client: TestClient, test_user: User) -> dict:
    """Фикстура для заголовков авторизации"""
    # Логинимся и получаем токен
    response = client.post("/api/v1/auth/login", json={
        "username": test_user.username,
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def manager_user(db_session: Session) -> User:
    """Фикстура для тестового менеджера"""
    from api.v1.dependencies import get_password_hash
    
    user = User(
        username="manager",
        email="manager@example.com",
        hashed_password=get_password_hash("testpassword"),
        first_name="Manager",
        last_name="User",
        role="manager",
        is_active=True,
        email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def admin_user(db_session: Session) -> User:
    """Фикстура для тестового администратора"""
    from api.v1.dependencies import get_password_hash
    
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("testpassword"),
        first_name="Admin",
        last_name="User",
        role="admin",
        is_active=True,
        email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
