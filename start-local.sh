#!/bin/bash

# Agregator Service - Скрипт запуска локальной разработки

echo "🚀 Запуск Agregator Service - локальная разработка"
echo "=================================================="

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker для продолжения."
    exit 1
fi

# Проверяем наличие Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose для продолжения."
    exit 1
fi

echo "📦 Запуск базы данных и Redis..."

# Запускаем только базу данных и Redis
docker-compose up -d agregator-db agregator-redis

echo "⏳ Ожидание запуска базы данных..."
sleep 10

# Проверяем статус контейнеров
echo "📊 Статус контейнеров:"
docker-compose ps

echo ""
echo "✅ База данных и Redis запущены!"
echo ""
echo "🌐 Доступные сервисы:"
echo "   • База данных: localhost:15433"
echo "   • Redis: localhost:16379"
echo ""
echo "🔧 Для запуска бекенда выполните:"
echo "   cd backend"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   python3 main.py"
echo ""
echo "👤 Для создания администратора выполните:"
echo "   cd backend"
echo "   python3 create_admin.py"
echo ""
echo "📚 API документация будет доступна по адресу:"
echo "   http://localhost:8001/docs"