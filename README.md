# Agregator Service - Полнофункциональный агрегатор услуг и исполнителей

Современное веб-приложение для управления заявками на ремонт и услуги с системой исполнителей и заказчиков.

## 🎯 Функциональность

### Роли пользователей
- **Заказчики (Customer)**: Создание и управление заявками на услуги
- **Исполнители (Contractor)**: Просмотр заявок и подача откликов  
- **Сервисные инженеры**: Управление заявками и назначение исполнителей
- **Администраторы**: Полное управление системой

### Основные возможности
- ✅ Система аутентификации и авторизации
- ✅ Создание и управление заявками на ремонт
- ✅ Профили заказчиков и исполнителей
- ✅ Система откликов исполнителей
- ✅ Современный React фронтенд с Material-UI
- ✅ RESTful API на FastAPI
- ✅ PostgreSQL база данных
- ✅ Redis для кеширования
- ✅ Docker контейнеризация

## 🏗️ Архитектура

```
agregator-service/
├── backend/                    # FastAPI бекенд
│   ├── api/v1/
│   │   ├── endpoints/         # API endpoints
│   │   ├── schemas.py         # Pydantic схемы
│   │   └── dependencies.py    # Зависимости
│   ├── models.py              # SQLAlchemy модели
│   ├── database.py            # Подключение к БД
│   ├── main.py                # Главный файл приложения
│   └── requirements.txt       # Python зависимости
├── frontend/                   # React фронтенд
│   ├── src/
│   │   ├── components/        # React компоненты
│   │   ├── pages/             # Страницы приложения
│   │   ├── services/          # API сервисы
│   │   ├── hooks/             # Пользовательские хуки
│   │   ├── types/             # TypeScript типы
│   │   └── config/            # Конфигурация
│   ├── Dockerfile             # Docker конфигурация
│   └── nginx.conf             # Nginx конфигурация
├── database/
│   └── init.sql               # SQL скрипты инициализации
├── docker-compose.yml          # Docker конфигурация
├── start-local.sh             # Скрипт запуска
└── README.md                  # Документация
```

## 🚀 Быстрый запуск

### 1. Запуск через Docker Compose (рекомендуется)

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd agregator-service

# Запустите все сервисы
docker-compose up -d

# Создайте администратора
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 create_admin.py
```

### 2. Локальная разработка

```bash
# Запуск базы данных и Redis
./start-local.sh

# Запуск бекенда
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py

# Запуск фронтенда (в новом терминале)
cd frontend
npm install
npm start
```

## 🌐 Доступные сервисы

После запуска приложение будет доступно по следующим адресам:

- **Фронтенд**: http://localhost:3000
- **Бекенд API**: http://localhost:8001
- **API документация**: http://localhost:8001/docs
- **База данных**: localhost:15433
- **Redis**: localhost:16379

## 🔑 Учетные данные по умолчанию

После создания администратора:
- **Логин**: `admin`
- **Пароль**: `admin123`

## 📚 API Endpoints

### Аутентификация
- `POST /api/v1/auth/login` - Вход в систему
- `GET /api/v1/auth/me` - Информация о пользователе

### Заявки на ремонт
- `GET /api/v1/repair-requests/` - Список заявок
- `POST /api/v1/repair-requests/` - Создание заявки
- `GET /api/v1/repair-requests/{id}` - Детали заявки
- `PUT /api/v1/repair-requests/{id}` - Обновление заявки
- `DELETE /api/v1/repair-requests/{id}` - Удаление заявки
- `POST /api/v1/repair-requests/{id}/responses` - Отклик исполнителя

### Исполнители
- `GET /api/v1/contractors/profile` - Профиль исполнителя
- `POST /api/v1/contractors/register` - Регистрация исполнителя
- `PUT /api/v1/contractors/profile` - Обновление профиля
- `POST /api/v1/contractors/upload-file` - Загрузка файлов

### Заказчики
- `GET /api/v1/customers/profile` - Профиль заказчика
- `POST /api/v1/customers/register` - Регистрация заказчика
- `PUT /api/v1/customers/profile` - Обновление профиля
- `GET /api/v1/customers/requests` - Заявки заказчика

## 🔧 Технологии

### Бекенд
- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **PostgreSQL** - основная база данных
- **Redis** - кеширование и сессии
- **JWT** - аутентификация
- **Pydantic** - валидация данных
- **Uvicorn** - ASGI сервер

### Фронтенд
- **React 18** с TypeScript
- **Material-UI** - компоненты интерфейса
- **React Router** - маршрутизация
- **React Hook Form** - управление формами
- **Axios** - HTTP клиент
- **Day.js** - работа с датами

### Инфраструктура
- **Docker** - контейнеризация
- **Docker Compose** - оркестрация
- **Nginx** - веб-сервер для фронтенда
- **PostgreSQL 15** - база данных
- **Redis 7** - кеш

## 📝 Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# База данных
DATABASE_URL=postgresql://agregator_user:agregator_password_2024@localhost:15433/agregator_db

# Redis
REDIS_URL=redis://localhost:16379

# JWT
SECRET_KEY=agregator_secret_key_2024
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Настройки
DEBUG=true
MAX_UPLOAD_SIZE=10485760
```

## 🎨 Особенности UI/UX

- **Современный дизайн** с Material Design
- **Адаптивный интерфейс** для всех устройств
- **Интуитивная навигация** с боковым меню
- **Ролевая система** с разными интерфейсами
- **Темная/светлая тема** (планируется)
- **Мобильная оптимизация**

## 🔒 Безопасность

- JWT токены для аутентификации
- Хеширование паролей с SHA256
- CORS настройки
- Валидация входных данных
- Защита от SQL инъекций через ORM

## 📊 Мониторинг и логирование

- Структурированные логи
- Health check endpoints
- Мониторинг состояния сервисов
- Обработка ошибок

## 🚀 Развертывание в продакшене

1. Настройте переменные окружения
2. Обновите настройки безопасности
3. Настройте SSL сертификаты
4. Запустите через Docker Compose:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Разработка

### Добавление новых функций

1. Создайте модели в `backend/models.py`
2. Добавьте API endpoints в `backend/api/v1/endpoints/`
3. Создайте React компоненты в `frontend/src/components/`
4. Добавьте страницы в `frontend/src/pages/`
5. Обновите типы в `frontend/src/types/`

### Тестирование

```bash
# Бекенд тесты
cd backend
python -m pytest

# Фронтенд тесты
cd frontend
npm test
```

## 📈 Планы развития

- [ ] Telegram Bot интеграция
- [ ] Система уведомлений
- [ ] Файловое хранилище
- [ ] Аналитика и отчеты
- [ ] Мобильное приложение
- [ ] Интеграция с внешними API

## 🎉 Готово к использованию!

Agregator Service полностью готов к работе и может функционировать как самостоятельное приложение для управления заказами услуг и исполнителями.

**Наслаждайтесь использованием!** 🚀