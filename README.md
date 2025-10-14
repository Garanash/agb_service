# AGB SERVICE - Агрегатор услуг и исполнителей

Полнофункциональная платформа для агрегации услуг с системой подтверждения email.

## 🚀 Возможности

- **Регистрация пользователей** с подтверждением email
- **Роли пользователей**: администратор, заказчик, исполнитель
- **Система аутентификации** с JWT токенами
- **Красивые HTML письма** с multipart/alternative структурой
- **API документация** через Swagger UI
- **Docker Compose** для локальной разработки

## 🛠 Технологии

### Backend
- **FastAPI** - современный веб-фреймворк для Python
- **PostgreSQL** - реляционная база данных
- **Redis** - кэширование и сессии
- **SQLAlchemy** - ORM для работы с БД
- **JWT** - аутентификация
- **SMTP** - отправка email писем

### Frontend
- **React** - библиотека для создания пользовательских интерфейсов
- **Material-UI** - компоненты для React
- **React Router** - маршрутизация
- **React Hook Form** - управление формами

## 📦 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd agregator-service
```

### 2. Настройка переменных окружения
Скопируйте файл `env.example` в `.env` и заполните необходимые параметры:

```bash
cp env.example .env
```

Обязательные параметры в `.env`:
```env
# Настройки почты (Mail.ru)
MAIL_USERNAME=your_email@mail.ru
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@mail.ru
MAIL_FROM_NAME=AGB SERVICE
MAIL_PORT=465
MAIL_SERVER=smtp.mail.ru
```

### 3. Запуск через Docker Compose
```bash
# Запуск всех сервисов
docker-compose up -d

# Или используйте скрипт для локальной разработки
./start-local.sh
```

### 4. Создание администратора
```bash
# Войти в контейнер backend
docker exec -it agregator_backend bash

# Создать администратора
python create_admin.py
```

## 🌐 Доступ к сервисам

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **Swagger UI**: http://localhost:8001/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📧 Настройка почты

### Получение пароля приложения для Mail.ru:

1. Войдите в свой аккаунт Mail.ru
2. Перейдите в "Настройки" → "Пароли для внешних приложений"
3. Создайте новый пароль для приложения
4. Используйте этот пароль в переменной `MAIL_PASSWORD`

### Тестирование отправки писем:

1. Зарегистрируйтесь на сайте
2. Проверьте почту на наличие письма подтверждения
3. Перейдите по ссылке для подтверждения email

## 🔧 Разработка

### Структура проекта
```
agregator-service/
├── backend/                 # Backend на FastAPI
│   ├── api/                # API endpoints
│   ├── services/           # Бизнес-логика
│   ├── models.py          # Модели данных
│   └── requirements.txt   # Python зависимости
├── frontend/              # Frontend на React
├── database/             # SQL скрипты
├── docker-compose.yml    # Docker конфигурация
└── start-local.sh       # Скрипт запуска
```

### API Endpoints

#### Аутентификация
- `POST /api/v1/auth/register` - регистрация
- `POST /api/v1/auth/login` - вход
- `POST /api/v1/auth/verify-email` - подтверждение email
- `GET /api/v1/auth/me` - текущий пользователь

#### Пользователи
- `GET /api/v1/contractors/` - список исполнителей
- `GET /api/v1/customers/` - список заказчиков

#### Заявки
- `GET /api/v1/repair-requests/` - список заявок
- `POST /api/v1/repair-requests/` - создание заявки

## 🐛 Решение проблем

### Проблемы с отправкой email:
1. Проверьте правильность пароля приложения Mail.ru
2. Убедитесь, что все переменные окружения установлены
3. Проверьте логи контейнера: `docker logs agregator_backend`

### Проблемы с базой данных:
1. Убедитесь, что PostgreSQL запущен: `docker ps`
2. Проверьте подключение: `docker exec -it agregator_db psql -U agregator_user -d agregator_db`

## 📝 Лицензия

© 2025 Neurofork. Все права защищены.

## 🤝 Поддержка

При возникновении проблем создайте issue в репозитории или обратитесь к команде разработки.