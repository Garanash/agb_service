#!/usr/bin/env python3
"""
Скрипт для заполнения системы тестовыми данными
"""

import os
import sys
import random
from datetime import datetime, timedelta
from passlib.context import CryptContext
from faker import Faker

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, Base, engine
from models import (
    User, UserRole, CustomerProfile, ContractorProfile, 
    RepairRequest, RequestStatus,
    ContractorResponse, SecurityVerification, HRDocument
)

# Настройка Faker для русского языка
fake = Faker('ru_RU')
pwd_context = CryptContext(schemes=['sha256_crypt'], deprecated='auto')

def create_test_users():
    """Создание тестовых пользователей всех ролей"""
    db = SessionLocal()
    try:
        print("🔧 Создание тестовых пользователей...")
        
        # Создаем пользователей разных ролей
        users_data = [
            # Администраторы
            {
                'username': 'admin1',
                'email': 'admin1@agregator.com',
                'first_name': 'Александр',
                'last_name': 'Петров',
                'middle_name': 'Владимирович',
                'phone': '+7 (495) 123-45-67',
                'role': UserRole.ADMIN,
                'is_active': True,
                'email_verified': True
            },
            {
                'username': 'admin2',
                'email': 'admin2@agregator.com',
                'first_name': 'Елена',
                'last_name': 'Сидорова',
                'middle_name': 'Игоревна',
                'phone': '+7 (495) 234-56-78',
                'role': UserRole.ADMIN,
                'is_active': True,
                'email_verified': True
            },
            
            # Менеджеры
            {
                'username': 'manager1',
                'email': 'manager1@agregator.com',
                'first_name': 'Дмитрий',
                'last_name': 'Козлов',
                'middle_name': 'Александрович',
                'phone': '+7 (495) 345-67-89',
                'role': UserRole.MANAGER,
                'is_active': True,
                'email_verified': True
            },
            {
                'username': 'manager2',
                'email': 'manager2@agregator.com',
                'first_name': 'Ольга',
                'last_name': 'Морозова',
                'middle_name': 'Сергеевна',
                'phone': '+7 (495) 456-78-90',
                'role': UserRole.MANAGER,
                'is_active': True,
                'email_verified': True
            },
            
            # Заказчики
            {
                'username': 'customer1',
                'email': 'customer1@company.com',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'middle_name': 'Петрович',
                'phone': '+7 (495) 567-89-01',
                'role': UserRole.CUSTOMER,
                'is_active': True,
                'email_verified': True
            },
            {
                'username': 'customer2',
                'email': 'customer2@mining.com',
                'first_name': 'Мария',
                'last_name': 'Смирнова',
                'middle_name': 'Андреевна',
                'phone': '+7 (495) 678-90-12',
                'role': UserRole.CUSTOMER,
                'is_active': True,
                'email_verified': True
            },
            {
                'username': 'customer3',
                'email': 'customer3@oil.com',
                'first_name': 'Сергей',
                'last_name': 'Кузнецов',
                'middle_name': 'Николаевич',
                'phone': '+7 (495) 789-01-23',
                'role': UserRole.CUSTOMER,
                'is_active': True,
                'email_verified': True
            },
            
            # Исполнители
            {
                'username': 'contractor1',
                'email': 'contractor1@service.com',
                'first_name': 'Андрей',
                'last_name': 'Волков',
                'middle_name': 'Михайлович',
                'phone': '+7 (495) 890-12-34',
                'role': UserRole.CONTRACTOR,
                'is_active': True,
                'email_verified': True
            },
            {
                'username': 'contractor2',
                'email': 'contractor2@repair.com',
                'first_name': 'Николай',
                'last_name': 'Лебедев',
                'middle_name': 'Владимирович',
                'phone': '+7 (495) 901-23-45',
                'role': UserRole.CONTRACTOR,
                'is_active': True,
                'email_verified': True
            },
            {
                'username': 'contractor3',
                'email': 'contractor3@tech.com',
                'first_name': 'Владимир',
                'last_name': 'Соколов',
                'middle_name': 'Иванович',
                'phone': '+7 (495) 012-34-56',
                'role': UserRole.CONTRACTOR,
                'is_active': True,
                'email_verified': True
            },
            
            # Сервисные инженеры
            {
                'username': 'engineer1',
                'email': 'engineer1@service.com',
                'first_name': 'Алексей',
                'last_name': 'Попов',
                'middle_name': 'Сергеевич',
                'phone': '+7 (495) 123-45-78',
                'role': UserRole.SERVICE_ENGINEER,
                'is_active': True,
                'email_verified': True
            },
            {
                'username': 'engineer2',
                'email': 'engineer2@tech.com',
                'first_name': 'Екатерина',
                'last_name': 'Васильева',
                'middle_name': 'Александровна',
                'phone': '+7 (495) 234-56-89',
                'role': UserRole.SERVICE_ENGINEER,
                'is_active': True,
                'email_verified': True
            },
            
            # Служба безопасности
            {
                'username': 'security1',
                'email': 'security1@company.com',
                'first_name': 'Роман',
                'last_name': 'Семенов',
                'middle_name': 'Дмитриевич',
                'phone': '+7 (495) 345-67-90',
                'role': UserRole.SECURITY,
                'is_active': True,
                'email_verified': True
            },
            
            # HR
            {
                'username': 'hr1',
                'email': 'hr1@company.com',
                'first_name': 'Анна',
                'last_name': 'Новикова',
                'middle_name': 'Владимировна',
                'phone': '+7 (495) 456-78-01',
                'role': UserRole.HR,
                'is_active': True,
                'email_verified': True
            }
        ]
        
        created_users = []
        for user_data in users_data:
            # Проверяем, существует ли пользователь
            existing_user = db.query(User).filter(
                (User.username == user_data['username']) | 
                (User.email == user_data['email'])
            ).first()
            
            if existing_user:
                print(f"  ⚠️  Пользователь {user_data['username']} уже существует")
                created_users.append(existing_user)
                continue
            
            # Создаем пользователя
            hashed_password = pwd_context.hash('password123')
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                hashed_password=hashed_password,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                middle_name=user_data['middle_name'],
                phone=user_data['phone'],
                role=user_data['role'],
                is_active=user_data['is_active'],
                email_verified=user_data['email_verified'],
                is_password_changed=False
            )
            
            db.add(user)
            created_users.append(user)
            print(f"  ✅ Создан пользователь: {user_data['username']} ({user_data['role']})")
        
        db.commit()
        # Обновляем объекты пользователей для работы с новой сессией
        for user in created_users:
            db.refresh(user)
        print(f"🎉 Создано {len(created_users)} пользователей")
        return created_users
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка создания пользователей: {e}")
        return []
    finally:
        db.close()

