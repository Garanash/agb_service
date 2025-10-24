# 🚀 Деплой Agregator Service на сервер 91.222.236.58

## 📋 Требования

- Docker и Docker Compose установлены на сервере
- Порты 3000, 8000, 5435, 6379 доступны
- Минимум 2GB RAM и 10GB свободного места

## 🔧 Быстрый деплой

1. **Скопируйте проект на сервер:**
   ```bash
   scp -r agregator-service/ user@91.222.236.58:/home/user/
   ```

2. **Подключитесь к серверу:**
   ```bash
   ssh user@91.222.236.58
   ```

3. **Перейдите в директорию проекта:**
   ```bash
   cd /home/user/agregator-service
   ```

4. **Настройте переменные окружения:**
   ```bash
   cp env.production .env
   # Отредактируйте .env файл с вашими настройками
   ```

5. **Запустите деплой:**
   ```bash
   ./deploy.sh
   ```

## 🌐 Доступ к приложению

- **Frontend:** http://91.222.236.58:3000
- **Backend API:** http://91.222.236.58:8000
- **API Documentation:** http://91.222.236.58:8000/docs

## 🔍 Проверка работы

```bash
# Проверка статуса контейнеров
docker-compose ps

# Проверка логов
docker-compose logs -f

# Проверка health checks
curl http://91.222.236.58:8000/health
curl http://91.222.236.58:3000/health
```

## 🛠️ Управление

```bash
# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Обновление
docker-compose pull
docker-compose up -d

# Просмотр логов
docker-compose logs -f [service_name]
```

## 🔒 Безопасность

- Измените пароли в `.env` файле
- Настройте firewall для ограничения доступа к портам
- Используйте HTTPS в продакшене
- Регулярно обновляйте зависимости

## 📊 Мониторинг

- Логи: `docker-compose logs -f`
- Статус: `docker-compose ps`
- Ресурсы: `docker stats`

## 🆘 Устранение проблем

1. **Контейнеры не запускаются:**
   ```bash
   docker-compose logs
   ```

2. **CORS ошибки:**
   - Проверьте настройки в `backend/main.py`
   - Убедитесь, что IP адрес правильный

3. **База данных недоступна:**
   ```bash
   docker-compose logs agregator-db
   ```

4. **Frontend не загружается:**
   ```bash
   docker-compose logs agregator-frontend
   ```
