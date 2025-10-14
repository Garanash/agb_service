"""
Unit тесты для сервисов
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from services.email_service import EmailService
from services.telegram_bot_service import TelegramBotService
from services.security_verification_service import SecurityVerificationService
from services.hr_document_service import HRDocumentService
from services.request_workflow_service import RequestWorkflowService
from models import User, CustomerProfile, ContractorProfile, RepairRequest, SecurityVerification, HRDocument, RequestStatus
from tests.factories import UserFactory, CustomerProfileFactory, ContractorProfileFactory, RepairRequestFactory, SecurityVerificationFactory, HRDocumentFactory


class TestEmailService:
    """Тесты для EmailService"""
    
    def test_email_service_initialization(self):
        """Тест инициализации EmailService"""
        service = EmailService()
        assert service.smtp_server == "smtp.mail.ru"
        assert service.smtp_port == 465
        assert service.mail_from_name == "AGB SERVICE"
    
    @patch('services.email_service.smtplib.SMTP_SSL')
    def test_send_email_success(self, mock_smtp):
        """Тест успешной отправки email"""
        service = EmailService()
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = service.send_email(
            recipients=["test@example.com"],
            subject="Test Subject",
            html_content="<h1>Test</h1>",
            text_content="Test"
        )
        
        assert result is True
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('services.email_service.smtplib.SMTP_SSL')
    def test_send_email_failure(self, mock_smtp):
        """Тест неудачной отправки email"""
        service = EmailService()
        mock_smtp.side_effect = Exception("SMTP Error")
        
        result = service.send_email(
            recipients=["test@example.com"],
            subject="Test Subject",
            html_content="<h1>Test</h1>"
        )
        
        assert result is False
    
    def test_send_welcome_email(self):
        """Тест отправки приветственного письма"""
        service = EmailService()
        
        with patch.object(service, 'send_email', return_value=True) as mock_send:
            result = service.send_welcome_email(
                user_email="test@example.com",
                user_name="Test User",
                user_role="customer"
            )
            
            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert call_args[1]['recipients'] == ["test@example.com"]
            assert "Добро пожаловать" in call_args[1]['subject']
    
    def test_send_email_verification(self):
        """Тест отправки письма подтверждения email"""
        service = EmailService()
        
        with patch.object(service, 'send_email', return_value=True) as mock_send:
            result = service.send_email_verification(
                user_email="test@example.com",
                user_name="Test User",
                verification_token="test_token"
            )
            
            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert call_args[1]['recipients'] == ["test@example.com"]
            assert "Подтверждение email" in call_args[1]['subject']


class TestTelegramBotService:
    """Тесты для TelegramBotService"""
    
    def test_telegram_service_initialization(self):
        """Тест инициализации TelegramBotService"""
        mock_db = Mock()
        service = TelegramBotService(mock_db)
        
        assert service.bot_token is None  # В тестах токен не установлен
        assert service.base_url == "https://api.telegram.org/botNone"
    
    @patch('services.telegram_bot_service.aiohttp.ClientSession')
    async def test_send_message_success(self, mock_session):
        """Тест успешной отправки сообщения"""
        mock_db = Mock()
        service = TelegramBotService(mock_db)
        service.bot_token = "test_token"
        service.base_url = "https://api.telegram.org/bot/test_token"
        
        mock_response = Mock()
        mock_response.status = 200
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await service._send_message("test_chat_id", "Test message")
        
        assert result is True
    
    @patch('services.telegram_bot_service.aiohttp.ClientSession')
    async def test_send_message_failure(self, mock_session):
        """Тест неудачной отправки сообщения"""
        mock_db = Mock()
        service = TelegramBotService(mock_db)
        service.bot_token = "test_token"
        
        mock_response = Mock()
        mock_response.status = 400
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await service._send_message("test_chat_id", "Test message")
        
        assert result is False
    
    def test_format_request_message(self):
        """Тест форматирования сообщения о заявке"""
        mock_db = Mock()
        service = TelegramBotService(mock_db)
        
        request = RepairRequestFactory.build(
            id=123,
            title="Test Request",
            description="Test description",
            equipment_type="Excavator",
            equipment_brand="Caterpillar",
            urgency="high",
            priority="urgent"
        )
        
        message = service._format_request_message(request)
        
        assert "НОВАЯ ЗАЯВКА НА СЕРВИС" in message
        assert "Заявка #123" in message
        assert "Test Request" in message
        assert "Excavator" in message
        assert "Caterpillar" in message
        assert "Высокая" in message  # urgency
        assert "Срочный" in message  # priority


class TestSecurityVerificationService:
    """Тесты для SecurityVerificationService"""
    
    def test_create_verification_request(self, db_session: Session):
        """Тест создания заявки на проверку"""
        contractor_profile = ContractorProfileFactory()
        db_session.add(contractor_profile)
        db_session.commit()
        
        service = SecurityVerificationService(db_session)
        verification = service.create_verification_request(contractor_profile.id)
        
        assert verification.contractor_id == contractor_profile.id
        assert verification.verification_status == "pending"
        assert verification.created_at is not None
    
    def test_approve_contractor(self, db_session: Session):
        """Тест одобрения исполнителя"""
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="pending"
        )
        db_session.add_all([contractor_profile, verification])
        db_session.commit()
        
        service = SecurityVerificationService(db_session)
        result = service.approve_contractor(verification.id, 1, "Approved")
        
        assert result.verification_status == "approved"
        assert result.checked_by == 1
        assert result.verification_notes == "Approved"
        assert result.checked_at is not None
    
    def test_reject_contractor(self, db_session: Session):
        """Тест отклонения исполнителя"""
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="pending"
        )
        db_session.add_all([contractor_profile, verification])
        db_session.commit()
        
        service = SecurityVerificationService(db_session)
        result = service.reject_contractor(verification.id, 1, "Rejected")
        
        assert result.verification_status == "rejected"
        assert result.checked_by == 1
        assert result.verification_notes == "Rejected"
        assert result.checked_at is not None
    
    def test_check_contractor_can_respond(self, db_session: Session):
        """Тест проверки возможности отклика исполнителя"""
        contractor_profile = ContractorProfileFactory()
        
        # Случай 1: Нет проверки
        service = SecurityVerificationService(db_session)
        assert service.check_contractor_can_respond(contractor_profile.id) is False
        
        # Случай 2: Проверка одобрена
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="approved"
        )
        db_session.add(verification)
        db_session.commit()
        
        assert service.check_contractor_can_respond(contractor_profile.id) is True
        
        # Случай 3: Проверка отклонена
        verification.verification_status = "rejected"
        db_session.commit()
        
        assert service.check_contractor_can_respond(contractor_profile.id) is False


class TestHRDocumentService:
    """Тесты для HRDocumentService"""
    
    def test_create_document_request(self, db_session: Session):
        """Тест создания заявки на документ"""
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="approved"
        )
        db_session.add_all([contractor_profile, verification])
        db_session.commit()
        
        service = HRDocumentService(db_session)
        document = service.create_document_request(
            contractor_profile.id,
            "employment_contract",
            1
        )
        
        assert document.contractor_id == contractor_profile.id
        assert document.document_type == "employment_contract"
        assert document.document_status == "pending"
        assert document.generated_by == 1
    
    def test_generate_document(self, db_session: Session):
        """Тест генерации документа"""
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="approved"
        )
        document = HRDocumentFactory(
            contractor_id=contractor_profile.id,
            document_type="employment_contract",
            document_status="pending"
        )
        db_session.add_all([contractor_profile, verification, document])
        db_session.commit()
        
        service = HRDocumentService(db_session)
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = service.generate_document(document.id, 1)
            
            assert result.document_status == "generated"
            assert result.generated_by == 1
            assert result.generated_at is not None
            assert result.document_path is not None
    
    def test_complete_document(self, db_session: Session):
        """Тест завершения документа"""
        document = HRDocumentFactory(document_status="generated")
        db_session.add(document)
        db_session.commit()
        
        service = HRDocumentService(db_session)
        result = service.complete_document(document.id, 1)
        
        assert result.document_status == "completed"


class TestRequestWorkflowService:
    """Тесты для RequestWorkflowService"""
    
    def test_create_request(self, db_session: Session):
        """Тест создания заявки"""
        customer_profile = CustomerProfileFactory()
        db_session.add(customer_profile)
        db_session.commit()
        
        service = RequestWorkflowService(db_session)
        request = service.create_request(
            customer_profile.id,
            "Test Request",
            "Test description",
            "medium",
            datetime.now(timezone.utc) + timedelta(days=1),
            "Test Address",
            "Test City",
            "Test Region",
            "Excavator",
            "Caterpillar",
            "CAT 320",
            "Test problem",
            "normal"
        )
        
        assert request.customer_id == customer_profile.id
        assert request.title == "Test Request"
        assert request.description == "Test description"
        assert request.status == RequestStatus.NEW
    
    def test_assign_to_manager(self, db_session: Session):
        """Тест назначения заявки менеджеру"""
        customer_profile = CustomerProfileFactory()
        manager_user = UserFactory(role="manager")
        request = RepairRequestFactory(
            customer_id=customer_profile.id,
            status=RequestStatus.NEW
        )
        db_session.add_all([customer_profile, manager_user, request])
        db_session.commit()
        
        service = RequestWorkflowService(db_session)
        result = service.assign_to_manager(request.id, manager_user.id)
        
        assert result.manager_id == manager_user.id
        assert result.status == RequestStatus.MANAGER_REVIEW
    
    def test_add_clarification(self, db_session: Session):
        """Тест добавления уточнений"""
        customer_profile = CustomerProfileFactory()
        manager_user = UserFactory(role="manager")
        request = RepairRequestFactory(
            customer_id=customer_profile.id,
            manager_id=manager_user.id,
            status=RequestStatus.MANAGER_REVIEW
        )
        db_session.add_all([customer_profile, manager_user, request])
        db_session.commit()
        
        service = RequestWorkflowService(db_session)
        result = service.add_clarification(request.id, manager_user.id, "Test clarification")
        
        assert result.clarification_details == "Test clarification"
        assert result.status == RequestStatus.CLARIFICATION
    
    def test_assign_contractor(self, db_session: Session):
        """Тест назначения исполнителя"""
        customer_profile = CustomerProfileFactory()
        manager_user = UserFactory(role="manager")
        contractor_profile = ContractorProfileFactory()
        verification = SecurityVerificationFactory(
            contractor_id=contractor_profile.id,
            verification_status="approved"
        )
        request = RepairRequestFactory(
            customer_id=customer_profile.id,
            manager_id=manager_user.id,
            status=RequestStatus.MANAGER_REVIEW
        )
        db_session.add_all([customer_profile, manager_user, contractor_profile, verification, request])
        db_session.commit()
        
        service = RequestWorkflowService(db_session)
        
        with patch('services.request_workflow_service.get_security_verification_service') as mock_security:
            mock_security.return_value.check_contractor_can_respond.return_value = True
            
            result = service.assign_contractor(request.id, contractor_profile.id, manager_user.id)
            
            assert result.assigned_contractor_id == contractor_profile.id
            assert result.status == RequestStatus.ASSIGNED
            assert result.assigned_at is not None


def mock_open():
    """Мок для функции open"""
    from unittest.mock import mock_open as _mock_open
    return _mock_open(read_data="Test document content")
