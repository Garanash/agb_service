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
            # Сначала удаляем отклики на все заявки пользователя, потом сами заявки
            
            # Получаем ID заявок, где пользователь является заказчиком или назначенным исполнителем
            requests_result = db.execute(text("SELECT id FROM repair_requests WHERE customer_id = :user_id OR assigned_contractor_id = :user_id"), {"user_id": user.id})
            request_ids = [row[0] for row in requests_result.fetchall()]
            
            # Удаляем отклики на эти заявки
            if request_ids:
                for req_id in request_ids:
                    db.execute(text("DELETE FROM contractor_responses WHERE request_id = :request_id"), {"request_id": req_id})
                print(f"  ✓ Удалены отклики на заявки: {len(request_ids)}")
                db.flush()
            
            # Удаляем заявки
            if request_ids:
                for req_id in request_ids:
                    db.execute(text("DELETE FROM repair_requests WHERE id = :request_id"), {"request_id": req_id})
                print(f"  ✓ Удалено заявок: {len(request_ids)}")
                db.flush()
            
            if user.role == "contractor":
                # Получаем contractor_profile_id для удаления связанных данных
                profile_result = db.execute(text("SELECT id FROM contractor_profiles WHERE user_id = :user_id"), {"user_id": user.id})
                profile_row = profile_result.fetchone()
                if profile_row:
                    contractor_profile_id = profile_row[0]
                    # Удаляем отклики исполнителя (ссылаются на contractor_profiles.id)
                    result = db.execute(text("DELETE FROM contractor_responses WHERE contractor_id = :contractor_id"), {"contractor_id": contractor_profile_id})
                    if result.rowcount > 0:
                        print(f"  ✓ Удалено откликов: {result.rowcount}")
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
                # Сначала удаляем заявки заказчика (если они еще есть)
                customer_requests = db.execute(text("SELECT id FROM repair_requests WHERE customer_id = :user_id"), {"user_id": user.id})
                customer_req_ids = [row[0] for row in customer_requests.fetchall()]
                if customer_req_ids:
                    for req_id in customer_req_ids:
                        db.execute(text("DELETE FROM contractor_responses WHERE request_id = :request_id"), {"request_id": req_id})
                        db.execute(text("DELETE FROM repair_requests WHERE id = :request_id"), {"request_id": req_id})
                    print(f"  ✓ Удалено заявок заказчика: {len(customer_req_ids)}")
                
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

