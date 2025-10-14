from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    CONTRACTOR = "contractor"
    SERVICE_ENGINEER = "service_engineer"
    MANAGER = "manager"
    SECURITY = "security"
    HR = "hr"

class RequestStatus(str, Enum):
    NEW = "new"
    MANAGER_REVIEW = "manager_review"
    CLARIFICATION = "clarification"
    SENT_TO_CONTRACTORS = "sent_to_contractors"
    CONTRACTOR_RESPONSES = "contractor_responses"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Пользователи
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    position: Optional[str] = Field(None, max_length=200)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole

# Расширенные схемы для регистрации
class CustomerRegistrationRequest(UserBase):
    password: str = Field(..., min_length=6)
    company_name: str = Field(..., min_length=1, max_length=200)
    region: str = Field(..., min_length=1, max_length=100)
    inn_or_ogrn: str = Field(..., min_length=10, max_length=15)
    # Новые поля для горнодобывающей техники
    equipment_brands: Optional[List[str]] = Field(None)
    equipment_types: Optional[List[str]] = Field(None)
    mining_operations: Optional[List[str]] = Field(None)
    service_history: Optional[str] = Field(None, max_length=1000)

class ContractorRegistrationRequest(UserBase):
    password: str = Field(..., min_length=6)
    # Новые поля для специализации
    specializations: Optional[List[str]] = Field(None)
    equipment_brands_experience: Optional[List[str]] = Field(None)
    certifications: Optional[List[str]] = Field(None)
    work_regions: Optional[List[str]] = Field(None)
    hourly_rate: Optional[float] = Field(None, ge=0)
    telegram_username: Optional[str] = Field(None, max_length=100)

class UserResponse(UserBase):
    class Config:
        orm_mode = True
    
    id: int
    role: str
    is_active: bool
    is_password_changed: Optional[bool] = False
    email_verified: Optional[bool] = False
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Профили заказчиков
class CustomerProfileBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    contact_person: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=10, max_length=20)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    address: Optional[str] = Field(None, max_length=500)
    inn: Optional[str] = Field(None, max_length=12)
    kpp: Optional[str] = Field(None, max_length=9)
    ogrn: Optional[str] = Field(None, max_length=15)
    # Новые поля для горнодобывающей техники
    equipment_brands: Optional[List[str]] = Field(None, description="Бренды техники (Алмазгеобур, Эпирог, Бортлангир и т.д.)")
    equipment_types: Optional[List[str]] = Field(None, description="Типы оборудования")
    mining_operations: Optional[List[str]] = Field(None, description="Виды горных работ")
    service_history: Optional[str] = Field(None, max_length=1000, description="История обслуживания")

class CustomerProfileCreate(CustomerProfileBase):
    pass