def create_customer_profiles(users):
    """Создание профилей заказчиков"""
    db = SessionLocal()
    try:
        print("🏢 Создание профилей заказчиков...")
        
        customer_users = [u for u in users if u.role == UserRole.CUSTOMER]
        companies = [
            {
                'company_name': 'ООО "Алмазгеобур"',
                'region': 'Московская область',
                'inn_or_ogrn': '1234567890',
                'equipment_brands': ['Алмазгеобур', 'Эпирог', 'Катерпиллар'],
                'equipment_types': ['Буровые установки', 'Экскаваторы', 'Погрузчики'],
                'mining_operations': ['Геологоразведочные работы', 'Открытые горные работы'],
                'service_history': 'Более 10 лет работы в горнодобывающей отрасли'
            },
            {
                'company_name': 'АО "Сибирские рудники"',
                'region': 'Красноярский край',
                'inn_or_ogrn': '2345678901',
                'equipment_brands': ['Бортлангир', 'Компани', 'Либхерр'],
                'equipment_types': ['Самосвалы', 'Бульдозеры', 'Краны'],
                'mining_operations': ['Подземные горные работы', 'Обогащение полезных ископаемых'],
                'service_history': 'Специализация на добыче угля и железной руды'
            },
            {
                'company_name': 'ПАО "Уральские недра"',
                'region': 'Свердловская область',
                'inn_or_ogrn': '3456789012',
                'equipment_types': ['Компрессоры', 'Генераторы', 'Другое оборудование'],
                'mining_operations': ['Транспортировка', 'Складские операции'],
                'service_history': 'Работа с драгоценными металлами и камнями'
            }
        ]
        
        created_profiles = []
        for i, user in enumerate(customer_users):
            if i < len(companies):
                company_data = companies[i]
            else:
                company_data = {
                    'company_name': f'ООО "{fake.company()}"',
                    'region': fake.region(),
                    'inn_or_ogrn': fake.numerify('##########'),
                    'equipment_brands': random.sample(['Алмазгеобур', 'Эпирог', 'Катерпиллар', 'Компани'], 2),
                    'equipment_types': random.sample(['Буровые установки', 'Экскаваторы', 'Самосвалы'], 2),
                    'mining_operations': random.sample(['Геологоразведочные работы', 'Открытые горные работы'], 1),
                    'service_history': fake.text(max_nb_chars=200)
                }
            
            # Проверяем, существует ли профиль
            existing_profile = db.query(CustomerProfile).filter(
                CustomerProfile.user_id == user.id
            ).first()
            
            if existing_profile:
                print(f"  ⚠️  Профиль заказчика для {user.username} уже существует")
                created_profiles.append(existing_profile)
                continue
            
            profile = CustomerProfile(
                user_id=user.id,
                company_name=company_data['company_name'],
                contact_person=f"{user.first_name} {user.last_name}",
                phone=user.phone,
                email=user.email,
                address=f"{company_data['region']}, {fake.address()}",
                inn=company_data['inn_or_ogrn'][:10] if len(company_data['inn_or_ogrn']) >= 10 else company_data['inn_or_ogrn'],
                ogrn=company_data['inn_or_ogrn'],
                equipment_brands=company_data['equipment_brands'],
                equipment_types=company_data['equipment_types'],
                mining_operations=company_data['mining_operations'],
                service_history=company_data['service_history']
            )
            
            db.add(profile)
            created_profiles.append(profile)
            print(f"  ✅ Создан профиль заказчика: {company_data['company_name']}")
        
        db.commit()
        print(f"🎉 Создано {len(created_profiles)} профилей заказчиков")
        return created_profiles
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка создания профилей заказчиков: {e}")
        return []
    finally:
        db.close()

