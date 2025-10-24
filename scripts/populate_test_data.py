#!/usr/bin/env python3
"""
Скрипт для добавления тестовых пользователей и заявок
"""
import requests
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/v1"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Списки для генерации данных
FIRST_NAMES = ["Александр", "Дмитрий", "Сергей", "Андрей", "Михаил", "Иван", "Алексей", "Павел", "Владимир", "Николай",
               "Мария", "Елена", "Ольга", "Анна", "Татьяна", "Наталья", "Ирина", "Екатерина", "Светлана", "Людмила"]
LAST_NAMES = ["Иванов", "Петров", "Сидоров", "Смирнов", "Козлов", "Новиков", "Морозов", "Волков", "Соколов", "Лебедев",
              "Иванова", "Петрова", "Сидорова", "Смирнова", "Козлова", "Новикова", "Морозова", "Волкова", "Соколова", "Лебедева"]
COMPANIES = ["ООО \"Горнодобывающая компания\"", "ЗАО \"Металлургический комплекс\"", "АО \"Технологии добычи\"", 
             "ИП Петров А.С.", "ООО \"Строительные технологии\"", "ЗАО \"Промышленные решения\""]
CITIES = ["Москва", "Санкт-Петербург", "Екатеринбург", "Новосибирск", "Челябинск", "Казань"]

def get_admin_token():
    """Получить токен администратора"""
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Ошибка авторизации: {response.status_code}, {response.text}")
        return None

def create_users(token, count=20):
    """Создать пользователей"""
    headers = {"Authorization": f"Bearer {token}"}
    created_users = {"customers": [], "contractors": []}
    
    for i in range(count):
        role = "customer" if i % 2 == 0 else "contractor"
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = f"test_{role}_{i+50}"
        email = f"{username}@test.com"
        
        user_data = {
            "username": username,
            "email": email,
            "password": "password123",
            "first_name": first_name,
            "last_name": last_name,
            "phone": f"+7-900-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "role": role
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=user_data)
        if response.status_code == 201 or response.status_code == 200:
            user = response.json()
            created_users[f"{role}s"].append(user)
            print(f"✓ Создан {role}: {username}")
        else:
            print(f"✗ Ошибка создания {username}: {response.status_code}")
    
    return created_users

def create_requests(customer_users, count=50):
    """Создать заявки от имени заказчиков"""
    equipment_types = ["Экскаватор", "Бульдозер", "Грузовик", "Кран", "Погрузчик"]
    request_types = ["Ремонт гидравлики", "Замена двигателя", "Техническое обслуживание", 
                     "Ремонт электрики", "Замена деталей"]
    
    # Используем существующих заказчиков
    customer_credentials = [
        {"username": "customer1", "password": "password123"},
        {"username": "customer2", "password": "password123"},
        {"username": "customer3", "password": "password123"},
    ]
    
    created_count = 0
    for i in range(count):
        # Выбираем случайного заказчика
        cred = random.choice(customer_credentials)
        
        # Получаем токен заказчика
        login_response = requests.post(
            f"{API_URL}/auth/login",
            json=cred
        )
        
        if login_response.status_code != 200:
            print(f"✗ Ошибка авторизации заказчика {cred['username']}")
            continue
        
        customer_token = login_response.json()["access_token"]
        
        equipment = random.choice(equipment_types)
        request_type = random.choice(request_types)
        
        request_data = {
            "title": f"{request_type} {equipment}",
            "description": f"Требуется {request_type.lower()} для {equipment.lower()}. Срочная заявка.",
            "equipment_type": equipment,
            "location_address": f"г. {random.choice(CITIES)}, ул. Промышленная, д. {random.randint(1, 100)}"
        }
        
        response = requests.post(
            f"{API_URL}/customer/requests",
            json=request_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        if response.status_code in [200, 201]:
            created_count += 1
            print(f"✓ Создана заявка {i+1}/{count}")
        else:
            print(f"✗ Ошибка создания заявки {i+1}: {response.status_code}")
    
    return created_count

def main():
    print("🚀 Начало создания тестовых данных...")
    
    # Получаем токен администратора
    token = get_admin_token()
    if not token:
        print("❌ Не удалось получить токен администратора")
        return
    
    print(f"✓ Токен администратора получен")
    
    # Создаем пользователей
    print("\n📝 Создание пользователей...")
    users = create_users(token, count=30)
    print(f"✓ Создано заказчиков: {len(users['customers'])}")
    print(f"✓ Создано исполнителей: {len(users['contractors'])}")
    
    # Создаем заявки
    print("\n📋 Создание заявок...")
    requests_count = create_requests(users['customers'], count=50)
    print(f"✓ Создано заявок: {requests_count}")
    
    print("\n✅ Завершено! Тестовые данные добавлены.")

if __name__ == "__main__":
    main()

