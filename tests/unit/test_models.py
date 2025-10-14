"""
Тесты для моделей базы данных
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from models import User, CustomerProfile, ContractorProfile, RepairRequest, SecurityVerification, HRDocument, RequestStatus, UserRole
from tests.factories import UserFactory, CustomerProfileFactory, ContractorProfileFactory, RepairRequestFactory, SecurityVerificationFactory, HRDocumentFactory


class TestUserModel:
    """Тесты для модели User"""
    
    def test_create_user(self, db_session: Session):
        """Тест создания пользователя"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == user.username
        assert user.email == user.email
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_relationships(self, db_session: Session):
        """Тест связей пользователя"""
        user = UserFactory(role="customer")
        customer_profile = CustomerProfileFactory(user_id=user.id)
        db_session.add_all([user, customer_profile])
        db_session.commit()
        
        # Проверяем связь с профилем заказчика
        assert user.customer_profile is not None
        assert user.customer_profile.user_id == user.id
    
    def test_user_role_enum(self):
        """Тест enum ролей пользователя"""
        assert UserRole.ADMIN == "admin"
        assert UserRole.CUSTOMER == "customer"
        assert UserRole.CONTRACTOR == "contractor"
        assert UserRole.MANAGER == "manager"
        assert UserRole.SECURITY == "security"
        assert UserRole.HR == "hr"


class TestCustomerProfileModel:
    """Тесты для модели CustomerProfile"""
    
    def test_create_customer_profile(self, db_session: Session):
        """Тест создания профиля заказчика"""
        user = UserFactory(role="customer")
        profile = CustomerProfileFactory(user_id=user.id)
        db_session.add_all([user, profile])
        db_session.commit()
        
        assert profile.id is not None
        assert profile.user_id == user.id
        assert profile.company_name is not None
        assert profile.contact_person is not None
        assert profile.equipment_brands is not None
        assert profile.equipment_types is not None
        assert profile.mining_operations is not None
    
    def test_customer_profile_relationships(self, db_session: Session):
        """Тест связей профиля заказчика"""
        user = UserFactory(role="customer")
        profile = CustomerProfileFactory(user_id=user.id)
        request = RepairRequestFactory(customer_id=profile.id)
        db_session.add_all([user, profile, request])
        db_session.commit()
        
        # Проверяем связь с пользователем
        assert profile.user is not None
        assert profile.user.id == user.id
        
        # Проверяем связь с заявками
        assert len(profile.requests) == 1
        assert profile.requests[0].id == request.id


class TestContractorProfileModel:
    """Тесты для модели ContractorProfile"""
    
    def test_create_contractor_profile(self, db_session: Session):
        """Тест создания профиля исполнителя"""
        user = UserFactory(role="contractor")
        profile = ContractorProfileFactory(user_id=user.id)
        db_session.add_all([user, profile])
        db_session.commit()
        
        assert profile.id is not None
        assert profile.user_id == user.id
        assert profile.first_name is not None
        assert profile.last_name is not None
        assert profile.specializations is not None
        assert profile.equipment_brands_experience is not None
        assert profile.certifications is not None
        assert profile.work_regions is not None
        assert profile.hourly_rate is not None
        assert profile.availability_status is not None
    
    def test_contractor_profile_relationships(self, db_session: Session):
        """Тест связей профиля исполнителя"""
        user = UserFactory(role="contractor")
        profile = ContractorProfileFactory(user_id=user.id)
        verification = SecurityVerificationFactory(contractor_id=profile.id)
        document = HRDocumentFactory(contractor_id=profile.id)
        db_session.add_all([user, profile, verification, document])
        db_session.commit()
        
        # Проверяем связь с пользователем
        assert profile.user is not None
        assert profile.user.id == user.id


class TestRepairRequestModel:
    """Тесты для модели RepairRequest"""
    
    def test_create_repair_request(self, db_session: Session):
        """Тест создания заявки на ремонт"""
        customer_profile = CustomerProfileFactory()
        request = RepairRequestFactory(customer_id=customer_profile.id)
        db_session.add_all([customer_profile, request])
        db_session.commit()
        
        assert request.id is not None
        assert request.customer_id == customer_profile.id
        assert request.title is not None
        assert request.description is not None
        assert request.status == "new"
        assert request.created_at is not None
    
    def test_repair_request_relationships(self, db_session: Session):
        """Тест связей заявки на ремонт"""
        customer_profile = CustomerProfileFactory()
        manager_user = UserFactory(role="manager")
        contractor_user = UserFactory(role="contractor")
        request = RepairRequestFactory(
            customer_id=customer_profile.id,
            manager_id=manager_user.id,
            assigned_contractor_id=contractor_user.id
        )
        db_session.add_all([customer_profile, manager_user, contractor_user, request])
        db_session.commit()
        
        # Проверяем связь с заказчиком
        assert request.customer is not None
        assert request.customer.id == customer_profile.id
        
        # Проверяем связь с менеджером
        assert request.manager is not None
        assert request.manager.id == manager_user.id
        
        # Проверяем связь с назначенным исполнителем
        assert request.assigned_contractor is not None
        assert request.assigned_contractor.id == contractor_user.id
    
    def test_request_status_enum(self):
        """Тест enum статусов заявки"""
        assert RequestStatus.NEW == "new"
        assert RequestStatus.MANAGER_REVIEW == "manager_review"
        assert RequestStatus.CLARIFICATION == "clarification"
        assert RequestStatus.SENT_TO_CONTRACTORS == "sent_to_contractors"
        assert RequestStatus.CONTRACTOR_RESPONSES == "contractor_responses"
        assert RequestStatus.ASSIGNED == "assigned"
        assert RequestStatus.IN_PROGRESS == "in_progress"
        assert RequestStatus.COMPLETED == "completed"
        assert RequestStatus.CANCELLED == "cancelled"


