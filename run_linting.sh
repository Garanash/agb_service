#!/bin/bash

# Скрипт для запуска линтинга проекта AGB SERVICE

echo "🔍 Запуск линтинга проекта AGB SERVICE"
echo "====================================="

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

# Функция для запуска backend линтинга
run_backend_linting() {
    print_status "Запуск линтинга backend..."
    
    # Проверяем, что backend контейнер запущен
    if ! docker ps | grep -q "agregator_backend"; then
        print_warning "Backend контейнер не запущен. Запускаем..."
        docker-compose up -d agregator-backend
        sleep 10
    fi
    
    # Устанавливаем зависимости для линтинга
    print_status "Установка зависимостей для линтинга..."
    docker exec agregator_backend pip install flake8 black isort mypy pylint bandit
    
    BACKEND_SUCCESS=true
    
    # Black - форматирование кода
    print_status "Проверка форматирования кода (Black)..."
    if docker exec agregator_backend black --check backend/; then
        print_success "Black: код отформатирован правильно"
    else
        print_warning "Black: найдены проблемы с форматированием"
        print_status "Запуск автоисправления..."
        docker exec agregator_backend black backend/
        print_success "Black: форматирование исправлено"
    fi
    
    # isort - сортировка импортов
    print_status "Проверка сортировки импортов (isort)..."
    if docker exec agregator_backend isort --check-only backend/; then
        print_success "isort: импорты отсортированы правильно"
    else
        print_warning "isort: найдены проблемы с сортировкой импортов"
        print_status "Запуск автоисправления..."
        docker exec agregator_backend isort backend/
        print_success "isort: импорты отсортированы"
    fi
    
    # flake8 - проверка стиля кода
    print_status "Проверка стиля кода (flake8)..."
    if docker exec agregator_backend flake8 backend/; then
        print_success "flake8: стиль кода соответствует стандартам"
    else
        print_error "flake8: найдены проблемы со стилем кода"
        BACKEND_SUCCESS=false
    fi
    
    # pylint - статический анализ
    print_status "Статический анализ кода (pylint)..."
    if docker exec agregator_backend pylint backend/ --disable=C0114,C0116; then
        print_success "pylint: статический анализ пройден"
    else
        print_warning "pylint: найдены предупреждения (не критично)"
    fi
    
    # mypy - проверка типов
    print_status "Проверка типов (mypy)..."
    if docker exec agregator_backend mypy backend/ --ignore-missing-imports; then
        print_success "mypy: проверка типов пройдена"
    else
        print_warning "mypy: найдены проблемы с типами (не критично)"
    fi
    
    # bandit - проверка безопасности
    print_status "Проверка безопасности (bandit)..."
    if docker exec agregator_backend bandit -r backend/ -f json -o /tmp/bandit-report.json; then
        print_success "bandit: проверка безопасности пройдена"
    else
        print_warning "bandit: найдены потенциальные проблемы безопасности"
    fi
    
    return $([ "$BACKEND_SUCCESS" = true ] && echo 0 || echo 1)
}

# Функция для запуска frontend линтинга
run_frontend_linting() {
    print_status "Запуск линтинга frontend..."
    
    # Проверяем, что frontend контейнер запущен
    if ! docker ps | grep -q "agregator_frontend"; then
        print_warning "Frontend контейнер не запущен. Запускаем..."
        docker-compose up -d agregator-frontend
        sleep 10
    fi
    
    FRONTEND_SUCCESS=true
    
    # ESLint - проверка кода
    print_status "Проверка кода (ESLint)..."
    if docker exec agregator_frontend npm run lint; then
        print_success "ESLint: код соответствует стандартам"
    else
        print_error "ESLint: найдены проблемы с кодом"
        FRONTEND_SUCCESS=false
    fi
    
    # Prettier - проверка форматирования
    print_status "Проверка форматирования (Prettier)..."
    if docker exec agregator_frontend npm run format:check; then
        print_success "Prettier: код отформатирован правильно"
    else
        print_warning "Prettier: найдены проблемы с форматированием"
        print_status "Запуск автоисправления..."
        docker exec agregator_frontend npm run format
        print_success "Prettier: форматирование исправлено"
    fi
    
    # TypeScript - проверка типов
    print_status "Проверка типов (TypeScript)..."
    if docker exec agregator_frontend npm run type-check; then
        print_success "TypeScript: проверка типов пройдена"
    else
        print_error "TypeScript: найдены ошибки типов"
        FRONTEND_SUCCESS=false
    fi
    
    return $([ "$FRONTEND_SUCCESS" = true ] && echo 0 || echo 1)
}

