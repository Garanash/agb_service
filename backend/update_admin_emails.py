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
        
        # Обновляем через SQL для обхода уникальности email
        from sqlalchemy import text
        
        for user in users:
            old_email = user.email
            
            # Проверяем, используется ли уже этот email другим пользователем
            existing = db.execute(text("SELECT id FROM users WHERE email = :email AND id != :user_id"), 
                                 {"email": new_email, "user_id": user.id}).first()
            if existing:
                # Если email уже занят другим пользователем, пропускаем
                print(f"⚠ Пропущен {user.username} (роль: {user.role}): email уже используется другим пользователем")
            else:
                db.execute(text("UPDATE users SET email = :new_email WHERE id = :user_id"), 
                          {"new_email": new_email, "user_id": user.id})
                updated_count += 1
                print(f"✓ Обновлен {user.username} (роль: {user.role}, старый email: {old_email})")
            db.flush()
        
        db.commit()
        print(f"\n✅ Успешно обновлено email для {updated_count} из {len(users)} пользователей на {new_email}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при обновлении email: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_emails()