class TestSecurityVerificationModel:
    """Тесты для модели SecurityVerification"""
    
    def test_create_security_verification(self, db_session: Session):
        """Тест создания проверки безопасности"""
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(contractor_id=contractor_profile.id)
        db_session.add_all([contractor_profile, verification])
        db_session.commit()
        
        assert verification.id is not None
        assert verification.contractor_id == contractor_profile.id
        assert verification.verification_status in ["pending", "approved", "rejected"]
        assert verification.created_at is not None
    
    def test_security_verification_relationships(self, db_session: Session):
        """Тест связей проверки безопасности"""
        contractor_profile = ContractorProfileFactory()
        security_officer = UserFactory(role="security")
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            checked_by=security_officer.id
        )
        db_session.add_all([contractor_profile, security_officer, verification])
        db_session.commit()
        
        # Проверяем связь с исполнителем
        assert verification.contractor is not None
        assert verification.contractor.id == contractor_profile.id
        
        # Проверяем связь с сотрудником безопасности
        assert verification.security_officer is not None
        assert verification.security_officer.id == security_officer.id


class TestHRDocumentModel:
    """Тесты для модели HRDocument"""
    
    def test_create_hr_document(self, db_session: Session):
        """Тест создания HR документа"""
        contractor_profile = ContractorProfileFactory()
        hr_officer = UserFactory(role="hr")
        document = HRDocumentFactory(
            contractor_id=contractor_profile.id,
            generated_by=hr_officer.id
        )
        db_session.add_all([contractor_profile, hr_officer, document])
        db_session.commit()
        
        assert document.id is not None
        assert document.contractor_id == contractor_profile.id
        assert document.document_type in ["employment_contract", "service_agreement", "nda_agreement", "safety_instruction", "equipment_certificate"]
        assert document.document_status in ["pending", "generated", "completed"]
        assert document.created_at is not None
    
    def test_hr_document_relationships(self, db_session: Session):
        """Тест связей HR документа"""
        contractor_profile = ContractorProfileFactory()
        hr_officer = UserFactory(role="hr")
        document = HRDocumentFactory(
            contractor_id=contractor_profile.id,
            generated_by=hr_officer.id
        )
        db_session.add_all([contractor_profile, hr_officer, document])
        db_session.commit()
        
        # Проверяем связь с исполнителем
        assert document.contractor is not None
        assert document.contractor.id == contractor_profile.id
        
        # Проверяем связь с HR сотрудником
        assert document.hr_officer is not None
        assert document.hr_officer.id == hr_officer.id


class TestModelConstraints:
    """Тесты для ограничений моделей"""
    
    def test_user_unique_constraints(self, db_session: Session):
        """Тест уникальных ограничений пользователя"""
        user1 = UserFactory(username="testuser", email="test@example.com")
        db_session.add(user1)
        db_session.commit()
        
        # Попытка создать пользователя с тем же username
        user2 = UserFactory(username="testuser", email="different@example.com")
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Должно быть исключение из-за нарушения уникальности
            db_session.commit()
        
        db_session.rollback()
        
        # Попытка создать пользователя с тем же email
        user3 = UserFactory(username="differentuser", email="test@example.com")
        db_session.add(user3)
        
        with pytest.raises(Exception):  # Должно быть исключение из-за нарушения уникальности
            db_session.commit()
    
    def test_customer_profile_unique_user_id(self, db_session: Session):
        """Тест уникальности user_id в профиле заказчика"""
        user = UserFactory(role="customer")
        profile1 = CustomerProfileFactory(user_id=user.id)
        db_session.add_all([user, profile1])
        db_session.commit()
        
        # Попытка создать второй профиль для того же пользователя
        profile2 = CustomerProfileFactory(user_id=user.id)
        db_session.add(profile2)
        
        with pytest.raises(Exception):  # Должно быть исключение из-за нарушения уникальности
            db_session.commit()
    
    def test_contractor_profile_unique_user_id(self, db_session: Session):
        """Тест уникальности user_id в профиле исполнителя"""
        user = UserFactory(role="contractor")
        profile1 = ContractorProfileFactory(user_id=user.id)
        db_session.add_all([user, profile1])
        db_session.commit()
        
        # Попытка создать второй профиль для того же пользователя
        profile2 = ContractorProfileFactory(user_id=user.id)
        db_session.add(profile2)
        
        with pytest.raises(Exception):  # Должно быть исключение из-за нарушения уникальности
            db_session.commit()
