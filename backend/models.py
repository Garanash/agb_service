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

class RequestStatus(str, enum.Enum):
    NEW = "new"
    PROCESSING = "processing"
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
    customer_profile = relationship("CustomerProfile", back_populates="user", lazy="selectin", uselist=False)
    contractor_profile = relationship("ContractorProfile", back_populates="user", lazy="selectin", uselist=False)

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

    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    user = relationship("User", back_populates="customer_profile", lazy="selectin")
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

    # Профессиональная информация (JSON массив)
    professional_info = Column(JSON, nullable=True, default=list)

    # Образование (JSON массив)
    education = Column(JSON, nullable=True, default=list)

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

    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    user = relationship("User", back_populates="contractor_profile", lazy="selectin")
    responses = relationship("ContractorResponse", back_populates="contractor", lazy="selectin")

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

    # Технические детали (заполняются сервисным инженером)
    equipment_type = Column(String, nullable=True)
    equipment_brand = Column(String, nullable=True)
    equipment_model = Column(String, nullable=True)
    problem_description = Column(String, nullable=True)
    estimated_cost = Column(Integer, nullable=True)  # в рублях
    
    # Дополнительная информация от менеджера сервиса
    manager_comment = Column(String, nullable=True)
    final_price = Column(Integer, nullable=True)
    sent_to_bot_at = Column(DateTime(timezone=True), nullable=True)

    # Статусы
    status = Column(String, default=RequestStatus.NEW)
    service_engineer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_contractor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)

    # Связи
    customer = relationship("CustomerProfile", back_populates="requests", lazy="selectin")
    service_engineer = relationship("User", foreign_keys=[service_engineer_id], lazy="selectin")
    assigned_contractor = relationship("User", foreign_keys=[assigned_contractor_id], lazy="selectin")
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
