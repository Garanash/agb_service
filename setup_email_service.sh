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
echo "🇷🇺 РОССИЙСКИЕ СЕРВИСЫ (рекомендуется):"
echo "1. 📧 Mail.ru Cloud Solutions:"
echo "   - Сайт: https://mcs.mail.ru/"
echo "   - Бесплатно: до 1000 писем/месяц"
echo "   - Настройка: MAILRU_API_KEY + MAILRU_DOMAIN"
echo ""
echo "2. 📧 Yandex.Cloud Mail API:"
echo "   - Сайт: https://cloud.yandex.ru/services/mail"
echo "   - Бесплатно: до 1000 писем/месяц"
echo "   - Настройка: YANDEX_API_KEY + YANDEX_DOMAIN"
echo ""
echo "3. 📧 Unisender:"
echo "   - Сайт: https://www.unisender.com/"
echo "   - Бесплатно: до 100 писем/день"
echo "   - Настройка: UNISENDER_API_KEY"
echo ""
echo "4. 📧 SendPulse:"
echo "   - Сайт: https://sendpulse.com/"
echo "   - Бесплатно: до 15000 писем/месяц"
echo "   - Настройка: SENDPULSE_API_KEY + SENDPULSE_SECRET"
echo ""
echo "🌍 ЗАРУБЕЖНЫЕ СЕРВИСЫ:"
echo "1. 📧 SendGrid (бесплатно до 100 писем/день)"
echo "2. 📧 Mailgun (бесплатно до 10,000 писем/месяц)"
echo "3. 📧 Amazon SES (очень дешево)"
echo ""
echo "🔧 Настройка переменных окружения:"
echo "   export MAILRU_API_KEY='your_mailru_key'"
echo "   export MAILRU_DOMAIN='your_domain.mail.ru'"
echo "   export YANDEX_API_KEY='your_yandex_key'"
echo "   export UNISENDER_API_KEY='your_unisender_key'"
echo "   export SENDPULSE_API_KEY='your_sendpulse_key'"
echo "   export SENDPULSE_SECRET='your_sendpulse_secret'"
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
echo ""
echo "🇷🇺 Российские сервисы:"
echo "MAILRU_API_KEY: ${MAILRU_API_KEY:-'не настроено'}"
echo "MAILRU_DOMAIN: ${MAILRU_DOMAIN:-'не настроено'}"
echo "YANDEX_API_KEY: ${YANDEX_API_KEY:-'не настроено'}"
echo "YANDEX_DOMAIN: ${YANDEX_DOMAIN:-'не настроено'}"
echo "UNISENDER_API_KEY: ${UNISENDER_API_KEY:-'не настроено'}"
echo "SENDPULSE_API_KEY: ${SENDPULSE_API_KEY:-'не настроено'}"
echo ""
echo "🌍 Зарубежные сервисы:"
echo "SENDGRID_API_KEY: ${SENDGRID_API_KEY:-'не настроено'}"
echo "MAILGUN_API_KEY: ${MAILGUN_API_KEY:-'не настроено'}"
echo "MAILGUN_DOMAIN: ${MAILGUN_DOMAIN:-'не настроено'}"
echo ""

echo "🎯 Следующие шаги:"
echo "=================="
echo "1. 🇷🇺 РЕКОМЕНДУЕТСЯ: Зарегистрироваться на Mail.ru Cloud Solutions"
echo "2. Получить API ключи от выбранного сервиса"
echo "3. Добавить ключи в переменные окружения"
echo "4. Перезапустить приложение: docker-compose restart agregator-backend"
echo ""
echo "⭐ ЛУЧШИЙ ВЫБОР: Mail.ru Cloud Solutions"
echo "   - Высокая доставляемость в России"
echo "   - Бесплатно до 1000 писем/месяц"
echo "   - Простая настройка"
echo ""

echo "✅ Скрипт завершен!"
