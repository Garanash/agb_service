"""
Миграция для добавления таблицы telegram_messages
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from database import Base, engine

def create_telegram_messages_table():
    """Создание таблицы telegram_messages"""
    
    try:
        # Создаем таблицу telegram_messages
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS telegram_messages (
            id SERIAL PRIMARY KEY,
            telegram_user_id INTEGER NOT NULL REFERENCES telegram_users(id),
            message_text TEXT NOT NULL,
            message_type VARCHAR(50) DEFAULT 'text',
            is_from_bot BOOLEAN DEFAULT FALSE,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_telegram_messages_telegram_user_id ON telegram_messages(telegram_user_id);
        CREATE INDEX IF NOT EXISTS idx_telegram_messages_created_at ON telegram_messages(created_at);
        CREATE INDEX IF NOT EXISTS idx_telegram_messages_is_read ON telegram_messages(is_read);
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
        
        print("✅ Таблица telegram_messages создана успешно")
        
    except Exception as e:
        print(f"❌ Ошибка создания таблицы telegram_messages: {e}")
        raise

if __name__ == "__main__":
    create_telegram_messages_table()
