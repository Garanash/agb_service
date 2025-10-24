#!/bin/bash

# Скрипт для деплоя Agregator Service на сервер 91.222.236.58

echo "🚀 Начинаем деплой Agregator Service на сервер 91.222.236.58"

# Проверяем, что мы находимся в правильной директории
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Ошибка: docker-compose.yml не найден. Запустите скрипт из корневой директории проекта."
    exit 1
fi

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose down

# Удаляем старые образы
echo "🗑️ Удаляем старые образы..."
docker-compose down --rmi all

# Собираем новые образы
echo "🔨 Собираем новые образы..."
docker-compose build --no-cache

# Запускаем контейнеры
echo "▶️ Запускаем контейнеры..."
docker-compose up -d

# Ждем запуска
echo "⏳ Ждем запуска сервисов..."
sleep 30

# Проверяем статус
echo "📊 Проверяем статус контейнеров..."
docker-compose ps

# Проверяем health checks
echo "🏥 Проверяем health checks..."
echo "Backend health:"
curl -s http://localhost:8000/health | jq . || echo "Backend не отвечает"

echo "Frontend health:"
curl -s http://localhost:3000/health || echo "Frontend не отвечает"

echo "✅ Деплой завершен!"
echo "🌐 Приложение доступно по адресу: http://91.222.236.58:3000"
echo "🔧 API доступно по адресу: http://91.222.236.58:8000"
