"""
Миграция: сделать поле degree в contractor_education необязательным
"""
import sys
import os

# Добавляем путь к корню проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import SessionLocal

def migrate():
    """Выполняет миграцию базы данных"""
    db = SessionLocal()
    try:
        # Изменяем поле degree на nullable
        db.execute(text("""
            ALTER TABLE contractor_education 
            ALTER COLUMN degree DROP NOT NULL;
        """))
        db.commit()
        print("✅ Миграция выполнена успешно: поле degree теперь необязательное")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при выполнении миграции: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
