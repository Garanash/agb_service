# 🚀 Инструкции по запуску системы с Kafka

## 📋 Быстрый старт

### 1. Полный запуск системы одной командой

```bash
# Запуск всех сервисов
./scripts/start_full_system.sh
```

### 2. Проверка системы

```bash
# Проверка всех компонентов
./scripts/check_system.sh
```

## 🔧 Пошаговый запуск

### Шаг 1: Запуск Kafka кластера

```bash
# Запуск Kafka кластера
docker-compose -f docker-compose.kafka.yml up -d

# Ожидание запуска (30 секунд)
sleep 30

# Проверка статуса
docker-compose -f docker-compose.kafka.yml ps
```

### Шаг 2: Создание топиков

```bash
# Создание всех необходимых топиков
./scripts/create_topics.sh
```

### Шаг 3: Установка зависимостей

```bash
# Backend зависимости
cd backend
pip install -r requirements.txt
cd ..

# Frontend зависимости (если нужно)
cd frontend
npm install
cd ..
```

### Шаг 4: Запуск сервисов

```bash
# Запуск основного приложения
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
cd ..

# Запуск Kafka consumers
cd backend
python kafka_service_main.py &
cd ..

# Запуск frontend (если нужно)
cd frontend
npm start &
cd ..
```

## 🧪 Тестирование

### Тестирование Kafka

```bash
# Запуск тестов Kafka
python scripts/test_kafka.py
```

### Мониторинг Kafka

```bash
# Проверка состояния Kafka
python scripts/monitor_kafka.py
```

## 📊 Доступные сервисы

После успешного запуска будут доступны:

- **🌐 Основное приложение**: http://localhost:8000
- **📱 Kafka UI**: http://localhost:8080
- **📊 API документация**: http://localhost:8000/docs
- **🎨 Frontend**: http://localhost:3000

## 🔍 Проверка работоспособности

### 1. Проверка Kafka UI

Откройте http://localhost:8080 и убедитесь, что:
- Кластер подключен
- Все топики созданы
- Consumer groups активны

### 2. Проверка API

Откройте http://localhost:8000/docs и убедитесь, что:
- API документация загружается
- Все endpoints доступны

### 3. Тестирование создания заявки

```bash
# Создание тестовой заявки через API
curl -X POST "http://localhost:8000/api/v1/customers/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Тестовая заявка",
    "description": "Тестовое описание",
    "urgency": "medium",
    "address": "Тестовый адрес",
    "city": "Москва",
    "region": "Москва"
  }'
```

## 🛑 Остановка системы

### Graceful остановка

```bash
# Нажмите Ctrl+C в терминале где запущен start_full_system.sh
```

### Принудительная остановка

```bash
# Остановка всех контейнеров
docker-compose -f docker-compose.kafka.yml down
docker-compose -f docker-compose.yml down

# Остановка процессов Python
pkill -f "uvicorn main:app"
pkill -f "kafka_service_main.py"
```

## 🚨 Troubleshooting

### Проблема: Kafka не запускается

**Решение:**
1. Проверьте, что Docker запущен
2. Проверьте доступность портов 9092-9094, 2181-2183
3. Очистите volumes: `docker-compose -f docker-compose.kafka.yml down -v`

### Проблема: Топики не создаются

**Решение:**
1. Убедитесь, что Kafka кластер полностью запущен
2. Проверьте логи: `docker-compose -f docker-compose.kafka.yml logs kafka-1`
3. Создайте топики вручную через Kafka UI

### Проблема: Consumer не получает сообщения

**Решение:**
1. Проверьте group_id в конфигурации
2. Убедитесь, что топики существуют
3. Проверьте логи consumer'а

### Проблема: API не отвечает

**Решение:**
1. Проверьте подключение к базе данных
2. Убедитесь, что все зависимости установлены
3. Проверьте переменные окружения

## 📈 Мониторинг производительности

### Kafka метрики

```bash
# Просмотр метрик топиков
python scripts/monitor_kafka.py
```

### Логи приложения

```bash
# Просмотр логов backend
tail -f backend/logs/app.log

# Просмотр логов Kafka
docker-compose -f docker-compose.kafka.yml logs -f kafka-1
```

## 🔧 Настройка для продакшена

### 1. Безопасность

```bash
# Настройка SSL/TLS для Kafka
# Обновите docker-compose.kafka.yml с SSL конфигурацией
```

### 2. Масштабирование

```bash
# Увеличение количества партиций
# Обновите kafka/kafka_config.py
```

### 3. Мониторинг

```bash
# Настройка Prometheus + Grafana
# Добавьте мониторинг метрик
```

## 📚 Дополнительные ресурсы

- [Документация Kafka](https://kafka.apache.org/documentation/)
- [FastAPI документация](https://fastapi.tiangolo.com/)
- [Docker Compose документация](https://docs.docker.com/compose/)

---

**🎉 Система готова к работе! Удачного использования!**
