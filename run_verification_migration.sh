#!/bin/bash

echo "🔄 Запуск миграции системы верификации исполнителей..."

# Проверяем, что мы в правильной директории
if [ ! -f "backend/migrate_contractor_verification.py" ]; then
    echo "❌ Файл миграции не найден. Убедитесь, что вы находитесь в корневой директории проекта."
    exit 1
fi

# Запускаем миграцию через Docker
echo "📝 Выполняем миграцию базы данных..."
docker-compose exec -T agregator-backend python /app/migrate_contractor_verification.py

if [ $? -eq 0 ]; then
    echo "✅ Миграция успешно завершена!"
    echo ""
    echo "📋 Добавленные таблицы:"
    echo "  - contractor_education (образование исполнителей)"
    echo "  - contractor_documents (документы исполнителей)"
    echo "  - contractor_verifications (верификация исполнителей)"
    echo ""
    echo "📝 Обновленные поля в contractor_profiles:"
    echo "  - Паспортные данные (passport_series, passport_number, etc.)"
    echo "  - ИНН (inn)"
    echo "  - Статусы верификации (security_verified, manager_verified, etc.)"
    echo ""
    echo "🎯 Следующие шаги:"
    echo "  1. Перезапустить backend: docker-compose restart agregator-backend"
    echo "  2. Протестировать новые API endpoints"
    echo "  3. Обновить фронтенд для работы с новой системой"
else
    echo "❌ Ошибка выполнения миграции!"
    exit 1
fi
