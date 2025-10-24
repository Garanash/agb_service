#!/usr/bin/env python3
"""
Миграция для добавления системы верификации исполнителей
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Выполняет миграцию базы данных"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Начинаем транзакцию
            trans = conn.begin()
            
            logger.info("🔄 Начинаем миграцию системы верификации исполнителей...")
            
            # 1. Добавляем новые поля в contractor_profiles
            logger.info("📝 Добавляем поля паспортных данных в contractor_profiles...")
            conn.execute(text("""
                ALTER TABLE contractor_profiles 
                ADD COLUMN IF NOT EXISTS passport_series VARCHAR,
                ADD COLUMN IF NOT EXISTS passport_number VARCHAR,
                ADD COLUMN IF NOT EXISTS passport_issued_by VARCHAR,
                ADD COLUMN IF NOT EXISTS passport_issued_date VARCHAR,
                ADD COLUMN IF NOT EXISTS passport_issued_code VARCHAR,
                ADD COLUMN IF NOT EXISTS birth_date VARCHAR,
                ADD COLUMN IF NOT EXISTS birth_place VARCHAR,
                ADD COLUMN IF NOT EXISTS inn VARCHAR
            """))
            
            # 2. Добавляем поля верификации в contractor_profiles
            logger.info("📝 Добавляем поля верификации в contractor_profiles...")
            conn.execute(text("""
                ALTER TABLE contractor_profiles 
                ADD COLUMN IF NOT EXISTS profile_completion_status VARCHAR DEFAULT 'incomplete',
                ADD COLUMN IF NOT EXISTS security_verified BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS manager_verified BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS security_verified_at TIMESTAMP WITH TIME ZONE,
                ADD COLUMN IF NOT EXISTS manager_verified_at TIMESTAMP WITH TIME ZONE,
                ADD COLUMN IF NOT EXISTS security_verified_by INTEGER REFERENCES users(id),
                ADD COLUMN IF NOT EXISTS manager_verified_by INTEGER REFERENCES users(id)
            """))
            
            # 3. Создаем таблицу contractor_education
            logger.info("📝 Создаем таблицу contractor_education...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS contractor_education (
                    id SERIAL PRIMARY KEY,
                    contractor_id INTEGER NOT NULL REFERENCES contractor_profiles(id) ON DELETE CASCADE,
                    institution_name VARCHAR NOT NULL,
                    degree VARCHAR NOT NULL,
                    specialization VARCHAR NOT NULL,
                    graduation_year INTEGER,
                    diploma_number VARCHAR,
                    document_path VARCHAR,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            
            # 4. Создаем таблицу contractor_documents
            logger.info("📝 Создаем таблицу contractor_documents...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS contractor_documents (
                    id SERIAL PRIMARY KEY,
                    contractor_id INTEGER NOT NULL REFERENCES contractor_profiles(id) ON DELETE CASCADE,
                    document_type VARCHAR NOT NULL,
                    document_name VARCHAR NOT NULL,
                    document_path VARCHAR NOT NULL,
                    file_size INTEGER,
                    mime_type VARCHAR,
                    verification_status VARCHAR NOT NULL DEFAULT 'pending',
                    verification_notes TEXT,
                    verified_by INTEGER REFERENCES users(id),
                    verified_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            
            # 5. Создаем таблицу contractor_verifications
            logger.info("📝 Создаем таблицу contractor_verifications...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS contractor_verifications (
                    id SERIAL PRIMARY KEY,
                    contractor_id INTEGER NOT NULL UNIQUE REFERENCES contractor_profiles(id) ON DELETE CASCADE,
                    profile_completed BOOLEAN DEFAULT FALSE,
                    documents_uploaded BOOLEAN DEFAULT FALSE,
                    security_check_passed BOOLEAN DEFAULT FALSE,
                    manager_approval BOOLEAN DEFAULT FALSE,
                    overall_status VARCHAR NOT NULL DEFAULT 'incomplete',
                    security_notes TEXT,
                    manager_notes TEXT,
                    security_checked_by INTEGER REFERENCES users(id),
                    manager_checked_by INTEGER REFERENCES users(id),
                    security_checked_at TIMESTAMP WITH TIME ZONE,
                    manager_checked_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            
            # 6. Создаем индексы для производительности
            logger.info("📝 Создаем индексы...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_contractor_education_contractor_id 
                ON contractor_education(contractor_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_contractor_documents_contractor_id 
                ON contractor_documents(contractor_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_contractor_documents_type 
                ON contractor_documents(document_type)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_contractor_verifications_status 
                ON contractor_verifications(overall_status)
            """))
            
            # 7. Создаем записи верификации для существующих исполнителей
            logger.info("📝 Создаем записи верификации для существующих исполнителей...")
            conn.execute(text("""
                INSERT INTO contractor_verifications (contractor_id, overall_status)
                SELECT id, 'incomplete'
                FROM contractor_profiles
                WHERE id NOT IN (SELECT contractor_id FROM contractor_verifications)
            """))
            
            # Подтверждаем транзакцию
            trans.commit()
            logger.info("✅ Миграция успешно завершена!")
            
        except Exception as e:
            # Откатываем транзакцию в случае ошибки
            trans.rollback()
            logger.error(f"❌ Ошибка миграции: {e}")
            raise

if __name__ == "__main__":
    run_migration()
