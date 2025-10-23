"""
Миграция для добавления полей координат в таблицу repair_requests
"""

from sqlalchemy import text
from database import engine
import logging

logger = logging.getLogger(__name__)

def add_coordinates_to_repair_requests():
    """Добавляет поля latitude и longitude в таблицу repair_requests"""
    try:
        with engine.connect() as conn:
            # Добавляем поля координат
            conn.execute(text("""
                ALTER TABLE repair_requests 
                ADD COLUMN IF NOT EXISTS latitude FLOAT,
                ADD COLUMN IF NOT EXISTS longitude FLOAT
            """))
            
            conn.commit()
            logger.info("✅ Поля координат успешно добавлены в таблицу repair_requests")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при добавлении полей координат: {e}")
        raise

if __name__ == "__main__":
    add_coordinates_to_repair_requests()