# Функция для автоисправления проблем
run_auto_fix() {
    print_status "Запуск автоисправления проблем..."
    
    # Backend автоисправление
    print_status "Автоисправление backend..."
    docker exec agregator_backend black backend/
    docker exec agregator_backend isort backend/
    
    # Frontend автоисправление
    print_status "Автоисправление frontend..."
    docker exec agregator_frontend npm run lint:fix
    docker exec agregator_frontend npm run format
    
    print_success "Автоисправление завершено"
}

# Функция для генерации отчета
generate_report() {
    print_status "Генерация отчета о линтинге..."
    
    # Создаем директорию для отчетов
    mkdir -p reports/linting
    
    # Backend отчеты
    print_status "Генерация отчета для backend..."
    docker exec agregator_backend flake8 backend/ --format=json > reports/linting/backend-flake8.json 2>/dev/null || true
    docker exec agregator_backend pylint backend/ --output-format=json > reports/linting/backend-pylint.json 2>/dev/null || true
    docker exec agregator_backend mypy backend/ --json-report reports/linting/backend-mypy 2>/dev/null || true
    
    # Frontend отчеты
    print_status "Генерация отчета для frontend..."
    docker exec agregator_frontend npm run lint -- --format=json > reports/linting/frontend-eslint.json 2>/dev/null || true
    
    print_success "Отчеты сгенерированы в директории reports/linting/"
}

# Функция для запуска всех проверок
run_all_linting() {
    print_status "Запуск всех проверок линтинга..."
    
    BACKEND_SUCCESS=true
    FRONTEND_SUCCESS=true
    
    # Запускаем backend линтинг
    if ! run_backend_linting; then
        BACKEND_SUCCESS=false
    fi
    
    # Запускаем frontend линтинг
    if ! run_frontend_linting; then
        FRONTEND_SUCCESS=false
    fi
    
    # Выводим итоговый результат
    echo ""
    echo "====================================="
    echo "📊 ИТОГОВЫЙ РЕЗУЛЬТАТ ЛИНТИНГА"
    echo "====================================="
    
    if [ "$BACKEND_SUCCESS" = true ]; then
        print_success "Backend линтинг: ПРОЙДЕН"
    else
        print_error "Backend линтинг: ПРОВАЛЕН"
    fi
    
    if [ "$FRONTEND_SUCCESS" = true ]; then
        print_success "Frontend линтинг: ПРОЙДЕН"
    else
        print_error "Frontend линтинг: ПРОВАЛЕН"
    fi
    
    if [ "$BACKEND_SUCCESS" = true ] && [ "$FRONTEND_SUCCESS" = true ]; then
        print_success "Все проверки линтинга прошли успешно! 🎉"
        return 0
    else
        print_error "Некоторые проверки линтинга провалились! ❌"
        return 1
    fi
}

# Основная логика
case "${1:-all}" in
    "backend")
        run_backend_linting
        ;;
    "frontend")
        run_frontend_linting
        ;;
    "fix")
        run_auto_fix
        ;;
    "report")
        generate_report
        ;;
    "all")
        run_all_linting
        ;;
    *)
        echo "Использование: $0 [backend|frontend|fix|report|all]"
        echo ""
        echo "Опции:"
        echo "  backend   - Запустить только backend линтинг"
        echo "  frontend  - Запустить только frontend линтинг"
        echo "  fix       - Автоисправить проблемы форматирования"
        echo "  report    - Сгенерировать отчеты о линтинге"
        echo "  all       - Запустить все проверки линтинга (по умолчанию)"
        exit 1
        ;;
esac
