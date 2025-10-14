from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    CONTRACTOR = "contractor"
    SERVICE_ENGINEER = "service_engineer"

class RequestStatus(str, Enum):
    NEW = "new"
    PROCESSING = "processing"
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
    estimated_cost: Optional[int] = Field(None, ge=0)
    manager_comment: Optional[str] = Field(None, max_length=2000)
    final_price: Optional[int] = Field(None, ge=0)
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

# Обновляем forward references
# Убираем model_rebuild() для Pydantic v1
# RepairRequestResponse.model_rebuild()
# ContractorResponseResponse.model_rebuild()
# ContractorRequestResponse.model_rebuild()
# ContractorRequestItemResponse.model_rebuild()
