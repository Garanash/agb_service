"""
Интеграционные тесты API
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.orm import Session

from tests.factories import UserFactory, CustomerProfileFactory, ContractorProfileFactory, RepairRequestFactory, SecurityVerificationFactory


class TestAuthAPI:
    """Тесты для API аутентификации"""
    
    def test_register_user(self, client: TestClient, db_session: Session):
        """Тест регистрации пользователя"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpassword123",
            "first_name": "New",
            "last_name": "User",
            "role": "customer"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["role"] == "customer"
        assert "id" in data
    
    def test_register_duplicate_username(self, client: TestClient, db_session: Session):
        """Тест регистрации с дублирующимся username"""
        # Создаем пользователя
        user = UserFactory(username="existinguser")
        db_session.add(user)
        db_session.commit()
        
        user_data = {
            "username": "existinguser",
            "email": "different@example.com",
            "password": "testpassword123",
            "role": "customer"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "уже существует" in response.json()["detail"]
    
    def test_login_success(self, client: TestClient, db_session: Session):
        """Тест успешного входа"""
        user = UserFactory(username="testuser", email="test@example.com")
        db_session.add(user)
        db_session.commit()
        
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"
    
    def test_login_invalid_credentials(self, client: TestClient, db_session: Session):
        """Тест входа с неверными данными"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Неверные учетные данные" in response.json()["detail"]
    
    def test_get_current_user(self, client: TestClient, auth_headers: dict):
        """Тест получения текущего пользователя"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "role" in data
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Тест получения текущего пользователя без авторизации"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401


class TestCustomerCabinetAPI:
    """Тесты для API личного кабинета заказчика"""
    
    def test_get_customer_profile(self, client: TestClient, db_session: Session, auth_headers: dict):
        """Тест получения профиля заказчика"""
        # Создаем профиль заказчика
        customer_profile = CustomerProfileFactory()
        db_session.add(customer_profile)
        db_session.commit()
        
        response = client.get("/api/v1/customer/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "user_info" in data
        assert "company_info" in data
        assert "equipment_info" in data
    
    def test_update_customer_profile(self, client: TestClient, db_session: Session, auth_headers: dict):
        """Тест обновления профиля заказчика"""
        customer_profile = CustomerProfileFactory()
        db_session.add(customer_profile)
        db_session.commit()
        
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "company_name": "Updated Company",
            "address": "Updated Address"
        }
        
        response = client.put("/api/v1/customer/profile", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        assert "успешно обновлен" in response.json()["message"]
    
    def test_create_customer_request(self, client: TestClient, db_session: Session, auth_headers: dict):
        """Тест создания заявки заказчиком"""
        customer_profile = CustomerProfileFactory()
        db_session.add(customer_profile)
        db_session.commit()
        
        request_data = {
            "title": "Test Request",
            "description": "Test description",
            "urgency": "medium",
            "address": "Test Address",
            "city": "Test City",
            "region": "Test Region",
            "equipment_type": "Excavator",
            "equipment_brand": "Caterpillar",
            "equipment_model": "CAT 320",
            "problem_description": "Test problem",
            "priority": "normal"
        }
        
        response = client.post("/api/v1/customer/requests", json=request_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Request"
        assert data["description"] == "Test description"
        assert data["status"] == "new"
    
    def test_get_customer_requests(self, client: TestClient, db_session: Session, auth_headers: dict):
        """Тест получения заявок заказчика"""
        customer_profile = CustomerProfileFactory()
        request1 = RepairRequestFactory(customer_id=customer_profile.id)
        request2 = RepairRequestFactory(customer_id=customer_profile.id)
        db_session.add_all([customer_profile, request1, request2])
        db_session.commit()
        
        response = client.get("/api/v1/customer/requests", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(req["customer_id"] == customer_profile.id for req in data)
    
    def test_cancel_customer_request(self, client: TestClient, db_session: Session, auth_headers: dict):
        """Тест отмены заявки заказчиком"""
        customer_profile = CustomerProfileFactory()
        request = RepairRequestFactory(
            customer_id=customer_profile.id,
            status="new"
        )
        db_session.add_all([customer_profile, request])
        db_session.commit()
        
        response = client.delete(f"/api/v1/customer/requests/{request.id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "успешно отменена" in response.json()["message"]
    
    def test_get_customer_statistics(self, client: TestClient, db_session: Session, auth_headers: dict):
        """Тест получения статистики заказчика"""
        customer_profile = CustomerProfileFactory()
        request1 = RepairRequestFactory(customer_id=customer_profile.id, status="new")
        request2 = RepairRequestFactory(customer_id=customer_profile.id, status="completed")
        db_session.add_all([customer_profile, request1, request2])
        db_session.commit()
        
        response = client.get("/api/v1/customer/statistics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_requests"] == 2
        assert data["status_counts"]["new"] == 1
        assert data["status_counts"]["completed"] == 1


class TestSecurityVerificationAPI:
    """Тесты для API проверки безопасности"""
    
    def test_get_pending_verifications(self, client: TestClient, db_session: Session, admin_user: User):
        """Тест получения ожидающих проверок"""
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="pending"
        )
        db_session.add_all([contractor_profile, verification])
        db_session.commit()
        
        # Логинимся как админ
        login_response = client.post("/api/v1/auth/login", json={
            "username": admin_user.username,
            "password": "testpassword"
        })
        admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        response = client.get("/api/v1/security/pending-verifications", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["verification_status"] == "pending"
    
    def test_approve_contractor(self, client: TestClient, db_session: Session, admin_user: User):
        """Тест одобрения исполнителя"""
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="pending"
        )
        db_session.add_all([contractor_profile, verification])
        db_session.commit()
        
        # Логинимся как админ
        login_response = client.post("/api/v1/auth/login", json={
            "username": admin_user.username,
            "password": "testpassword"
        })
        admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        approval_data = {
            "verification_notes": "Approved after background check"
        }
        
        response = client.post(f"/api/v1/security/approve/{verification.id}", json=approval_data, headers=admin_headers)
        
        assert response.status_code == 200
        assert "успешно одобрен" in response.json()["message"]
    
    def test_reject_contractor(self, client: TestClient, db_session: Session, admin_user: User):
        """Тест отклонения исполнителя"""
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="pending"
        )
        db_session.add_all([contractor_profile, verification])
        db_session.commit()
        
        # Логинимся как админ
        login_response = client.post("/api/v1/auth/login", json={
            "username": admin_user.username,
            "password": "testpassword"
        })
        admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        rejection_data = {
            "verification_notes": "Failed background check"
        }
        
        response = client.post(f"/api/v1/security/reject/{verification.id}", json=rejection_data, headers=admin_headers)
        
        assert response.status_code == 200
        assert "отклонен" in response.json()["message"]


class TestHRDocumentsAPI:
    """Тесты для API HR документов"""
    
    def test_get_verified_contractors_for_hr(self, client: TestClient, db_session: Session, admin_user: User):
        """Тест получения проверенных исполнителей для HR"""
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="approved"
        )
        db_session.add_all([contractor_profile, verification])
        db_session.commit()
        
        # Логинимся как админ
        login_response = client.post("/api/v1/auth/login", json={
            "username": admin_user.username,
            "password": "testpassword"
        })
        admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        response = client.get("/api/v1/hr/verified-contractors", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["contractor_id"] == contractor_profile.id
    
    def test_create_document_request(self, client: TestClient, db_session: Session, admin_user: User):
        """Тест создания заявки на документ"""
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="approved"
        )
        db_session.add_all([contractor_profile, verification])
        db_session.commit()
        
        # Логинимся как админ
        login_response = client.post("/api/v1/auth/login", json={
            "username": admin_user.username,
            "password": "testpassword"
        })
        admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        document_data = {
            "document_type": "employment_contract"
        }
        
        response = client.post(f"/api/v1/hr/contractor/{contractor_profile.id}/create-document", 
                             json=document_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "employment_contract"
        assert data["document_status"] == "pending"
    
    def test_get_hr_statistics(self, client: TestClient, db_session: Session, admin_user: User):
        """Тест получения статистики HR"""
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="approved"
        )
        document = HRDocumentFactory(
            contractor_id=contractor_profile.id,
            document_status="completed"
        )
        db_session.add_all([contractor_profile, verification, document])
        db_session.commit()
        
        # Логинимся как админ
        login_response = client.post("/api/v1/auth/login", json={
            "username": admin_user.username,
            "password": "testpassword"
        })
        admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        response = client.get("/api/v1/hr/statistics", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "completion_rate" in data
        assert data["total_documents"] >= 1


class TestTelegramBotAPI:
    """Тесты для API Telegram бота"""
    
    def test_get_bot_info(self, client: TestClient, admin_user: User):
        """Тест получения информации о боте"""
        # Логинимся как админ
        login_response = client.post("/api/v1/auth/login", json={
            "username": admin_user.username,
            "password": "testpassword"
        })
        admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        response = client.get("/api/v1/telegram/bot-info", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "bot_configured" in data
        assert "chat_configured" in data
    
    def test_get_verified_contractors_for_notifications(self, client: TestClient, db_session: Session, admin_user: User):
        """Тест получения проверенных исполнителей для уведомлений"""
        contractor_profile = ContractorProfileFactory(telegram_username="test_user")
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="approved"
        )
        db_session.add_all([contractor_profile, verification])
        db_session.commit()
        
        # Логинимся как админ
        login_response = client.post("/api/v1/auth/login", json={
            "username": admin_user.username,
            "password": "testpassword"
        })
        admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        response = client.get("/api/v1/telegram/verified-contractors", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["telegram_username"] == "test_user"