def create_contractor_profiles(users):
    """Создание профилей исполнителей"""
    db = SessionLocal()
    try:
        print("🔧 Создание профилей исполнителей...")
        
        contractor_users = [u for u in users if u.role == UserRole.CONTRACTOR]
        specializations_list = [
            'Электрика', 'Гидравлика', 'Ходовая часть', 'Двигатели',
            'Трансмиссия', 'Системы управления', 'Пневматика', 'Сварка',
            'Механика', 'Электроника'
        ]
        
        equipment_brands = [
            'Алмазгеобур', 'Эпирог', 'Бортлангир', 'Катерпиллар',
            'Компани', 'Либхерр', 'Вольво'
        ]
        
        certifications = [
            'Сертификат сварщика', 'Сертификат электрика', 'Сертификат гидравлика',
            'Сертификат по технике безопасности', 'Сертификат по работе с грузоподъемными механизмами'
        ]
        
        work_regions = [
            'Москва и область', 'Санкт-Петербург и область', 'Центральный федеральный округ',
            'Уральский федеральный округ', 'Сибирский федеральный округ'
        ]
        
        created_profiles = []
        for user in contractor_users:
            # Проверяем, существует ли профиль
            existing_profile = db.query(ContractorProfile).filter(
                ContractorProfile.user_id == user.id
            ).first()
            
            if existing_profile:
                print(f"  ⚠️  Профиль исполнителя для {user.username} уже существует")
                created_profiles.append(existing_profile)
                continue
            
            profile = ContractorProfile(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                patronymic=user.middle_name,
                phone=user.phone,
                email=user.email,
                specializations=random.sample(specializations_list, random.randint(2, 4)),
                equipment_brands_experience=random.sample(equipment_brands, random.randint(2, 4)),
                certifications=random.sample(certifications, random.randint(1, 3)),
                work_regions=random.sample(work_regions, random.randint(1, 3)),
                hourly_rate=random.randint(1500, 5000),
                telegram_username=f"@{user.username}",
                general_description=fake.text(max_nb_chars=500),
                professional_info=fake.text(max_nb_chars=300),
                education=fake.text(max_nb_chars=200),
                availability_status=random.choice(['available', 'busy', 'unavailable'])
            )
            
            db.add(profile)
            created_profiles.append(profile)
            print(f"  ✅ Создан профиль исполнителя: {user.first_name} {user.last_name}")
        
        db.commit()
        print(f"🎉 Создано {len(created_profiles)} профилей исполнителей")
        return created_profiles
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка создания профилей исполнителей: {e}")
        return []
    finally:
        db.close()

