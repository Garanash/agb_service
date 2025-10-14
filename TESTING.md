# Тестирование проекта AGB SERVICE

Этот документ описывает систему тестирования для проекта AGB SERVICE, включая unit тесты, интеграционные тесты и frontend тесты.

## 📋 Структура тестов

```
tests/
├── conftest.py              # Конфигурация pytest и фикстуры
├── factories.py             # Фабрики для создания тестовых данных
├── unit/                    # Unit тесты
│   ├── test_services.py     # Тесты сервисов
│   └── test_models.py       # Тесты моделей
├── integration/             # Интеграционные тесты
│   └── test_api.py          # Тесты API endpoints
└── fixtures/                # Тестовые данные

frontend/src/__tests__/      # Frontend тесты
├── components/              # Тесты компонентов
├── pages/                   # Тесты страниц
├── hooks/                   # Тесты хуков
└── services/                # Тесты сервисов
```

## 🚀 Запуск тестов

### Автоматический запуск всех тестов

```bash
./run_tests.sh
```

### Запуск отдельных групп тестов

```bash
# Только backend тесты
./run_tests.sh backend

# Только frontend тесты
./run_tests.sh frontend

# Генерация отчета о покрытии
./run_tests.sh coverage

# Очистка тестовых данных
./run_tests.sh cleanup
```

### Ручной запуск тестов

#### Backend тесты

```bash
# Запуск всех тестов
docker exec agregator_backend python -m pytest tests/ -v

# Запуск unit тестов
docker exec agregator_backend python -m pytest tests/unit/ -v

# Запуск интеграционных тестов
docker exec agregator_backend python -m pytest tests/integration/ -v

# Запуск с покрытием кода
docker exec agregator_backend python -m pytest tests/ --cov=backend --cov-report=html
```

#### Frontend тесты

```bash
# Запуск всех тестов
docker exec agregator_frontend npm test

# Запуск с покрытием кода
docker exec agregator_frontend npm run test:coverage

# Запуск в CI режиме
docker exec agregator_frontend npm run test:ci
```

## 📊 Покрытие кода

### Backend покрытие

- **Цель**: минимум 80% покрытия
- **Отчет**: `backend/htmlcov/index.html`
- **Команда**: `python -m pytest tests/ --cov=backend --cov-report=html`

### Frontend покрытие

- **Цель**: минимум 70% покрытия
- **Отчет**: `frontend/coverage/lcov-report/index.html`
- **Команда**: `npm run test:coverage`

## 🧪 Типы тестов

### Unit тесты

Тестируют отдельные функции и методы в изоляции:

- **Сервисы**: EmailService, TelegramBotService, SecurityVerificationService, HRDocumentService, RequestWorkflowService
- **Модели**: User, CustomerProfile, ContractorProfile, RepairRequest, SecurityVerification, HRDocument
- **Утилиты**: функции валидации, хеширования паролей, генерации токенов

### Интеграционные тесты

Тестируют взаимодействие между компонентами:

- **API endpoints**: все REST API endpoints
- **Аутентификация**: регистрация, вход, получение текущего пользователя
- **Личный кабинет заказчика**: профиль, заявки, статистика
- **Проверка безопасности**: одобрение/отклонение исполнителей
- **HR документы**: создание, генерация, завершение документов
- **Telegram бот**: отправка уведомлений, получение информации о боте

### Frontend тесты

Тестируют React компоненты и хуки:

- **Компоненты**: Layout, формы, таблицы
- **Хуки**: useAuth, useApi
- **Сервисы**: API клиент, утилиты
- **Страницы**: основные страницы приложения

## 🔧 Конфигурация

### pytest.ini

```ini
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
asyncio_mode = "auto"
```

### package.json (Jest)

```json
{
  "jest": {
    "testEnvironment": "jsdom",
    "setupFilesAfterEnv": ["<rootDir>/src/setupTests.ts"],
    "collectCoverageFrom": [
      "src/**/*.{ts,tsx}",
      "!src/**/*.d.ts",
      "!src/index.tsx",
      "!src/reportWebVitals.ts"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 70,
        "functions": 70,
        "lines": 70,
        "statements": 70
      }
    }
  }
}
```

## 📝 Фикстуры

### Backend фикстуры

- `db_session`: сессия базы данных для тестов
- `client`: тестовый клиент FastAPI
- `async_client`: асинхронный тестовый клиент
- `test_user`: тестовый пользователь
- `test_customer_profile`: профиль заказчика
- `test_contractor_profile`: профиль исполнителя
- `test_repair_request`: заявка на ремонт
- `auth_headers`: заголовки авторизации

### Frontend фикстуры

- `TestWrapper`: обертка для тестов с роутингом и темой
- Моки для API сервисов
- Моки для localStorage и sessionStorage

## 🏭 Фабрики тестовых данных

Используется `factory-boy` для создания тестовых данных:

- `UserFactory`: создание пользователей
- `CustomerProfileFactory`: создание профилей заказчиков
- `ContractorProfileFactory`: создание профилей исполнителей
- `RepairRequestFactory`: создание заявок на ремонт
- `SecurityVerificationFactory`: создание проверок безопасности
- `HRDocumentFactory`: создание HR документов

## 🎯 Маркеры тестов

```python
@pytest.mark.unit          # Unit тесты
@pytest.mark.integration   # Интеграционные тесты
@pytest.mark.api          # API тесты
@pytest.mark.slow         # Медленные тесты
```

Запуск тестов по маркерам:

```bash
# Только unit тесты
pytest -m unit

# Только интеграционные тесты
pytest -m integration

# Исключить медленные тесты
pytest -m "not slow"
```

## 🐛 Отладка тестов

### Backend

```bash
# Запуск с подробным выводом
docker exec agregator_backend python -m pytest tests/ -v -s

# Запуск конкретного теста
docker exec agregator_backend python -m pytest tests/unit/test_services.py::TestEmailService::test_send_email_success -v

# Запуск с отладочной информацией
docker exec agregator_backend python -m pytest tests/ --pdb
```

### Frontend

```bash
# Запуск в watch режиме
docker exec agregator_frontend npm test

# Запуск конкретного теста
docker exec agregator_frontend npm test -- --testNamePattern="Layout Component"

# Запуск с отладочной информацией
docker exec agregator_frontend npm test -- --verbose
```

## 📈 Метрики качества

### Цели покрытия кода

- **Backend**: 80%+ покрытие
- **Frontend**: 70%+ покрытие
- **Критические компоненты**: 90%+ покрытие

### Качество тестов

- Каждый тест должен быть независимым
- Тесты должны быть быстрыми (< 1 секунды для unit тестов)
- Тесты должны быть читаемыми и понятными
- Тесты должны покрывать как позитивные, так и негативные сценарии

## 🔄 CI/CD интеграция

Тесты автоматически запускаются при:

- Push в main ветку
- Pull request
- Создание release

Команды для CI:

```bash
# Backend тесты в CI
python -m pytest tests/ --cov=backend --cov-report=xml --junitxml=test-results.xml

# Frontend тесты в CI
npm run test:ci
```

## 📚 Полезные ресурсы

- [pytest документация](https://docs.pytest.org/)
- [Jest документация](https://jestjs.io/docs/getting-started)
- [Testing Library документация](https://testing-library.com/)
- [Factory Boy документация](https://factoryboy.readthedocs.io/)
- [FastAPI тестирование](https://fastapi.tiangolo.com/tutorial/testing/)
