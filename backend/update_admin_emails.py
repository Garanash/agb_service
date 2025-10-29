#!/usr/bin/env python3
"""
Скрипт для изменения email всех админов, безопасников и менеджеров
на dolgov_am@mail.ru для тестирования отправки email
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from models import User
from sqlalchemy import or_

def update_admin_emails():
    """Обновляет email всех админов, безопасников и менеджеров"""
    db = SessionLocal()
    
    try:
        # Получаем всех пользователей с ролями admin, security, manager
        users = db.query(User).filter(
            or_(
                User.role == "admin",
                User.role == "security",
                User.role == "manager"
            )
        ).all()
        
        if not users:
            print("⚠️ Не найдено пользователей с ролями admin, security или manager")
            return
        
        new_email = "dolgov_am@mail.ru"
        updated_count = 0
        
        for user in users:
            old_email = user.email
            user.email = new_email
            updated_count += 1
            print(f"✓ Обновлен {user.username} (роль: {user.role}, старый email: {old_email})")
        
        db.commit()
        print(f"\n✅ Успешно обновлено email для {updated_count} пользователей на {new_email}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при обновлении email: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_emails()

