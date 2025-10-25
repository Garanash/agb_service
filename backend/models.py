from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, BigInteger, Float, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base
import enum
import datetime

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"  # Заказчик (компания)
    CONTRACTOR = "contractor"  # Исполнитель (физлицо)
    SERVICE_ENGINEER = "service_engineer"  # Сервисный инженер
    MANAGER = "manager"  # Менеджер сервиса
    SECURITY = "security"  # Служба безопасности
    HR = "hr"  # Отдел кадров

class RequestStatus(str, enum.Enum):
    NEW = "new"
    MANAGER_REVIEW = "manager_review"
    CLARIFICATION = "clarification"
    SENT_TO_CONTRACTORS = "sent_to_contractors"
    CONTRACTOR_RESPONSES = "contractor_responses"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    """Пользователи системы агрегатора"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_password_changed = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    position = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи с профилями
    customer_profile = relationship("CustomerProfile", back_populates="user", lazy="selectin", uselist=False, foreign_keys="CustomerProfile.user_id")
    contractor_profile = relationship("ContractorProfile", back_populates="user", lazy="selectin", uselist=False, foreign_keys="ContractorProfile.user_id")

class CustomerProfile(Base):
    """Профиль заказчика (компания)"""
    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Данные компании
    company_name = Column(String, nullable=False)
    contact_person = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    address = Column(String, nullable=True)
    inn = Column(String, nullable=True)  # ИНН
    kpp = Column(String, nullable=True)  # КПП
    ogrn = Column(String, nullable=True)  # ОГРН
    
    # Новые поля для горнодобывающей техники
    equipment_brands = Column(JSON, nullable=True)  # Бренды техники
    equipment_types = Column(JSON, nullable=True)  # Типы оборудования
    mining_operations = Column(JSON, nullable=True)  # Виды горных работ
    service_history = Column(Text, nullable=True)  # История обслуживания

    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    user = relationship("User", back_populates="customer_profile", lazy="selectin", foreign_keys=[user_id])
    requests = relationship("RepairRequest", back_populates="customer", lazy="selectin")

class ContractorProfile(Base):
    """Профиль исполнителя (физлицо)"""
    __tablename__ = "contractor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Личные данные
    last_name = Column(String, nullable=True, default=None)
    first_name = Column(String, nullable=True, default=None)
    patronymic = Column(String, nullable=True, default=None)
    phone = Column(String, nullable=True, default=None)
    email = Column(String, nullable=True, default=None)

    # Паспортные данные (обязательно для СБ)
    passport_series = Column(String, nullable=True)
    passport_number = Column(String, nullable=True)
    passport_issued_by = Column(String, nullable=True)
    passport_issued_date = Column(String, nullable=True)
    passport_issued_code = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    birth_place = Column(String, nullable=True)
    
    # ИНН (обязательно для СБ)
    inn = Column(String, nullable=True)
    
    # Профессиональная информация (JSON массив)
    professional_info = Column(JSON, nullable=True, default=list)

    # Банковские данные
    bank_name = Column(String, nullable=True)
    bank_account = Column(String, nullable=True)
    bank_bik = Column(String, nullable=True)

    # Контакты
    telegram_username = Column(String, nullable=True)
    website = Column(String, nullable=True)

    # Общее описание
    general_description = Column(String, nullable=True, default=None)

    # Файлы
    profile_photo_path = Column(String, nullable=True, default=None)
    portfolio_files = Column(JSON, nullable=True, default=list)
    document_files = Column(JSON, nullable=True, default=list)
    
    # Новые поля для специализации по обслуживанию техники
    specializations = Column(JSON, nullable=True)  # Специализации
    equipment_brands_experience = Column(JSON, nullable=True)  # Опыт с брендами
    certifications = Column(JSON, nullable=True)  # Сертификаты
    work_regions = Column(JSON, nullable=True)  # Регионы работы
    hourly_rate = Column(Float, nullable=True)  # Почасовая ставка
    availability_status = Column(String, nullable=True, default="available")  # Статус доступности

    # Статус верификации
    profile_completion_status = Column(String, nullable=True, default="incomplete")  # incomplete, pending_security, pending_manager, approved, rejected
    security_verified = Column(Boolean, default=False)
    manager_verified = Column(Boolean, default=False)
    security_verified_at = Column(DateTime(timezone=True), nullable=True)
    manager_verified_at = Column(DateTime(timezone=True), nullable=True)
    security_verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    manager_verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    user = relationship("User", back_populates="contractor_profile", lazy="selectin", foreign_keys=[user_id])
    responses = relationship("ContractorResponse", back_populates="contractor", lazy="selectin")
    education_records = relationship("ContractorEducation", back_populates="contractor", lazy="selectin")
    documents = relationship("ContractorDocument", back_populates="contractor", lazy="selectin")

class RepairRequest(Base):
    """Заявка на ремонт"""
    __tablename__ = "repair_requests"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer_profiles.id"), nullable=False)

    # Основная информация
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    urgency = Column(String, nullable=True)  # срочно, средне, не срочно
    preferred_date = Column(DateTime, nullable=True)

    # Местоположение
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    region = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)  # Широта места выполнения работ
    longitude = Column(Float, nullable=True)  # Долгота места выполнения работ

    # Технические детали (заполняются сервисным инженером)
    equipment_type = Column(String, nullable=True)
    equipment_brand = Column(String, nullable=True)
    equipment_model = Column(String, nullable=True)
    problem_description = Column(String, nullable=True)
    priority = Column(String, nullable=True, default="normal")  # Приоритет заявки
    
    # Поля для менеджера
    manager_comment = Column(String, nullable=True)
    clarification_details = Column(Text, nullable=True)  # Уточненные детали от заказчика
    estimated_cost = Column(Integer, nullable=True)  # в рублях
    final_price = Column(Integer, nullable=True)
    sent_to_bot_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_date = Column(DateTime, nullable=True)  # Запланированная дата выполнения

    # Статусы
    status = Column(String, default=RequestStatus.NEW)
    service_engineer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_contractor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Менеджер, работающий с заявкой

    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)

    # Связи
    customer = relationship("CustomerProfile", back_populates="requests", lazy="selectin")
    service_engineer = relationship("User", foreign_keys=[service_engineer_id], lazy="selectin")
    assigned_contractor = relationship("User", foreign_keys=[assigned_contractor_id], lazy="selectin")
    manager = relationship("User", foreign_keys=[manager_id], lazy="selectin")
    responses = relationship("ContractorResponse", back_populates="request", lazy="selectin")

class ContractorResponse(Base):
    """Отклик исполнителя на заявку"""
    __tablename__ = "contractor_responses"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("repair_requests.id"), nullable=False)
    contractor_id = Column(Integer, ForeignKey("contractor_profiles.id"), nullable=False)

    # Информация об отклике
    proposed_price = Column(Integer, nullable=True)
    estimated_time = Column(String, nullable=True)  # "2-3 дня", "1 неделя" и т.д.
    comment = Column(String, nullable=True)
    is_accepted = Column(Boolean, default=False)

    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    request = relationship("RepairRequest", back_populates="responses", lazy="selectin")
    contractor = relationship("ContractorProfile", back_populates="responses", lazy="selectin")

class TelegramUser(Base):
    """Telegram пользователи для уведомлений"""
    __tablename__ = "telegram_users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    user = relationship("User", lazy="selectin")
    messages = relationship("TelegramMessage", back_populates="telegram_user", lazy="selectin")

class TelegramMessage(Base):
    """Сообщения Telegram бота"""
    __tablename__ = "telegram_messages"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, ForeignKey("telegram_users.id"), nullable=False)
    message_text = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, photo, document, etc.
    is_from_bot = Column(Boolean, default=False)  # True если сообщение от бота к пользователю
    is_read = Column(Boolean, default=False)  # True если сообщение прочитано
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    telegram_user = relationship("TelegramUser", back_populates="messages", lazy="selectin")

class ArticleMapping(Base):
    """Сопоставление артикулов для технических заявок"""
    __tablename__ = "article_mappings"

    id = Column(Integer, primary_key=True, index=True)
    contractor_article = Column(String, nullable=False, index=True)
    contractor_description = Column(String, nullable=False)
    agb_article = Column(String, nullable=False, index=True)
    agb_description = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ContractorRequest(Base):
    """Заявки от контрагентов на сопоставление артикулов"""
    __tablename__ = "contractor_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String, nullable=False, unique=True, index=True)
    contractor_name = Column(String, nullable=False)
    request_date = Column(DateTime, nullable=False)
    status = Column(String, default="new")
    total_items = Column(Integer, default=0)
    matched_items = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Связи
    creator = relationship("User", foreign_keys=[created_by], lazy="selectin")
    processor = relationship("User", foreign_keys=[processed_by], lazy="selectin")
    items = relationship("ContractorRequestItem", back_populates="request", lazy="selectin")

class ContractorRequestItem(Base):
    """Позиции в заявке контрагента"""
    __tablename__ = "contractor_request_items"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("contractor_requests.id"), nullable=False)
    contractor_article = Column(String, nullable=False)
    contractor_description = Column(String, nullable=False)
    agb_article = Column(String, nullable=True)
    agb_description = Column(String, nullable=True)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    request = relationship("ContractorRequest", back_populates="items", lazy="selectin")

# Новые модели для системы безопасности и HR
class SecurityVerification(Base):
    """Проверка исполнителей службой безопасности"""
    __tablename__ = "security_verifications"

    id = Column(Integer, primary_key=True, index=True)
    contractor_id = Column(Integer, ForeignKey("contractor_profiles.id"), nullable=False)
    verification_status = Column(String, nullable=False, default="pending")  # pending, approved, rejected
    verification_notes = Column(Text, nullable=True)
    checked_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # ID сотрудника службы безопасности
    checked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    contractor = relationship("ContractorProfile", lazy="selectin")
    security_officer = relationship("User", lazy="selectin")

class HRDocument(Base):
    """Документы HR для исполнителей"""
    __tablename__ = "hr_documents"

    id = Column(Integer, primary_key=True, index=True)
    contractor_id = Column(Integer, ForeignKey("contractor_profiles.id"), nullable=False)
    document_type = Column(String, nullable=False)  # Тип документа
    document_status = Column(String, nullable=False, default="pending")  # Статус документа
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # ID сотрудника HR
    generated_at = Column(DateTime(timezone=True), nullable=True)
    document_path = Column(String, nullable=True)  # Путь к файлу документа
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    contractor = relationship("ContractorProfile", lazy="selectin")
    hr_officer = relationship("User", lazy="selectin")

class ContractorEducation(Base):
    """Образование исполнителя"""
    __tablename__ = "contractor_education"

    id = Column(Integer, primary_key=True, index=True)
    contractor_id = Column(Integer, ForeignKey("contractor_profiles.id"), nullable=False)
    
    # Данные об образовании
    institution_name = Column(String, nullable=False)  # Название учебного заведения
    degree = Column(String, nullable=False)  # Степень/квалификация
    specialization = Column(String, nullable=False)  # Специализация
    graduation_year = Column(Integer, nullable=True)  # Год окончания
    diploma_number = Column(String, nullable=True)  # Номер диплома
    document_path = Column(String, nullable=True)  # Путь к файлу диплома
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    contractor = relationship("ContractorProfile", back_populates="education_records", lazy="selectin")

class ContractorDocument(Base):
    """Документы исполнителя"""
    __tablename__ = "contractor_documents"

    id = Column(Integer, primary_key=True, index=True)
    contractor_id = Column(Integer, ForeignKey("contractor_profiles.id"), nullable=False)
    
    # Данные о документе
    document_type = Column(String, nullable=False)  # Тип документа (passport, inn, safety_certificate, etc.)
    document_name = Column(String, nullable=False)  # Название документа
    document_path = Column(String, nullable=False)  # Путь к файлу
    file_size = Column(Integer, nullable=True)  # Размер файла в байтах
    mime_type = Column(String, nullable=True)  # MIME тип файла
    
    # Статус проверки
    verification_status = Column(String, nullable=False, default="pending")  # pending, approved, rejected
    verification_notes = Column(Text, nullable=True)  # Комментарии при проверке
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Кто проверил
    verified_at = Column(DateTime(timezone=True), nullable=True)  # Когда проверили
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    contractor = relationship("ContractorProfile", back_populates="documents", lazy="selectin")
    verifier = relationship("User", lazy="selectin")

class ContractorVerification(Base):
    """Общая верификация исполнителя"""
    __tablename__ = "contractor_verifications"

    id = Column(Integer, primary_key=True, index=True)
    contractor_id = Column(Integer, ForeignKey("contractor_profiles.id"), nullable=False, unique=True)
    
    # Статусы проверки
    profile_completed = Column(Boolean, default=False)  # Профиль заполнен
    documents_uploaded = Column(Boolean, default=False)  # Документы загружены
    security_check_passed = Column(Boolean, default=False)  # Проверка СБ пройдена
    manager_approval = Column(Boolean, default=False)  # Одобрение менеджера
    
    # Общий статус
    overall_status = Column(String, nullable=False, default="incomplete")  # incomplete, pending_security, pending_manager, approved, rejected
    
    # Комментарии
    security_notes = Column(Text, nullable=True)
    manager_notes = Column(Text, nullable=True)
    
    # Кто проверял
    security_checked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    manager_checked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    security_checked_at = Column(DateTime(timezone=True), nullable=True)
    manager_checked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    contractor = relationship("ContractorProfile", lazy="selectin")
    security_officer = relationship("User", foreign_keys=[security_checked_by], lazy="selectin")
    manager = relationship("User", foreign_keys=[manager_checked_by], lazy="selectin")
