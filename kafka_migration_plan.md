# 🚀 План миграции на Apache Kafka

## 📋 Обзор миграции

### Цели миграции
- ✅ **Ускорение обработки** заказов в 3-5 раз
- ✅ **Улучшение масштабируемости** - горизонтальное масштабирование сервисов
- ✅ **Повышение надежности** - гарантированная доставка сообщений
- ✅ **Устранение синхронных вызовов** - переход на асинхронную архитектуру
- ✅ **Предотвращение потери данных** - репликация и персистентность

### Текущие проблемы
- 🐌 Медленная обработка пиковых нагрузок
- 🔗 Синхронные вызовы между сервисами
- 💥 Потеря данных при сбоях
- 📈 Сложность масштабирования
- 🔍 Отсутствие централизованного логирования

## 🗓️ Этапы миграции

### Этап 1: Подготовка инфраструктуры (1-2 недели)

#### 1.1 Установка и настройка Kafka кластера
```bash
# Запуск Kafka кластера
./start_kafka_cluster.sh

# Создание топиков
./create_topics.sh

# Проверка работоспособности
./health_check.sh
```

**Результат:** Готовый к работе Kafka кластер с 3 нодами

#### 1.2 Настройка мониторинга
- Установка Kafka UI для визуального мониторинга
- Настройка Prometheus + Grafana для метрик
- Конфигурация алертов

**Результат:** Полный мониторинг кластера

#### 1.3 Создание базовых классов
- `KafkaConfig` - конфигурация
- `BaseEvent` - базовые схемы событий
- `KafkaEventProducer` - producer
- `KafkaEventConsumer` - consumer

**Результат:** Готовая библиотека для работы с Kafka

### Этап 2: Пилотное внедрение (2-3 недели)

#### 2.1 Миграция создания заявок
**Приоритет:** Высокий
**Сложность:** Средняя

**Текущий процесс:**
```python
# Синхронный процесс
def create_request(data):
    request = save_to_db(data)  # Блокирующий вызов
    send_email_notification()   # Блокирующий вызов
    notify_managers()          # Блокирующий вызов
    return request
```

**Новый процесс:**
```python
# Асинхронный процесс
def create_request(data):
    request = save_to_db(data)  # Только сохранение в БД
    
    # Публикация события
    event = RequestCreatedEvent(
        request_id=request.id,
        customer_id=request.customer_id,
        # ... другие поля
    )
    kafka_producer.publish_event("request-events", event)
    
    return request  # Быстрый ответ клиенту
```

**Изменения в коде:**
1. Модификация `CreateRequestPage.tsx` - убрать ожидание уведомлений
2. Обновление `RequestWorkflowService.create_request()`
3. Создание `NotificationServiceConsumer` для обработки событий

**Тестирование:**
- Unit тесты для producer/consumer
- Integration тесты с реальным Kafka
- Load тесты для проверки производительности

#### 2.2 Миграция уведомлений
**Приоритет:** Высокий
**Сложность:** Низкая

**Текущий процесс:**
```python
# Синхронные уведомления
def assign_contractor(request_id, contractor_id):
    update_request_status(request_id, "assigned")
    send_telegram_notification(contractor_id)  # Блокирующий
    send_email_to_customer()                   # Блокирующий
```

**Новый процесс:**
```python
# Асинхронные уведомления
def assign_contractor(request_id, contractor_id):
    update_request_status(request_id, "assigned")
    
    # Публикация события
    event = WorkflowContractorAssignedEvent(
        request_id=request_id,
        contractor_id=contractor_id,
        # ...
    )
    kafka_producer.publish_event("workflow-events", event)
```

**Изменения в коде:**
1. Обновление `RequestWorkflowService.assign_contractor()`
2. Создание `TelegramNotificationConsumer`
3. Создание `EmailNotificationConsumer`

### Этап 3: Расширение функциональности (3-4 недели)

#### 3.1 Миграция workflow заявок
**Приоритет:** Средний
**Сложность:** Высокая

**События для миграции:**
- `workflow.manager_assigned`
- `workflow.sent_to_contractors`
- `workflow.work_started`
- `workflow.work_completed`
- `workflow.status_changed`

**Изменения в коде:**
1. Обновление всех методов в `RequestWorkflowService`
2. Создание `WorkflowEventConsumer`
3. Модификация `ManagerWorkflowPage.tsx`

