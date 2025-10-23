#!/bin/bash

echo "🔍 Проверка системы агрегатора сервисных услуг"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для проверки статуса
check_status() {
    local service=$1
    local url=$2
    local expected_status=$3
    
    echo -n "🔍 Проверка $service... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Функция для проверки Docker контейнеров
check_docker() {
    local container=$1
    
    echo -n "🐳 Проверка контейнера $container... "
    
    if docker ps --format "table {{.Names}}" | grep -q "$container"; then
        echo -e "${GREEN}✅ RUNNING${NC}"
        return 0
    else
        echo -e "${RED}❌ NOT RUNNING${NC}"
        return 1
    fi
}

echo -e "${BLUE}🚀 Начало проверки системы${NC}"
echo ""

# Проверка Docker контейнеров
echo -e "${YELLOW}📋 Проверка Docker контейнеров:${NC}"
check_docker "kafka-1"
check_docker "kafka-2" 
check_docker "kafka-3"
check_docker "zookeeper-1"
check_docker "zookeeper-2"
check_docker "zookeeper-3"
check_docker "kafka-ui"
echo ""

# Проверка основных сервисов
echo -e "${YELLOW}🌐 Проверка веб-сервисов:${NC}"
check_status "Основное приложение" "http://localhost:8000/health" "200"
check_status "Kafka UI" "http://localhost:8080" "200"
check_status "API документация" "http://localhost:8000/docs" "200"
echo ""

# Проверка Kafka топиков
echo -e "${YELLOW}📨 Проверка Kafka топиков:${NC}"
if command -v python &> /dev/null; then
    if [ -f "./scripts/monitor_kafka.py" ]; then
        echo "🔍 Запуск проверки Kafka топиков..."
        python ./scripts/monitor_kafka.py
    else
        echo -e "${RED}❌ Скрипт мониторинга Kafka не найден${NC}"
    fi
else
    echo -e "${RED}❌ Python не установлен${NC}"
fi
echo ""

# Проверка тестов Kafka
echo -e "${YELLOW}🧪 Проверка тестов Kafka:${NC}"
if [ -f "./scripts/test_kafka.py" ]; then
    echo "🔍 Запуск тестов Kafka..."
    python ./scripts/test_kafka.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Тесты Kafka прошли успешно${NC}"
    else
        echo -e "${RED}❌ Тесты Kafka не прошли${NC}"
    fi
else
    echo -e "${RED}❌ Скрипт тестирования Kafka не найден${NC}"
fi
echo ""

# Проверка файлов проекта
echo -e "${YELLOW}📁 Проверка файлов проекта:${NC}"

files_to_check=(
    "backend/kafka/kafka_config.py"
    "backend/kafka/kafka_events.py"
    "backend/kafka/kafka_producer.py"
    "backend/kafka/kafka_consumer.py"
    "backend/services/notification_service_consumer.py"
    "backend/kafka_service_main.py"
    "docker-compose.kafka.yml"
    "scripts/create_topics.sh"
    "scripts/test_kafka.py"
    "scripts/monitor_kafka.py"
    "scripts/start_full_system.sh"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "📄 $file ${GREEN}✅ EXISTS${NC}"
    else
        echo -e "📄 $file ${RED}❌ MISSING${NC}"
    fi
done
echo ""

# Итоговая статистика
echo -e "${BLUE}📊 Итоговая статистика:${NC}"
echo ""

# Подсчет успешных проверок
total_checks=0
passed_checks=0

# Проверки Docker
for container in "kafka-1" "kafka-2" "kafka-3" "zookeeper-1" "zookeeper-2" "zookeeper-3" "kafka-ui"; do
    total_checks=$((total_checks + 1))
    if docker ps --format "table {{.Names}}" | grep -q "$container"; then
        passed_checks=$((passed_checks + 1))
    fi
done

# Проверки веб-сервисов
for url in "http://localhost:8000/health" "http://localhost:8080" "http://localhost:8000/docs"; do
    total_checks=$((total_checks + 1))
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200"; then
        passed_checks=$((passed_checks + 1))
    fi
done

# Проверки файлов
for file in "${files_to_check[@]}"; do
    total_checks=$((total_checks + 1))
    if [ -f "$file" ]; then
        passed_checks=$((passed_checks + 1))
    fi
done

echo -e "✅ Успешных проверок: ${GREEN}$passed_checks${NC} из ${BLUE}$total_checks${NC}"

if [ $passed_checks -eq $total_checks ]; then
    echo -e "${GREEN}🎉 Все проверки прошли успешно! Система готова к работе.${NC}"
    exit 0
elif [ $passed_checks -gt $((total_checks / 2)) ]; then
    echo -e "${YELLOW}⚠️ Большинство проверок прошли успешно. Система частично готова.${NC}"
    exit 1
else
    echo -e "${RED}❌ Много проверок не прошли. Система требует внимания.${NC}"
    exit 2
fi
