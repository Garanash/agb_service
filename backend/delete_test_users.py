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
        
        from sqlalchemy import text
        
        for user in test_users:
            print(f"🗑️ Удаление пользователя: {user.username} (email: {user.email}, роль: {user.role})")
            
            # Удаляем все связанные данные через SQL
            if user.role == "customer":
                # Удаляем заявки заказчика
                result = db.execute(text("DELETE FROM repair_requests WHERE customer_id = :user_id"), {"user_id": user.id})
                if result.rowcount > 0:
                    print(f"  ✓ Удалено заявок: {result.rowcount}")
            
            if user.role == "contractor":
                # Удаляем отклики исполнителя
                result = db.execute(text("DELETE FROM contractor_responses WHERE contractor_id = :user_id"), {"user_id": user.id})
                if result.rowcount > 0:
                    print(f"  ✓ Удалено откликов: {result.rowcount}")
                
                # Получаем contractor_id для удаления связанных данных
                profile_result = db.execute(text("SELECT id FROM contractor_profiles WHERE user_id = :user_id"), {"user_id": user.id})
                profile_row = profile_result.fetchone()
                if profile_row:
                    contractor_profile_id = profile_row[0]
                    # Удаляем связанные данные профиля
                    db.execute(text("DELETE FROM contractor_documents WHERE contractor_id = :contractor_id"), {"contractor_id": contractor_profile_id})
                    db.execute(text("DELETE FROM contractor_education WHERE contractor_id = :contractor_id"), {"contractor_id": contractor_profile_id})
                    db.execute(text("DELETE FROM contractor_verifications WHERE contractor_id = :contractor_id"), {"contractor_id": contractor_profile_id})
                    print(f"  ✓ Удалены связанные данные профиля")
            
            # Удаляем профили
            if user.role == "contractor":
                result = db.execute(text("DELETE FROM contractor_profiles WHERE user_id = :user_id"), {"user_id": user.id})
                if result.rowcount > 0:
                    print(f"  ✓ Удален профиль исполнителя")
            
            if user.role == "customer":
                result = db.execute(text("DELETE FROM customer_profiles WHERE user_id = :user_id"), {"user_id": user.id})
                if result.rowcount > 0:
                    print(f"  ✓ Удален профиль заказчика")
            
            # Удаляем пользователя
            result = db.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user.id})
            if result.rowcount > 0:
                deleted_count += 1
                print(f"  ✓ Пользователь удален")
        
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