#### 3.2 Миграция системы безопасности
**Приоритет:** Средний
**Сложность:** Средняя

**События для миграции:**
- `security.contractor_verified`
- `security.contractor_rejected`
- `security.access_granted`
- `security.access_revoked`

**Изменения в коде:**
1. Обновление `SecurityVerificationService`
2. Создание `SecurityEventConsumer`
3. Модификация `SecurityVerificationPage.tsx`

#### 3.3 Миграция HR системы
**Приоритет:** Низкий
**Сложность:** Средняя

**События для миграции:**
- `hr.document_created`
- `hr.document_signed`
- `hr.contract_generated`
- `hr.payment_processed`

**Изменения в коде:**
1. Обновление `HRDocumentService`
2. Создание `HREventConsumer`
3. Модификация `HRDocumentsPage.tsx`

### Этап 4: Аудит и аналитика (2-3 недели)

#### 4.1 Внедрение аудита
**Приоритет:** Высокий
**Сложность:** Низкая

**События для аудита:**
- `audit.user_action`
- `audit.system_event`
- `audit.error_occurred`
- `audit.performance_metric`

**Изменения в коде:**
1. Добавление аудита во все критические операции
2. Создание `AuditEventConsumer`
3. Настройка ClickHouse для аналитики

#### 4.2 Настройка аналитики
- Интеграция с ClickHouse
- Создание дашбордов в Grafana
- Настройка алертов

### Этап 5: Оптимизация и мониторинг (1-2 недели)

#### 5.1 Оптимизация производительности
- Настройка партиционирования
- Оптимизация размеров сообщений
- Настройка сжатия

#### 5.2 Полный мониторинг
- Настройка всех метрик
- Создание дашбордов
- Настройка алертов

## 🔄 Стратегия миграции

### Dual-Write подход
```python
class RequestServiceMigration:
    def create_request(self, data):
        # Сохраняем в БД (как раньше)
        request = self._save_to_db(data)
        
        # Публикуем событие (новый функционал)
        try:
            event = RequestCreatedEvent(
                request_id=request.id,
                customer_id=request.customer_id,
                # ...
            )
            kafka_producer.publish_event("request-events", event)
        except Exception as e:
            logger.error(f"Ошибка публикации события: {e}")
            # Не прерываем основной процесс
        
        return request
```

### Постепенное переключение
1. **Фаза 1:** Dual-write (старая + новая логика)
2. **Фаза 2:** Проверка корректности новой логики
3. **Фаза 3:** Переключение на новую логику
4. **Фаза 4:** Удаление старой логики

### Rollback план
```python
class RollbackManager:
    def rollback_to_sync(self):
        """Откат к синхронной обработке"""
        # Отключаем Kafka consumers
        # Включаем синхронные вызовы
        # Логируем события для последующей обработки
    
    def process_pending_events(self):
        """Обработка накопившихся событий"""
        # Читаем события из Kafka
        # Обрабатываем их синхронно
        # Удаляем обработанные события
```

## 📊 Метрики успеха

### Производительность
- **Время отклика API:** < 200ms (было 2-5s)
- **Пропускная способность:** 1000+ заявок/мин (было 100-200)
- **Время обработки заявки:** < 30s (было 2-5 мин)

### Надежность
- **Доставка сообщений:** 99.99%
- **Потеря данных:** 0%
- **Время восстановления:** < 30s

### Масштабируемость
- **Горизонтальное масштабирование:** +300% производительности
- **Пиковые нагрузки:** обработка без деградации
- **Ресурсы:** снижение CPU на 40%

## 🧪 План тестирования

### Unit тесты
```python
def test_request_created_event():
    """Тест создания события заявки"""
    event = RequestCreatedEvent(
        request_id=123,
        customer_id=456,
        title="Test Request"
    )
    
    assert event.event_type == EventType.REQUEST_CREATED
    assert event.request_id == 123
    assert event.customer_id == 456

def test_kafka_producer():
    """Тест Kafka producer"""
    producer = KafkaEventProducer()
    event = RequestCreatedEvent(request_id=123, customer_id=456, title="Test")
    
    success = producer.publish_event("request-events", event)
    assert success == True
```