def create_repair_requests(users, customer_profiles):
    """Создание заявок на ремонт"""
    db = SessionLocal()
    try:
        print("📋 Создание заявок на ремонт...")
        
        managers = [u for u in users if u.role == UserRole.MANAGER]
        customers = [p for p in customer_profiles]
        
        if not managers or not customers:
            print("  ⚠️  Нет менеджеров или заказчиков для создания заявок")
            return []
        
        request_templates = [
            {
                'title': 'Ремонт буровой установки',
                'description': 'Требуется диагностика и ремонт гидравлической системы буровой установки. Обнаружена утечка масла и снижение давления.',
                'equipment_type': 'Буровые установки',
                'priority': 'high',
                'urgency': 'urgent'
            },
            {
                'title': 'Замена двигателя экскаватора',
                'description': 'Необходима замена двигателя Caterpillar 320D. Двигатель выработал ресурс, требуется полная замена с гарантией.',
                'equipment_type': 'Экскаваторы',
                'priority': 'medium',
                'urgency': 'normal'
            },
            {
                'title': 'Ремонт ходовой части самосвала',
                'description': 'Проблемы с ходовой частью самосвала Volvo. Требуется замена подшипников и ремонт тормозной системы.',
                'equipment_type': 'Самосвалы',
                'priority': 'high',
                'urgency': 'urgent'
            },
            {
                'title': 'Настройка системы управления',
                'description': 'Требуется настройка и калибровка системы управления погрузчиком. Проблемы с точностью позиционирования.',
                'equipment_type': 'Погрузчики',
                'priority': 'medium',
                'urgency': 'normal'
            },
            {
                'title': 'Ремонт компрессора',
                'description': 'Компрессор не развивает необходимое давление. Требуется диагностика и ремонт компрессорной станции.',
                'equipment_type': 'Компрессоры',
                'priority': 'low',
                'urgency': 'normal'
            },
            {
                'title': 'Замена гидроцилиндров',
                'description': 'Требуется замена гидроцилиндров подъема стрелы крана. Обнаружена течь в уплотнениях.',
                'equipment_type': 'Краны',
                'priority': 'medium',
                'urgency': 'urgent'
            }
        ]
        
        statuses = [
            RequestStatus.NEW,
            RequestStatus.MANAGER_REVIEW,
            RequestStatus.CLARIFICATION,
            RequestStatus.SENT_TO_CONTRACTORS,
            RequestStatus.CONTRACTOR_RESPONSES,
            RequestStatus.ASSIGNED,
            RequestStatus.IN_PROGRESS,
            RequestStatus.COMPLETED,
            RequestStatus.CANCELLED
        ]
        
        created_requests = []
        for i in range(20):  # Создаем 20 заявок
            template = random.choice(request_templates)
            customer = random.choice(customers)
            manager = random.choice(managers)
            status = random.choice(statuses)
            
            # Создаем дату в последние 30 дней
            created_date = fake.date_time_between(start_date='-30d', end_date='now')
            
            request = RepairRequest(
                customer_id=customer.id,
                manager_id=manager.id,
                title=template['title'],
                description=template['description'],
                equipment_type=template['equipment_type'],
                location=fake.city(),
                priority=template['priority'],
                urgency=template['urgency'],
                status=status,
                estimated_cost=random.randint(50000, 500000),
                created_at=created_date,
                updated_at=created_date
            )
            
            # Добавляем дополнительные поля в зависимости от статуса
            if status in [RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS, RequestStatus.COMPLETED]:
                contractors = [u for u in users if u.role == UserRole.CONTRACTOR]
                if contractors:
                    request.assigned_contractor_id = random.choice(contractors).id
                    request.assigned_at = created_date + timedelta(days=random.randint(1, 5))
            
            if status == RequestStatus.COMPLETED:
                request.completed_at = created_date + timedelta(days=random.randint(5, 15))
                request.final_cost = random.randint(40000, 600000)
            
            if status in [RequestStatus.CLARIFICATION, RequestStatus.MANAGER_REVIEW]:
                request.manager_comment = fake.text(max_nb_chars=200)
            
            db.add(request)
            created_requests.append(request)
            print(f"  ✅ Создана заявка: {template['title']} (статус: {status})")
        
        db.commit()
        print(f"🎉 Создано {len(created_requests)} заявок на ремонт")
        return created_requests
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка создания заявок: {e}")
        return []
    finally:
        db.close()

