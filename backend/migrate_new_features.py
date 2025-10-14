#!/usr/bin/env python3
"""
Миграция для добавления новых функций системы Алмазгеобур
- Новые роли пользователей (MANAGER, SECURITY, HR)
- Новые поля для профилей заказчиков и исполнителей
- Новые статусы заявок
- Новые таблицы для проверки безопасности и HR документов
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Ошибка: Переменная окружения DATABASE_URL не установлена.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_migration():
    print("🔄 Выполняем миграцию для новых функций системы Алмазгеобур...")
    db = SessionLocal()
    
    try:
        # 1. Обновляем статусы заявок
        print("Обновляем статусы заявок...")
        try:
            # Добавляем новые статусы
            db.execute(text("""
                ALTER TABLE repair_requests 
                DROP CONSTRAINT IF EXISTS repair_requests_status_check
            """))
            db.execute(text("""
                ALTER TABLE repair_requests 
                ADD CONSTRAINT repair_requests_status_check 
                CHECK (status IN ('new', 'manager_review', 'clarification', 'sent_to_contractors', 
                                'contractor_responses', 'assigned', 'in_progress', 'completed', 'cancelled'))
            """))
            db.commit()
            print("✅ Статусы заявок обновлены")
        except Exception as e:
            db.rollback()
            print(f"⚠️ Ошибка при обновлении статусов: {e}")

        # 2. Добавляем новые поля в customer_profiles
        print("Добавляем поля для горнодобывающей техники в профили заказчиков...")
        new_customer_fields = [
            "equipment_brands JSON",
            "equipment_types JSON", 
            "mining_operations JSON",
            "service_history TEXT"
        ]
        
        for field in new_customer_fields:
            field_name = field.split()[0]
            field_type = field.split()[1]
            try:
                db.execute(text(f"ALTER TABLE customer_profiles ADD COLUMN {field_name} {field_type}"))
                db.commit()
                print(f"✅ Поле {field_name} добавлено в customer_profiles")
            except ProgrammingError as e:
                db.rollback()
                if "already exists" in str(e):
                    print(f"Поле {field_name} уже существует в customer_profiles")
                else:
                    print(f"Ошибка при добавлении {field_name}: {e}")

        # 3. Добавляем новые поля в contractor_profiles
        print("Добавляем поля специализации в профили исполнителей...")
        new_contractor_fields = [
            "specializations JSON",
            "equipment_brands_experience JSON",
            "certifications JSON", 
            "work_regions JSON",
            "hourly_rate FLOAT",
            "availability_status VARCHAR(50) DEFAULT 'available'"
        ]
        
        for field in new_contractor_fields:
            field_name = field.split()[0]
            field_definition = field
            try:
                db.execute(text(f"ALTER TABLE contractor_profiles ADD COLUMN {field_definition}"))
                db.commit()
                print(f"✅ Поле {field_name} добавлено в contractor_profiles")
            except ProgrammingError as e:
                db.rollback()
                if "already exists" in str(e):
                    print(f"Поле {field_name} уже существует в contractor_profiles")
                else:
                    print(f"Ошибка при добавлении {field_name}: {e}")

        # 4. Добавляем новые поля в repair_requests
        print("Добавляем поля workflow в заявки...")
        new_request_fields = [
            "priority VARCHAR(50) DEFAULT 'normal'",
            "clarification_details TEXT",
            "scheduled_date TIMESTAMP",
            "manager_id INTEGER REFERENCES users(id)"
        ]
        
        for field in new_request_fields:
            field_name = field.split()[0]
            field_definition = field
            try:
                db.execute(text(f"ALTER TABLE repair_requests ADD COLUMN {field_definition}"))
                db.commit()
                print(f"✅ Поле {field_name} добавлено в repair_requests")
            except ProgrammingError as e:
                db.rollback()
                if "already exists" in str(e):
                    print(f"Поле {field_name} уже существует в repair_requests")
                else:
                    print(f"Ошибка при добавлении {field_name}: {e}")

        # 5. Создаем таблицу security_verifications
        print("Создаем таблицу проверки безопасности...")
        try:
            db.execute(text("""
                CREATE TABLE security_verifications (
                    id SERIAL PRIMARY KEY,
                    contractor_id INTEGER NOT NULL REFERENCES contractor_profiles(id),
                    verification_status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    verification_notes TEXT,
                    checked_by INTEGER REFERENCES users(id),
                    checked_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            db.commit()
            print("✅ Таблица security_verifications создана")
        except ProgrammingError as e:
            db.rollback()
            if "already exists" in str(e):
                print("Таблица security_verifications уже существует")
            else:
                print(f"Ошибка при создании security_verifications: {e}")

        # 6. Создаем таблицу hr_documents
        print("Создаем таблицу HR документов...")
        try:
            db.execute(text("""
                CREATE TABLE hr_documents (
                    id SERIAL PRIMARY KEY,
                    contractor_id INTEGER NOT NULL REFERENCES contractor_profiles(id),
                    document_type VARCHAR(200) NOT NULL,
                    document_status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    generated_by INTEGER REFERENCES users(id),
                    generated_at TIMESTAMP WITH TIME ZONE,
                    document_path VARCHAR(500),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            db.commit()
            print("✅ Таблица hr_documents создана")
        except ProgrammingError as e:
            db.rollback()
            if "already exists" in str(e):
                print("Таблица hr_documents уже существует")
            else:
                print(f"Ошибка при создании hr_documents: {e}")

        # 7. Создаем индексы для производительности
        print("Создаем индексы...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_security_verifications_contractor_id ON security_verifications(contractor_id)",
            "CREATE INDEX IF NOT EXISTS idx_security_verifications_status ON security_verifications(verification_status)",
            "CREATE INDEX IF NOT EXISTS idx_hr_documents_contractor_id ON hr_documents(contractor_id)",
            "CREATE INDEX IF NOT EXISTS idx_hr_documents_status ON hr_documents(document_status)",
            "CREATE INDEX IF NOT EXISTS idx_repair_requests_manager_id ON repair_requests(manager_id)",
            "CREATE INDEX IF NOT EXISTS idx_repair_requests_status ON repair_requests(status)"
        ]
        
        for index_sql in indexes:
            try:
                db.execute(text(index_sql))
                db.commit()
                print(f"✅ Индекс создан: {index_sql.split()[-1]}")
            except Exception as e:
                db.rollback()
                print(f"⚠️ Ошибка создания индекса: {e}")

        print("🎉 Миграция завершена успешно!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Критическая ошибка миграции: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
