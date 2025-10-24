# Инструкция по исправлению ошибки авторизации

## Проблема
Ошибка 500 при попытке входа в систему возникает из-за несоответствия схем хеширования паролей:
- В коде авторизации используется `passlib` с схемой `sha256_crypt`
- В скрипте инициализации использовался `bcrypt`

## Решение

### Вариант 1: Исправление существующих пользователей (рекомендуется)

1. Загрузите исправленные файлы на сервер:
```bash
# Загрузите файлы fix_passwords.py и fix_passwords.sh на сервер
scp fix_passwords.py root@91.222.236.58:/root/agregator-service/
scp fix_passwords.sh root@91.222.236.58:/root/agregator-service/
```

2. Подключитесь к серверу и запустите исправление:
```bash
ssh root@91.222.236.58
cd /root/agregator-service
chmod +x fix_passwords.sh
./fix_passwords.sh
```

### Вариант 2: Пересоздание базы данных

1. Остановите контейнеры:
```bash
docker-compose down
```

2. Удалите данные базы данных:
```bash
docker volume rm agregator-service_agregator_postgres_data
```

3. Запустите контейнеры заново:
```bash
docker-compose up -d
```

4. Подождите запуска и выполните инициализацию:
```bash
sleep 30
./init_db.sh
```

## Проверка

После исправления попробуйте войти в систему:
- URL: http://91.222.236.58:3000/login
- Логин: admin
- Пароль: admin123

## Дополнительные пользователи

После исправления будут доступны следующие пользователи:
- admin / admin123 (администратор)
- customer1 / password123 (заказчик)
- contractor1 / password123 (исполнитель)
- manager1 / password123 (менеджер)
- security1 / password123 (служба безопасности)
- hr1 / password123 (отдел кадров)
