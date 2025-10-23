#!/bin/bash

echo "🚀 Запуск Kafka кластера"

# Проверка доступности портов
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        echo "❌ Порт $port уже занят"
        exit 1
    fi
}

# Проверяем порты
check_port 2181
check_port 2182
check_port 2183
check_port 9092
check_port 9093
check_port 9094
check_port 8080

echo "✅ Все порты свободны"

# Запускаем кластер
docker-compose -f docker-compose.kafka.yml up -d

# Ждем запуска
echo "⏳ Ожидание запуска кластера..."
sleep 30

# Проверяем статус
echo "📊 Статус сервисов:"
docker-compose -f docker-compose.kafka.yml ps

# Создаем топики
echo "📝 Создание топиков..."
./scripts/create_topics.sh

echo "🎉 Kafka кластер запущен и готов к работе!"
echo "📱 Kafka UI доступен по адресу: http://localhost:8080"
