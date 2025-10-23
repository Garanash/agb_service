#!/bin/bash

# Конфигурация
KAFKA_HOME="/opt/kafka"
BOOTSTRAP_SERVERS="localhost:9092,localhost:9093,localhost:9094"

# Функция создания топика
create_topic() {
    local topic_name=$1
    local partitions=$2
    local replication_factor=$3
    local retention_ms=$4
    
    echo "Создание топика: $topic_name"
    
    docker exec kafka-1 kafka-topics.sh \
        --bootstrap-server $BOOTSTRAP_SERVERS \
        --create \
        --topic $topic_name \
        --partitions $partitions \
        --replication-factor $replication_factor \
        --config retention.ms=$retention_ms \
        --config compression.type=snappy \
        --config min.insync.replicas=2 \
        --if-not-exists
    
    if [ $? -eq 0 ]; then
        echo "✅ Топик $topic_name создан успешно"
    else
        echo "❌ Ошибка создания топика $topic_name"
        exit 1
    fi
}

# Создание всех топиков
echo "🚀 Создание топиков Kafka для агрегатора услуг"

create_topic "request-events" 6 3 604800000      # 7 дней
create_topic "workflow-events" 3 3 2592000000    # 30 дней
create_topic "notification-events" 3 3 259200000 # 3 дня
create_topic "security-events" 3 3 7776000000    # 90 дней
create_topic "hr-events" 3 3 31536000000        # 365 дней
create_topic "audit-events" 6 3 31536000000     # 365 дней

# Создание Dead Letter Queues
create_topic "request-events-dlq" 3 3 604800000
create_topic "workflow-events-dlq" 3 3 2592000000
create_topic "notification-events-dlq" 3 3 259200000
create_topic "security-events-dlq" 3 3 7776000000
create_topic "hr-events-dlq" 3 3 31536000000
create_topic "audit-events-dlq" 6 3 31536000000

echo "🎉 Все топики созданы успешно!"

# Показать список топиков
echo "📋 Список созданных топиков:"
docker exec kafka-1 kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS --list
