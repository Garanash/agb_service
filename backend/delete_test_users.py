#!/usr/bin/env python3
"""
Скрипт для удаления моковых/тестовых пользователей
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from models import User, ContractorProfile, CustomerProfile, RepairRequest
from sqlalchemy import or_

def delete_test_users():
    """Удаляет тестовых пользователей"""
    db = SessionLocal()
    
    try:
        # Находим тестовых пользователей по email или username
        test_patterns = [
            "%test.com%",
            "%@test",
            "contractor%d",
            "customer%d",
            "test_%",
        ]
        
        # Строим условие для поиска
        conditions = []
        for pattern in test_patterns:
            conditions.append(User.email.like(pattern))
            conditions.append(User.username.like(pattern))
        
        test_users = db.query(User).filter(or_(*conditions)).all()
        
        if not test_users:
            print("⚠️ Не найдено тестовых пользователей для удаления")
            return
        
        deleted_count = 0
        
        for user in test_users:
            print(f"🗑️ Удаление пользователя: {user.username} (email: {user.email}, роль: {user.role})")
            
            # Удаляем связанные заявки для заказчиков
            if user.role == "customer":
                requests = db.query(RepairRequest).filter(RepairRequest.customer_id == user.id).all()
                for req in requests:
                    db.delete(req)
                    print(f"  ✓ Удалена заявка {req.id}")
            
            # Удаляем связанные профили
            if user.role == "contractor":
                profile = db.query(ContractorProfile).filter(ContractorProfile.user_id == user.id).first()
                if profile:
                    db.delete(profile)
                    print(f"  ✓ Удален профиль исполнителя {profile.id}")
            
            if user.role == "customer":
                profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == user.id).first()
                if profile:
                    db.delete(profile)
                    print(f"  ✓ Удален профиль заказчика {profile.id}")
            
            # Удаляем пользователя
            db.delete(user)
            deleted_count += 1
        
        db.commit()
        print(f"\n✅ Успешно удалено {deleted_count} тестовых пользователей")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при удалении тестовых пользователей: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    delete_test_users()

