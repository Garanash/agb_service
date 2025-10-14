# Линтинг и качество кода проекта AGB SERVICE

Этот документ описывает систему линтинга и проверки качества кода для проекта AGB SERVICE, включая настройку инструментов для Python и TypeScript/React.

## 📋 Инструменты линтинга

### Backend (Python)

- **Black** - автоматическое форматирование кода
- **isort** - сортировка и организация импортов
- **flake8** - проверка стиля кода и ошибок
- **pylint** - статический анализ кода
- **mypy** - проверка типов
- **bandit** - проверка безопасности

### Frontend (TypeScript/React)

- **ESLint** - проверка кода и ошибок
- **Prettier** - автоматическое форматирование
- **TypeScript** - проверка типов

## 🚀 Запуск линтинга

### Автоматический запуск всех проверок

```bash
./run_linting.sh
```

### Запуск отдельных групп проверок

```bash
# Только backend линтинг
./run_linting.sh backend

# Только frontend линтинг
./run_linting.sh frontend

# Автоисправление проблем
./run_linting.sh fix

# Генерация отчетов
./run_linting.sh report
```

### Ручной запуск проверок

#### Backend проверки

```bash
# Black - форматирование кода
docker exec agregator_backend black --check backend/
docker exec agregator_backend black backend/  # автоисправление

# isort - сортировка импортов
docker exec agregator_backend isort --check-only backend/
docker exec agregator_backend isort backend/  # автоисправление

# flake8 - проверка стиля
docker exec agregator_backend flake8 backend/

# pylint - статический анализ
docker exec agregator_backend pylint backend/

# mypy - проверка типов
docker exec agregator_backend mypy backend/

# bandit - проверка безопасности
docker exec agregator_backend bandit -r backend/
```

#### Frontend проверки

```bash
# ESLint - проверка кода
docker exec agregator_frontend npm run lint
docker exec agregator_frontend npm run lint:fix  # автоисправление

# Prettier - форматирование
docker exec agregator_frontend npm run format:check
docker exec agregator_frontend npm run format  # автоисправление

# TypeScript - проверка типов
docker exec agregator_frontend npm run type-check

# Все проверки сразу
docker exec agregator_frontend npm run lint:all
```

## ⚙️ Конфигурация

### Backend конфигурация

#### .flake8
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
exclude = .git,__pycache__,.pytest_cache,.mypy_cache,venv,env,.venv,.env,migrations,tests,node_modules
per-file-ignores = __init__.py:F401,migrations/*:E501
max-complexity = 10
select = C,E,F,W,B,B950
ignore = E203,W503
```

#### pyproject.toml (Black)
```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | venv
  | _build
  | buck-out
  | build
  | dist
  | migrations
)/
'''
```

#### pyproject.toml (isort)
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["migrations/*"]
known_first_party = ["backend", "services", "api", "models", "database"]
```

#### pyproject.toml (mypy)
```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
show_error_codes = true
```

### Frontend конфигурация

#### .eslintrc.json
```json
{
  "env": {
    "browser": true,
    "es2021": true,
    "node": true,
    "jest": true
  },
  "extends": [
    "react-app",
    "react-app/jest",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaFeatures": {
      "jsx": true
    },
    "ecmaVersion": "latest",
    "sourceType": "module",
    "project": "./tsconfig.json"
  },
  "plugins": [
    "react",
    "react-hooks",
    "@typescript-eslint",
    "prettier"
  ],
  "rules": {
    "prettier/prettier": "error",
    "react/react-in-jsx-scope": "off",
    "react/prop-types": "off",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/no-explicit-any": "warn",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "no-console": "warn",
    "no-debugger": "error",
    "prefer-const": "error",
    "no-var": "error"
  }
}
```

#### .prettierrc
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "bracketSameLine": false,
  "arrowParens": "avoid",
  "endOfLine": "lf",
  "jsxSingleQuote": true,
  "proseWrap": "preserve"
}
```

## 📊 Стандарты качества

### Backend стандарты

- **Длина строки**: максимум 88 символов (Black стандарт)
- **Сложность функций**: максимум 10 (flake8)
- **Типизация**: обязательна для всех функций (mypy)
- **Безопасность**: проверка на уязвимости (bandit)
- **Стиль кода**: PEP 8 с исключениями для Black

### Frontend стандарты

- **Длина строки**: максимум 80 символов
- **Типизация**: строгая проверка TypeScript
- **React Hooks**: соблюдение правил хуков
- **Форматирование**: единообразное с Prettier
- **Импорты**: организованные и отсортированные

## 🔧 Интеграция с IDE

### VS Code

Рекомендуемые расширения:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.mypy-type-checker",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

Настройки VS Code:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "eslint.validate": ["javascript", "typescript", "javascriptreact", "typescriptreact"],
  "prettier.requireConfig": true
}
```

## 🚨 Обработка ошибок

### Частые ошибки Backend

1. **E501 - строка слишком длинная**
   ```bash
   # Решение: использовать Black для автоформатирования
   black backend/
   ```

2. **F401 - неиспользуемый импорт**
   ```bash
   # Решение: удалить неиспользуемые импорты
   isort backend/
   ```

3. **W503 - оператор перед двоеточием**
   ```bash
   # Решение: игнорируется в конфигурации flake8
   ```

### Частые ошибки Frontend

1. **no-unused-vars - неиспользуемые переменные**
   ```bash
   # Решение: удалить или использовать префикс _
   npm run lint:fix
   ```

2. **prettier/prettier - проблемы форматирования**
   ```bash
   # Решение: автоформатирование
   npm run format
   ```

3. **react-hooks/exhaustive-deps - зависимости хуков**
   ```bash
   # Решение: добавить зависимости в массив deps
   ```

## 📈 Отчеты и метрики

### Генерация отчетов

```bash
# Генерация всех отчетов
./run_linting.sh report

# Отчеты сохраняются в reports/linting/
ls reports/linting/
# backend-flake8.json
# backend-pylint.json
# backend-mypy/
# frontend-eslint.json
```

### CI/CD интеграция

Команды для CI:

```bash
# Backend проверки в CI
black --check backend/
isort --check-only backend/
flake8 backend/
mypy backend/ --ignore-missing-imports

# Frontend проверки в CI
npm run lint:all
```

## 🎯 Цели качества

### Метрики качества

- **Покрытие линтингом**: 100% файлов
- **Ошибки**: 0 критических ошибок
- **Предупреждения**: минимум предупреждений
- **Форматирование**: единообразное во всем проекте
- **Типизация**: строгая типизация

### Процесс улучшения

1. **Ежедневно**: автоисправление форматирования
2. **Еженедельно**: проверка всех инструментов
3. **Перед коммитом**: запуск линтинга
4. **В CI/CD**: автоматические проверки

## 📚 Полезные ресурсы

- [Black документация](https://black.readthedocs.io/)
- [flake8 документация](https://flake8.pycqa.org/)
- [pylint документация](https://pylint.pycqa.org/)
- [mypy документация](https://mypy.readthedocs.io/)
- [ESLint документация](https://eslint.org/)
- [Prettier документация](https://prettier.io/)
- [TypeScript документация](https://www.typescriptlang.org/)