def create_contractor_responses(users, repair_requests):
    """Создание ответов исполнителей на заявки"""
    db = SessionLocal()
    try:
        print("💬 Создание ответов исполнителей...")
        
        contractor_profiles = db.query(ContractorProfile).all()
        
        if not contractor_profiles or not repair_requests:
            print("  ⚠️  Нет исполнителей или заявок для создания ответов")
            return []
        
        created_responses = []
        for request in repair_requests[:10]:  # Ответы на первые 10 заявок
            # Создаем 1-3 ответа на каждую заявку
            num_responses = random.randint(1, 3)
            responding_profiles = random.sample(contractor_profiles, min(num_responses, len(contractor_profiles)))
            
            for profile in responding_profiles:
                response = ContractorResponse(
                    request_id=request.id,
                    contractor_id=profile.id,
                    proposed_cost=random.randint(30000, 400000),
                    estimated_duration_days=random.randint(1, 30),
                    message=fake.text(max_nb_chars=300),
                    is_accepted=random.choice([True, False, None])  # True, False, или None (не рассмотрено)
                )
                
                db.add(response)
                created_responses.append(response)
                print(f"  ✅ Создан ответ от {profile.first_name} {profile.last_name} на заявку #{request.id}")
        
        db.commit()
        print(f"🎉 Создано {len(created_responses)} ответов исполнителей")
        return created_responses
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка создания ответов исполнителей: {e}")
        return []
    finally:
        db.close()

def create_security_verifications(users):
    """Создание записей верификации безопасности"""
    db = SessionLocal()
    try:
        print("🛡️ Создание записей верификации безопасности...")
        
        contractor_profiles = db.query(ContractorProfile).all()
        security_users = [u for u in users if u.role == UserRole.SECURITY]
        
        if not contractor_profiles or not security_users:
            print("  ⚠️  Нет исполнителей или службы безопасности для создания верификаций")
            return []
        
        verification_statuses = ['pending', 'approved', 'rejected', 'under_review']
        
        created_verifications = []
        for profile in contractor_profiles:
            status = random.choice(verification_statuses)
            security_user = random.choice(security_users)
            
            verification = SecurityVerification(
                contractor_id=profile.id,
                verification_status=status,
                verification_notes=fake.text(max_nb_chars=200),
                checked_by=security_user.id if status in ['approved', 'rejected'] else None,
                checked_at=fake.date_time_between(start_date='-30d', end_date='now') if status in ['approved', 'rejected'] else None
            )
            
            db.add(verification)
            created_verifications.append(verification)
            print(f"  ✅ Создана верификация для {profile.first_name} {profile.last_name} (статус: {status})")
        
        db.commit()
        print(f"🎉 Создано {len(created_verifications)} записей верификации")
        return created_verifications
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка создания верификаций: {e}")
        return []
    finally:
        db.close()

