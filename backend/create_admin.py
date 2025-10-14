"""
Agregator Service - Создание администратора
"""

import sys
from pathlib import Path
from datetime import datetime

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import SessionLocal
from models import User, UserRole
from sqlalchemy import text
from api.v1.dependencies import get_password_hash

def create_admin():
    """Создание администратора"""
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже администратор
        existing_admin = db.execute(text("SELECT id FROM users WHERE username = 'admin'")).fetchone()
        
        if existing_admin:
            print("✅ Администратор уже существует")
            # Обновляем пароль
            hashed_password = get_password_hash("admin123")
            db.execute(text("UPDATE users SET hashed_password = :password WHERE username = 'admin'"), {"password": hashed_password})
            db.commit()
            print("✅ Пароль администратора обновлен")
        else:
            # Создаем нового администратора
            hashed_password = get_password_hash("admin123")
            db.execute(text("""
                INSERT INTO users (username, email, hashed_password, first_name, last_name, middle_name, role, is_active, created_at)
                VALUES ('admin', 'admin@agregator.com', :password, 'Администратор', 'Система', 'admin', 'admin', true, NOW())
            """), {"password": hashed_password})
            db.commit()
            print("✅ Администратор создан")
        
        print("👤 Логин: admin")
        print("🔑 Пароль: admin123")
        print("🌐 URL: http://localhost:8001")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()