class CustomerProfileResponse(CustomerProfileBase):
    class Config:
        orm_mode = True
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Профили исполнителей
class ContractorProfileBase(BaseModel):
    last_name: Optional[str] = Field(None, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    patronymic: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    professional_info: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    education: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    bank_name: Optional[str] = Field(None, max_length=200)
    bank_account: Optional[str] = Field(None, max_length=20)
    bank_bik: Optional[str] = Field(None, max_length=9)
    telegram_username: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    general_description: Optional[str] = Field(None, max_length=1000)
    profile_photo_path: Optional[str] = None
    portfolio_files: Optional[List[str]] = Field(default_factory=list)
    document_files: Optional[List[str]] = Field(default_factory=list)
    # Новые поля для специализации по обслуживанию техники
    specializations: Optional[List[str]] = Field(None, description="Специализации (электрика, ходовая часть, гидравлика и т.д.)")
    equipment_brands_experience: Optional[List[str]] = Field(None, description="Опыт работы с брендами техники")
    certifications: Optional[List[str]] = Field(None, description="Сертификаты и квалификации")
    work_regions: Optional[List[str]] = Field(None, description="Регионы работы")
    hourly_rate: Optional[float] = Field(None, description="Почасовая ставка")
    availability_status: Optional[str] = Field("available", description="Статус доступности")

class ContractorProfileCreate(ContractorProfileBase):
    pass

class ContractorProfileResponse(ContractorProfileBase):
    class Config:
        orm_mode = True
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Заявки на ремонт
class RepairRequestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    urgency: Optional[str] = Field(None, max_length=50)
    preferred_date: Optional[datetime] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    # Новые поля для горнодобывающей техники
    equipment_type: Optional[str] = Field(None, max_length=200, description="Тип оборудования")
    equipment_brand: Optional[str] = Field(None, max_length=200, description="Бренд оборудования")
    equipment_model: Optional[str] = Field(None, max_length=200, description="Модель оборудования")
    problem_description: Optional[str] = Field(None, max_length=2000, description="Описание неисправности")
    priority: Optional[str] = Field("normal", description="Приоритет заявки")

class RepairRequestCreate(RepairRequestBase):
    pass

class RepairRequestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    urgency: Optional[str] = Field(None, max_length=50)
    preferred_date: Optional[datetime] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    equipment_type: Optional[str] = Field(None, max_length=200)
    equipment_brand: Optional[str] = Field(None, max_length=200)
    equipment_model: Optional[str] = Field(None, max_length=200)
    problem_description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[str] = Field(None, description="Приоритет заявки")
    # Поля для менеджера
    manager_comment: Optional[str] = Field(None, max_length=2000, description="Комментарий менеджера")
    clarification_details: Optional[str] = Field(None, max_length=2000, description="Уточненные детали от заказчика")
    estimated_cost: Optional[int] = Field(None, ge=0, description="Предварительная стоимость")
    final_price: Optional[int] = Field(None, ge=0, description="Итоговая стоимость")
    assigned_contractor_id: Optional[int] = Field(None, description="Назначенный исполнитель")
    scheduled_date: Optional[datetime] = Field(None, description="Запланированная дата выполнения")
    status: Optional[RequestStatus] = None

class RepairRequestResponse(RepairRequestBase):
    class Config:
        orm_mode = True
    
    id: int
    customer_id: int
    equipment_type: Optional[str] = None
    equipment_brand: Optional[str] = None
    equipment_model: Optional[str] = None
    problem_description: Optional[str] = None
    estimated_cost: Optional[int] = None
    manager_comment: Optional[str] = None
    final_price: Optional[int] = None
    sent_to_bot_at: Optional[datetime] = None
    status: str
    service_engineer_id: Optional[int] = None
    assigned_contractor_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    assigned_at: Optional[datetime] = None
    
    # Связанные объекты
    customer: Optional[CustomerProfileResponse] = None
    service_engineer: Optional[UserResponse] = None
    assigned_contractor: Optional[UserResponse] = None
    responses: Optional[List['ContractorResponseResponse']] = None

# Отклики исполнителей
class ContractorResponseBase(BaseModel):
    proposed_price: Optional[int] = Field(None, ge=0)
    estimated_time: Optional[str] = Field(None, max_length=100)
    comment: Optional[str] = Field(None, max_length=1000)

class ContractorResponseCreate(ContractorResponseBase):
    pass

class ContractorResponseResponse(ContractorResponseBase):
    class Config:
        orm_mode = True
    
    id: int
    request_id: int
    contractor_id: int
    is_accepted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Связанные объекты
    contractor: Optional[ContractorProfileResponse] = None

# Сопоставление артикулов
class ArticleMappingBase(BaseModel):
    contractor_article: str = Field(..., min_length=1, max_length=200)
    contractor_description: str = Field(..., min_length=1, max_length=1000)
    agb_article: str = Field(..., min_length=1, max_length=200)
    agb_description: str = Field(..., min_length=1, max_length=1000)

class ArticleMappingCreate(ArticleMappingBase):
    confidence: Optional[float] = Field(0.0, ge=0.0, le=1.0)

class ArticleMappingResponse(ArticleMappingBase):
    class Config:
        orm_mode = True
    
    id: int
    confidence: float
    created_at: datetime
    updated_at: Optional[datetime] = None

# Заявки контрагентов
class ContractorRequestBase(BaseModel):
    request_number: str = Field(..., min_length=1, max_length=50)
    contractor_name: str = Field(..., min_length=1, max_length=200)
    request_date: datetime

class ContractorRequestCreate(ContractorRequestBase):
    pass

class ContractorRequestResponse(ContractorRequestBase):
    class Config:
        orm_mode = True
    
    id: int
    status: str
    total_items: int
    matched_items: int
    created_by: int
    processed_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    # Связанные объекты
    creator: Optional[UserResponse] = None
    processor: Optional[UserResponse] = None
    items: Optional[List['ContractorRequestItemResponse']] = None

# Позиции заявок контрагентов
class ContractorRequestItemBase(BaseModel):
    contractor_article: str = Field(..., min_length=1, max_length=200)
    contractor_description: str = Field(..., min_length=1, max_length=1000)

class ContractorRequestItemCreate(ContractorRequestItemBase):
    agb_article: Optional[str] = Field(None, max_length=200)
    agb_description: Optional[str] = Field(None, max_length=1000)
    confidence: Optional[float] = Field(0.0, ge=0.0, le=1.0)

class ContractorRequestItemResponse(ContractorRequestItemBase):
    class Config:
        orm_mode = True
    
    id: int
    request_id: int
    agb_article: Optional[str] = None
    agb_description: Optional[str] = None
    confidence: float
    created_at: datetime

# Аутентификация
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class EmailVerificationRequest(BaseModel):
    token: str

class EmailVerificationResponse(BaseModel):
    message: str
    verified: bool

# Новые схемы для системы безопасности
class SecurityVerificationBase(BaseModel):
    contractor_id: int
    verification_status: str = Field(..., description="pending, approved, rejected")
    verification_notes: Optional[str] = Field(None, max_length=2000)
    checked_by: Optional[int] = Field(None, description="ID сотрудника службы безопасности")
    checked_at: Optional[datetime] = None

class SecurityVerificationCreate(SecurityVerificationBase):
    pass

class SecurityVerificationResponse(SecurityVerificationBase):
    class Config:
        orm_mode = True
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Схемы для HR документов
class HRDocumentBase(BaseModel):
    contractor_id: int
    document_type: str = Field(..., description="Тип документа")
    document_status: str = Field("pending", description="Статус документа")
    generated_by: Optional[int] = Field(None, description="ID сотрудника HR")
    generated_at: Optional[datetime] = None
    document_path: Optional[str] = Field(None, description="Путь к файлу документа")

class HRDocumentCreate(HRDocumentBase):
    pass

class HRDocumentResponse(HRDocumentBase):
    class Config:
        orm_mode = True
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Схемы для откликов исполнителей
class ContractorResponseBase(BaseModel):
    request_id: int
    contractor_id: int
    response_text: str = Field(..., max_length=2000)
    proposed_price: Optional[int] = Field(None, ge=0)
    estimated_duration: Optional[str] = Field(None, max_length=100)
    availability_date: Optional[datetime] = None

class ContractorResponseCreate(ContractorResponseBase):
    pass

class ContractorResponseResponse(ContractorResponseBase):
    class Config:
        orm_mode = True
    
    id: int
    status: str = Field("pending", description="pending, accepted, rejected")
    created_at: datetime
    updated_at: Optional[datetime] = None

# Обновляем forward references
# Убираем model_rebuild() для Pydantic v1
# RepairRequestResponse.model_rebuild()
# ContractorResponseResponse.model_rebuild()
# ContractorRequestResponse.model_rebuild()
# ContractorRequestItemResponse.model_rebuild()