def create_hr_documents(users):
    """Создание HR документов"""
    db = SessionLocal()
    try:
        print("📄 Создание HR документов...")
        
        hr_users = [u for u in users if u.role == UserRole.HR]
        contractor_profiles = db.query(ContractorProfile).all()
        
        if not hr_users or not contractor_profiles:
            print("  ⚠️  Нет HR или исполнителей для создания документов")
            return []
        
        document_types = [
            'Трудовой договор',
            'Дополнительное соглашение',
            'Справка о доходах',
            'Справка о стаже',
            'Справка о квалификации',
            'Договор подряда',
            'Соглашение о неразглашении'
        ]
        
        created_documents = []
        for profile in contractor_profiles:
            num_docs = random.randint(1, 3)
            hr_user = random.choice(hr_users)
            
            for _ in range(num_docs):
                doc_type = random.choice(document_types)
                document = HRDocument(
                    contractor_id=profile.id,
                    document_type=doc_type,
                    document_path=f"/documents/{profile.id}/{doc_type.lower().replace(' ', '_')}.pdf",
                    document_status=random.choice(['draft', 'generated', 'sent', 'signed']),
                    generated_by=hr_user.id,
                    generated_at=fake.date_time_between(start_date='-30d', end_date='now')
                )
                
                db.add(document)
                created_documents.append(document)
                print(f"  ✅ Создан документ: {doc_type} для {profile.first_name} {profile.last_name}")
        
        db.commit()
        print(f"🎉 Создано {len(created_documents)} HR документов")
        return created_documents
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка создания HR документов: {e}")
        return []
    finally:
        db.close()

def main():
    """Основная функция для заполнения системы тестовыми данными"""
    print("🚀 Начинаем заполнение системы тестовыми данными...")
    print("=" * 60)
    
    # Создаем таблицы, если их нет
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы базы данных созданы/проверены")
    
    # Создаем пользователей
    users = create_test_users()
    if not users:
        print("❌ Не удалось создать пользователей. Завершение.")
        return
    
    # Создаем профили заказчиков
    customer_profiles = create_customer_profiles(users)
    
    # Создаем профили исполнителей
    contractor_profiles = create_contractor_profiles(users)
    
    # Создаем заявки на ремонт
    repair_requests = create_repair_requests(users, customer_profiles)
    
    # Создаем ответы исполнителей
    contractor_responses = create_contractor_responses(users, repair_requests)
    
    # Создаем верификации безопасности
    security_verifications = create_security_verifications(users)
    
    # Создаем HR документы
    hr_documents = create_hr_documents(users)
    
    print("=" * 60)
    print("🎉 ЗАПОЛНЕНИЕ СИСТЕМЫ ЗАВЕРШЕНО!")
    print(f"📊 Статистика:")
    print(f"  👥 Пользователей: {len(users)}")
    print(f"  🏢 Профилей заказчиков: {len(customer_profiles)}")
    print(f"  🔧 Профилей исполнителей: {len(contractor_profiles)}")
    print(f"  📋 Заявок на ремонт: {len(repair_requests)}")
    print(f"  💬 Ответов исполнителей: {len(contractor_responses)}")
    print(f"  🛡️ Верификаций безопасности: {len(security_verifications)}")
    print(f"  📄 HR документов: {len(hr_documents)}")
    print("=" * 60)
    print("🔑 Тестовые учетные данные:")
    print("  admin / admin123 - Администратор")
    print("  manager1 / password123 - Менеджер")
    print("  customer1 / password123 - Заказчик")
    print("  contractor1 / password123 - Исполнитель")
    print("  engineer1 / password123 - Сервисный инженер")
    print("  security1 / password123 - Служба безопасности")
    print("  hr1 / password123 - HR")
    print("=" * 60)

if __name__ == "__main__":
    main()