### Integration тесты
```python
def test_end_to_end_request_flow():
    """Тест полного потока создания заявки"""
    # 1. Создаем заявку
    response = client.post("/api/v1/requests", json=request_data)
    assert response.status_code == 201
    
    # 2. Проверяем событие в Kafka
    consumer = KafkaEventConsumer(["request-events"])
    messages = consumer.poll(timeout_ms=5000)
    assert len(messages) > 0
    
    # 3. Проверяем уведомления
    # Проверяем email
    # Проверяем Telegram
```

### Load тесты
```python
def test_high_load():
    """Тест высокой нагрузки"""
    # Создаем 1000 заявок одновременно
    tasks = []
    for i in range(1000):
        task = asyncio.create_task(create_request_async(request_data))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # Проверяем, что все заявки созданы
    assert len(results) == 1000
    
    # Проверяем производительность
    assert all(r.status_code == 201 for r in results)
```

### Chaos тесты
```python
def test_kafka_broker_failure():
    """Тест отказоустойчивости при сбое брокера"""
    # Останавливаем один брокер
    docker.stop("kafka-2")
    
    # Продолжаем работу
    response = client.post("/api/v1/requests", json=request_data)
    assert response.status_code == 201
    
    # Запускаем брокер обратно
    docker.start("kafka-2")
    
    # Проверяем, что события обработаны
    # после восстановления
```

## 🚨 Риски и митигация

### Технические риски

#### 1. Потеря сообщений
**Риск:** Высокий
**Митигация:**
- Настройка `acks=all`
- Включение retry механизмов
- Использование Dead Letter Queues
- Мониторинг consumer lag

#### 2. Производительность Kafka
**Риск:** Средний
**Митигация:**
- Правильное партиционирование
- Оптимизация размеров сообщений
- Настройка сжатия
- Мониторинг метрик

#### 3. Сложность отладки
**Риск:** Средний
**Митигация:**
- Централизованное логирование
- Трассировка событий
- Kafka UI для мониторинга
- Подробные метрики

### Бизнес риски

#### 1. Простой системы
**Риск:** Высокий
**Митигация:**
- Поэтапная миграция
- Dual-write подход
- Rollback план
- Тщательное тестирование

#### 2. Потеря данных
**Риск:** Высокий
**Митигация:**
- Репликация factor=3
- Персистентность сообщений
- Регулярные бэкапы
- Мониторинг целостности

## 📅 Временные рамки

| Этап | Длительность | Команда | Результат |
|------|-------------|---------|-----------|
| 1. Подготовка инфраструктуры | 1-2 недели | DevOps + Backend | Kafka кластер |
| 2. Пилотное внедрение | 2-3 недели | Backend + Frontend | Создание заявок |
| 3. Расширение функциональности | 3-4 недели | Backend + Frontend | Полный workflow |
| 4. Аудит и аналитика | 2-3 недели | Backend + DevOps | Мониторинг |
| 5. Оптимизация | 1-2 недели | Backend + DevOps | Производительность |

**Общее время:** 9-14 недель
**Команда:** 4-6 разработчиков

## 💰 Бюджет

### Инфраструктура
- **Kafka кластер:** $500-1000/месяц
- **Мониторинг:** $200-400/месяц
- **Хранилище:** $100-200/месяц

### Разработка
- **Backend разработчики:** 2-3 человека × 3 месяца
- **Frontend разработчики:** 1-2 человека × 2 месяца
- **DevOps инженер:** 1 человек × 2 месяца

### Обучение
- **Kafka обучение команды:** $2000-5000
- **Консультации экспертов:** $5000-10000

## ✅ Критерии готовности

### Технические критерии
- [ ] Kafka кластер работает стабильно
- [ ] Все топики созданы и настроены
- [ ] Мониторинг настроен и работает
- [ ] Unit тесты покрывают 90% кода
- [ ] Integration тесты проходят
- [ ] Load тесты показывают требуемую производительность

### Бизнес критерии
- [ ] Время отклика API < 200ms
- [ ] Пропускная способность > 1000 заявок/мин
- [ ] Доставка сообщений > 99.9%
- [ ] Команда обучена работе с Kafka
- [ ] Документация создана
- [ ] Rollback план протестирован

## 🎯 Следующие шаги

1. **Утверждение плана** руководством
2. **Формирование команды** проекта
3. **Заказ инфраструктуры** для Kafka
4. **Начало Этапа 1** - подготовка инфраструктуры
5. **Еженедельные ретроспективы** и корректировка плана

