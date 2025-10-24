#!/bin/bash

# Скрипт для настройки внешнего SMTP сервиса
# Этот скрипт поможет настроить отправку почты через внешние сервисы

echo "🔧 Настройка внешнего SMTP сервиса для AGB SERVICE"
echo "=================================================="

# Проверяем доступность портов
echo "📡 Проверка доступности портов..."

# Проверяем порт 443 (HTTPS) - должен быть доступен
if timeout 5 bash -c "</dev/tcp/google.com/443" 2>/dev/null; then
    echo "✅ Порт 443 (HTTPS) доступен"
else
    echo "❌ Порт 443 (HTTPS) недоступен"
fi

# Проверяем порт 80 (HTTP) - должен быть доступен
if timeout 5 bash -c "</dev/tcp/google.com/80" 2>/dev/null; then
    echo "✅ Порт 80 (HTTP) доступен"
else
    echo "❌ Порт 80 (HTTP) недоступен"
fi

# Проверяем SMTP порты
echo ""
echo "📧 Проверка SMTP портов..."

for port in 25 465 587; do
    if timeout 5 bash -c "</dev/tcp/smtp.mail.ru/$port" 2>/dev/null; then
        echo "✅ Порт $port доступен"
    else
        echo "❌ Порт $port заблокирован"
    fi
done

echo ""
echo "🛠️ Рекомендации по решению проблемы:"
echo "====================================="
echo ""
echo "1. 📧 Использовать внешние API сервисы:"
echo "   - SendGrid (бесплатно до 100 писем/день)"
echo "   - Mailgun (бесплатно до 10,000 писем/месяц)"
echo "   - Amazon SES (очень дешево)"
echo ""
echo "2. 🔧 Настроить переменные окружения:"
echo "   export SENDGRID_API_KEY='your_sendgrid_key'"
echo "   export MAILGUN_API_KEY='your_mailgun_key'"
echo "   export MAILGUN_DOMAIN='your_domain'"
echo ""
echo "3. 🌐 Использовать прокси или VPN:"
echo "   - Настроить прокси для исходящих соединений"
echo "   - Использовать VPN для обхода блокировок"
echo ""
echo "4. 📞 Обратиться к провайдеру:"
echo "   - Запросить разблокировку портов 25, 465, 587"
echo "   - Узнать о разрешенных SMTP серверах"
echo ""
echo "5. 🔄 Альтернативные решения:"
echo "   - Использовать webhook для отправки через внешний сервис"
echo "   - Настроить локальный почтовый сервер"
echo "   - Использовать облачные функции для отправки почты"
echo ""

# Проверяем текущие настройки
echo "📋 Текущие настройки почты:"
echo "============================"
echo "MAIL_FROM: ${MAIL_FROM:-'не настроено'}"
echo "MAIL_SERVER: ${MAIL_SERVER:-'не настроено'}"
echo "MAIL_PORT: ${MAIL_PORT:-'не настроено'}"
echo "MAIL_USERNAME: ${MAIL_USERNAME:-'не настроено'}"
echo "SENDGRID_API_KEY: ${SENDGRID_API_KEY:-'не настроено'}"
echo "MAILGUN_API_KEY: ${MAILGUN_API_KEY:-'не настроено'}"
echo ""

echo "🎯 Следующие шаги:"
echo "=================="
echo "1. Зарегистрироваться на SendGrid или Mailgun"
echo "2. Получить API ключи"
echo "3. Добавить ключи в переменные окружения"
echo "4. Перезапустить приложение"
echo ""

echo "✅ Скрипт завершен!"
