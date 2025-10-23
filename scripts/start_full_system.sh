#!/bin/bash

echo "🚀 Полный запуск системы с Kafka"

# Проверяем, что Docker запущен
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker не запущен. Запустите Docker и попробуйте снова."
    exit 1
fi

# Проверяем, что Python установлен
if ! python --version > /dev/null 2>&1; then
    echo "❌ Python не установлен. Установите Python и попробуйте снова."
    exit 1
fi

echo "✅ Предварительные проверки пройдены"

# Останавливаем существующие контейнеры
echo "🛑 Остановка существующих контейнеров..."
docker-compose -f docker-compose.yml down 2>/dev/null || true
docker-compose -f docker-compose.kafka.yml down 2>/dev/null || true

# Запускаем Kafka кластер
echo "☁️ Запуск Kafka кластера..."
docker-compose -f docker-compose.kafka.yml up -d

# Ждем запуска Kafka
echo "⏳ Ожидание запуска Kafka кластера..."
sleep 30

# Проверяем статус Kafka
echo "📊 Статус Kafka сервисов:"
docker-compose -f docker-compose.kafka.yml ps

# Создаем топики
echo "📝 Создание топиков Kafka..."
if [ -f "./scripts/create_topics.sh" ]; then
    chmod +x ./scripts/create_topics.sh
    ./scripts/create_topics.sh
else
    echo "⚠️ Скрипт создания топиков не найден"
fi

# Устанавливаем зависимости Python
echo "📦 Установка зависимостей Python..."
cd backend
pip install -r requirements.txt
cd ..

# Запускаем основное приложение
echo "🌐 Запуск основного приложения..."
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
APP_PID=$!
cd ..

# Ждем запуска приложения
echo "⏳ Ожидание запуска приложения..."
sleep 10

# Запускаем Kafka consumers
echo "📨 Запуск Kafka consumers..."
cd backend
python kafka_service_main.py &
KAFKA_PID=$!
cd ..

# Ждем запуска consumers
echo "⏳ Ожидание запуска consumers..."
sleep 5

# Проверяем статус
echo "📊 Статус всех сервисов:"
echo "🌐 Основное приложение: http://localhost:8000"
echo "📱 Kafka UI: http://localhost:8080"
echo "📊 API документация: http://localhost:8000/docs"

# Проверяем подключение к Kafka
echo "🔍 Проверка подключения к Kafka..."
if [ -f "./scripts/test_kafka.py" ]; then
    python ./scripts/test_kafka.py
    if [ $? -eq 0 ]; then
        echo "✅ Kafka тесты прошли успешно"
    else
        echo "❌ Kafka тесты не прошли"
    fi
else
    echo "⚠️ Скрипт тестирования Kafka не найден"
fi

# Проверяем мониторинг
echo "📊 Запуск мониторинга Kafka..."
if [ -f "./scripts/monitor_kafka.py" ]; then
    python ./scripts/monitor_kafka.py
else
    echo "⚠️ Скрипт мониторинга Kafka не найден"
fi

echo ""
echo "🎉 Система запущена успешно!"
echo ""
echo "📋 Доступные сервисы:"
echo "   🌐 Основное приложение: http://localhost:8000"
echo "   📱 Kafka UI: http://localhost:8080"
echo "   📊 API документация: http://localhost:8000/docs"
echo ""
echo "🛑 Для остановки системы нажмите Ctrl+C"

# Функция для graceful shutdown
cleanup() {
    echo ""
    echo "🛑 Остановка системы..."
    
    # Останавливаем процессы
    if [ ! -z "$APP_PID" ]; then
        kill $APP_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$KAFKA_PID" ]; then
        kill $KAFKA_PID 2>/dev/null || true
    fi
    
    # Останавливаем контейнеры
    docker-compose -f docker-compose.kafka.yml down
    docker-compose -f docker-compose.yml down
    
    echo "✅ Система остановлена"
    exit 0
}

# Устанавливаем обработчик сигналов
trap cleanup SIGINT SIGTERM

# Ждем завершения
wait
