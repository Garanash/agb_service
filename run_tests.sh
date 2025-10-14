#!/bin/bash

# Скрипт для запуска всех тестов проекта

echo "🧪 Запуск тестов проекта AGB SERVICE"
echo "=================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода статуса
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверяем, что мы в корневой директории проекта
if [ ! -f "docker-compose.yml" ]; then
    print_error "Скрипт должен запускаться из корневой директории проекта"
    exit 1
fi

# Функция для запуска backend тестов
run_backend_tests() {
    print_status "Запуск backend тестов..."
    
    # Проверяем, что backend контейнер запущен
    if ! docker ps | grep -q "agregator_backend"; then
        print_warning "Backend контейнер не запущен. Запускаем..."
        docker-compose up -d agregator-backend
        sleep 10
    fi
    
    # Устанавливаем зависимости для тестирования
    print_status "Установка зависимостей для тестирования..."
    docker exec agregator_backend pip install pytest pytest-asyncio pytest-cov httpx factory-boy faker
    
    # Запускаем тесты
    print_status "Выполнение unit тестов..."
    docker exec agregator_backend python -m pytest tests/unit/ -v --tb=short
    
    if [ $? -eq 0 ]; then
        print_success "Unit тесты прошли успешно"
    else
        print_error "Unit тесты завершились с ошибками"
        return 1
    fi
    
    print_status "Выполнение интеграционных тестов..."
    docker exec agregator_backend python -m pytest tests/integration/ -v --tb=short
    
    if [ $? -eq 0 ]; then
        print_success "Интеграционные тесты прошли успешно"
    else
        print_error "Интеграционные тесты завершились с ошибками"
        return 1
    fi
    
    print_status "Генерация отчета о покрытии кода..."
    docker exec agregator_backend python -m pytest tests/ --cov=backend --cov-report=html --cov-report=term
    
    return 0
}

# Функция для запуска frontend тестов
run_frontend_tests() {
    print_status "Запуск frontend тестов..."
    
    # Проверяем, что frontend контейнер запущен
    if ! docker ps | grep -q "agregator_frontend"; then
        print_warning "Frontend контейнер не запущен. Запускаем..."
        docker-compose up -d agregator-frontend
        sleep 10
    fi
    
    # Запускаем тесты
    print_status "Выполнение frontend тестов..."
    docker exec agregator_frontend npm test -- --coverage --watchAll=false --passWithNoTests
    
    if [ $? -eq 0 ]; then
        print_success "Frontend тесты прошли успешно"
    else
        print_error "Frontend тесты завершились с ошибками"
        return 1
    fi
    
    return 0
}

# Функция для запуска всех тестов
run_all_tests() {
    print_status "Запуск всех тестов проекта..."
    
    BACKEND_SUCCESS=true
    FRONTEND_SUCCESS=true
    
    # Запускаем backend тесты
    if ! run_backend_tests; then
        BACKEND_SUCCESS=false
    fi
    
    # Запускаем frontend тесты
    if ! run_frontend_tests; then
        FRONTEND_SUCCESS=false
    fi
    
    # Выводим итоговый результат
    echo ""
    echo "=================================="
    echo "📊 ИТОГОВЫЙ РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ"
    echo "=================================="
    
    if [ "$BACKEND_SUCCESS" = true ]; then
        print_success "Backend тесты: ПРОЙДЕНЫ"
    else
        print_error "Backend тесты: ПРОВАЛЕНЫ"
    fi
    
    if [ "$FRONTEND_SUCCESS" = true ]; then
        print_success "Frontend тесты: ПРОЙДЕНЫ"
    else
        print_error "Frontend тесты: ПРОВАЛЕНЫ"
    fi
    
    if [ "$BACKEND_SUCCESS" = true ] && [ "$FRONTEND_SUCCESS" = true ]; then
        print_success "Все тесты прошли успешно! 🎉"
        return 0
    else
        print_error "Некоторые тесты провалились! ❌"
        return 1
    fi
}

# Функция для генерации отчета о покрытии
generate_coverage_report() {
    print_status "Генерация отчета о покрытии кода..."
    
    # Backend покрытие
    print_status "Генерация отчета для backend..."
    docker exec agregator_backend python -m pytest tests/ --cov=backend --cov-report=html --cov-report=term
    
    # Frontend покрытие
    print_status "Генерация отчета для frontend..."
    docker exec agregator_frontend npm run test:coverage
    
    print_success "Отчеты о покрытии сгенерированы:"
    print_status "- Backend: backend/htmlcov/index.html"
    print_status "- Frontend: frontend/coverage/lcov-report/index.html"
}

# Функция для очистки тестовых данных
cleanup_test_data() {
    print_status "Очистка тестовых данных..."
    
    # Удаляем тестовую базу данных
    docker exec agregator_backend rm -f test.db
    
    print_success "Тестовые данные очищены"
}

# Основная логика
case "${1:-all}" in
    "backend")
        run_backend_tests
        ;;
    "frontend")
        run_frontend_tests
        ;;
    "coverage")
        generate_coverage_report
        ;;
    "cleanup")
        cleanup_test_data
        ;;
    "all")
        run_all_tests
        ;;
    *)
        echo "Использование: $0 [backend|frontend|coverage|cleanup|all]"
        echo ""
        echo "Опции:"
        echo "  backend   - Запустить только backend тесты"
        echo "  frontend  - Запустить только frontend тесты"
        echo "  coverage  - Сгенерировать отчет о покрытии кода"
        echo "  cleanup   - Очистить тестовые данные"
        echo "  all       - Запустить все тесты (по умолчанию)"
        exit 1
        ;;
esac
