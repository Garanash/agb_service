"""
Фабрики для создания тестовых данных
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from datetime import datetime, timezone, timedelta
from typing import List

from models import User, CustomerProfile, ContractorProfile, RepairRequest, SecurityVerification, HRDocument
from api.v1.dependencies import get_password_hash

fake = Faker('ru_RU')

class UserFactory(SQLAlchemyModelFactory):
    """Фабрика для создания пользователей"""
    
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    hashed_password = factory.LazyFunction(lambda: get_password_hash("testpassword"))
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    middle_name = factory.Faker('middle_name')
    phone = factory.Faker('phone_number')
    position = factory.Faker('job')
    role = factory.Iterator(['customer', 'contractor', 'manager', 'admin', 'security', 'hr'])
    is_active = True
    is_password_changed = False
    email_verified = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

class CustomerProfileFactory(SQLAlchemyModelFactory):
    """Фабрика для создания профилей заказчиков"""
    
    class Meta:
        model = CustomerProfile
        sqlalchemy_session_persistence = "commit"
    
    user_id = factory.SubFactory(UserFactory)
    company_name = factory.Faker('company')
    contact_person = factory.Faker('name')
    phone = factory.Faker('phone_number')
    email = factory.LazyAttribute(lambda obj: f"{obj.user_id.username}@example.com")
    address = factory.Faker('address')
    inn = factory.Faker('numerify', text='##########')
    ogrn = factory.Faker('numerify', text='#############')
    equipment_brands = factory.LazyFunction(lambda: fake.random_elements(
        elements=['Caterpillar', 'Komatsu', 'Hitachi', 'Volvo', 'Liebherr'],
        length=fake.random_int(min=1, max=3),
        unique=True
    ))
    equipment_types = factory.LazyFunction(lambda: fake.random_elements(
        elements=['Excavator', 'Bulldozer', 'Loader', 'Dump Truck', 'Crane'],
        length=fake.random_int(min=1, max=3),
        unique=True
    ))
    mining_operations = factory.LazyFunction(lambda: fake.random_elements(
        elements=['Open pit mining', 'Underground mining', 'Quarrying', 'Drilling', 'Blasting'],
        length=fake.random_int(min=1, max=3),
        unique=True
    ))
    service_history = factory.Faker('text', max_nb_chars=500)

class ContractorProfileFactory(SQLAlchemyModelFactory):
    """Фабрика для создания профилей исполнителей"""
    
    class Meta:
        model = ContractorProfile
        sqlalchemy_session_persistence = "commit"
    
    user_id = factory.SubFactory(UserFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    patronymic = factory.Faker('middle_name')
    phone = factory.Faker('phone_number')
    email = factory.LazyAttribute(lambda obj: f"{obj.user_id.username}@example.com")
    telegram_username = factory.LazyAttribute(lambda obj: f"{obj.user_id.username}_tg")
    specializations = factory.LazyFunction(lambda: fake.random_elements(
        elements=['Hydraulic repair', 'Engine maintenance', 'Electrical systems', 'Transmission repair', 'Diagnostics'],
        length=fake.random_int(min=1, max=4),
        unique=True
    ))
    equipment_brands_experience = factory.LazyFunction(lambda: fake.random_elements(
        elements=['Caterpillar', 'Komatsu', 'Hitachi', 'Volvo', 'Liebherr'],
        length=fake.random_int(min=1, max=3),
        unique=True
    ))
    certifications = factory.LazyFunction(lambda: fake.random_elements(
        elements=['Certified technician', 'Hydraulic specialist', 'Engine expert', 'Safety certified'],
        length=fake.random_int(min=1, max=3),
        unique=True
    ))
    work_regions = factory.LazyFunction(lambda: fake.random_elements(
        elements=['Moscow', 'St. Petersburg', 'Novosibirsk', 'Yekaterinburg', 'Krasnoyarsk'],
        length=fake.random_int(min=1, max=3),
        unique=True
    ))
    hourly_rate = factory.Faker('pyfloat', left_digits=4, right_digits=0, positive=True, min_value=500, max_value=3000)
    availability_status = factory.Iterator(['available', 'busy', 'blocked'])

class RepairRequestFactory(SQLAlchemyModelFactory):
    """Фабрика для создания заявок на ремонт"""
    
    class Meta:
        model = RepairRequest
        sqlalchemy_session_persistence = "commit"
    
    customer_id = factory.SubFactory(CustomerProfileFactory)
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=200)
    urgency = factory.Iterator(['low', 'medium', 'high', 'critical'])
    preferred_date = factory.LazyFunction(lambda: fake.date_time_between(start_date='+1d', end_date='+30d'))
    address = factory.Faker('address')
    city = factory.Faker('city')
    region = factory.Faker('state')
    equipment_type = factory.Iterator(['Excavator', 'Bulldozer', 'Loader', 'Dump Truck', 'Crane'])
    equipment_brand = factory.Iterator(['Caterpillar', 'Komatsu', 'Hitachi', 'Volvo', 'Liebherr'])
    equipment_model = factory.LazyFunction(lambda: f"{fake.random_element(elements=['CAT', 'PC', 'EX', 'A', 'L'])} {fake.random_int(min=200, max=500)}")
    problem_description = factory.Faker('text', max_nb_chars=300)
    priority = factory.Iterator(['low', 'normal', 'high', 'urgent'])
    status = factory.Iterator(['new', 'manager_review', 'clarification', 'sent_to_contractors', 'assigned', 'in_progress', 'completed'])
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

class SecurityVerificationFactory(SQLAlchemyModelFactory):
    """Фабрика для создания проверок безопасности"""
    
    class Meta:
        model = SecurityVerification
        sqlalchemy_session_persistence = "commit"
    
    contractor_id = factory.SubFactory(ContractorProfileFactory)
    verification_status = factory.Iterator(['pending', 'approved', 'rejected'])
    verification_notes = factory.Faker('text', max_nb_chars=200)
    checked_by = factory.SubFactory(UserFactory)
    checked_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

class HRDocumentFactory(SQLAlchemyModelFactory):
    """Фабрика для создания HR документов"""
    
    class Meta:
        model = HRDocument
        sqlalchemy_session_persistence = "commit"
    
    contractor_id = factory.SubFactory(ContractorProfileFactory)
    document_type = factory.Iterator(['employment_contract', 'service_agreement', 'nda_agreement', 'safety_instruction', 'equipment_certificate'])
    document_status = factory.Iterator(['pending', 'generated', 'completed'])
    generated_by = factory.SubFactory(UserFactory)
    generated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    document_path = factory.Faker('file_path')
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
