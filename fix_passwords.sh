#!/bin/bash

# Скрипт для исправления паролей на сервере

echo "🔧 Исправляем хеши паролей в базе данных..."

# Копируем скрипт исправления в контейнер
docker cp fix_passwords.py agregator-backend:/app/fix_passwords.py

# Запускаем исправление
echo "🚀 Запускаем исправление паролей..."
docker-compose exec agregator-backend python /app/fix_passwords.py

echo "✅ Исправление завершено!"
echo "🔑 Теперь можно войти с данными:"
echo "   Админ: admin / admin123"
echo "   Остальные пользователи: username / password123"
