# Оптимизация сборки проекта AGB SERVICE

Этот документ описывает систему оптимизации сборки для проекта AGB SERVICE, включая Docker multi-stage builds, оптимизацию frontend bundle и CI/CD pipeline.

## 🐳 Docker Multi-Stage Builds

### Backend Dockerfile

```dockerfile
# Этап 1: Сборка зависимостей
FROM python:3.11-slim as builder
RUN apt-get update && apt-get install -y build-essential libpq-dev
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Этап 2: Production образ
FROM python:3.11-slim as production
RUN apt-get update && apt-get install -y libpq5
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app
COPY backend/ /app/
RUN mkdir -p /app/logs /app/data && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Frontend Dockerfile

```dockerfile
# Этап 1: Сборка приложения
FROM node:18-alpine as builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production --silent
COPY frontend/ ./
RUN npm run build

# Этап 2: Production образ с nginx
FROM nginx:alpine as production
RUN apk add --no-cache curl
COPY --from=builder /app/build /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/nginx.conf
RUN addgroup -g 1001 -S nginx && adduser -S -D -H -u 1001 nginx
RUN chown -R nginx:nginx /usr/share/nginx/html
USER nginx
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1
CMD ["nginx", "-g", "daemon off;"]
```

## 🚀 Оптимизация Frontend Bundle

### Анализ Bundle

```bash
# Анализ текущего размера bundle
./optimize_frontend.sh analyze

# Установка bundle analyzer
docker exec agregator_frontend npm install --save-dev webpack-bundle-analyzer

# Генерация отчета
docker exec agregator_frontend npx webpack-bundle-analyzer build/static/js/*.js --mode static --report build/bundle-report.html
```

### Оптимизация изображений

```bash
# Оптимизация изображений
./optimize_frontend.sh images

# Установка инструментов оптимизации
docker exec agregator_frontend npm install --save-dev imagemin imagemin-mozjpeg imagemin-pngquant imagemin-svgo
```

### Tree Shaking

```bash
# Оптимизация tree shaking
./optimize_frontend.sh tree-shaking

# Webpack конфигурация для tree shaking
optimization: {
  usedExports: true,
  sideEffects: false,
  splitChunks: {
    chunks: 'all',
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendors',
        chunks: 'all',
      },
    },
  },
}
```

### Code Splitting

```bash
# Оптимизация code splitting
./optimize_frontend.sh code-splitting

# Lazy loading компонентов
const LazyCustomerCabinet = lazy(() => import('../pages/CustomerCabinetPage'));
const LazyManagerDashboard = lazy(() => import('../pages/ManagerDashboardPage'));
```

### Сжатие

```bash
# Настройка сжатия
./optimize_frontend.sh compression

# Nginx конфигурация для сжатия
gzip on;
gzip_comp_level 9;
gzip_types text/plain text/css application/json application/javascript;
```

## 🔧 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Run backend linting
      run: |
        cd backend
        black --check .
        flake8 .
        mypy . --ignore-missing-imports

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
    steps:
    - name: Run backend tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      run: |
        cd backend
        pytest tests/ --cov=backend --cov-report=xml

  build:
    runs-on: ubuntu-latest
    needs: [code-quality, test]
    steps:
    - name: Build and push backend image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        file: ./backend/Dockerfile
        target: production
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:${{ github.sha }}
```

## 📊 Production Configuration

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    restart: unless-stopped
    depends_on:
      backend:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: '0.25'
```

### Nginx Reverse Proxy

```nginx
upstream backend {
    server backend:8000;
    keepalive 32;
}

upstream frontend {
    server frontend:80;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    
    # SSL конфигурация
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # API роуты
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🎯 Метрики производительности

### Цели оптимизации

- **Размер bundle**: < 1MB для основного JS файла
- **Время загрузки**: < 3 секунд для первого рендера
- **Lighthouse Score**: > 90 для Performance
- **Размер Docker образа**: < 200MB для backend, < 50MB для frontend
- **Время сборки**: < 5 минут для полной сборки

### Мониторинг

```bash
# Анализ размера bundle
./optimize_frontend.sh analyze

# Проверка размера Docker образов
docker images | grep agregator

# Анализ производительности
docker exec agregator_frontend npm run build
docker exec agregator_frontend npx lighthouse http://localhost --output html --output-path reports/lighthouse.html
```

## 🔍 Отладка и профилирование

### Анализ производительности

```bash
# Анализ bundle
docker exec agregator_frontend npx webpack-bundle-analyzer build/static/js/*.js

# Профилирование React
docker exec agregator_frontend npm install --save-dev @welldone-software/why-did-you-render

# Анализ размера зависимостей
docker exec agregator_frontend npx npm-check-updates
```

### Мониторинг ресурсов

```bash
# Мониторинг использования ресурсов
docker stats agregator_backend_prod agregator_frontend_prod

# Анализ логов
docker logs agregator_backend_prod --tail 100
docker logs agregator_frontend_prod --tail 100
```

## 🚀 Развертывание

### Локальное развертывание

```bash
# Сборка и запуск production версии
docker-compose -f docker-compose.prod.yml up --build -d

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f
```

### Продакшен развертывание

```bash
# Подготовка к развертыванию
./optimize_frontend.sh all

# Сборка production образов
docker-compose -f docker-compose.prod.yml build

# Развертывание
docker-compose -f docker-compose.prod.yml up -d

# Проверка здоровья
curl -f http://localhost/health
```

## 📚 Полезные ресурсы

- [Docker Multi-stage Builds](https://docs.docker.com/develop/dev-best-practices/dockerfile_best-practices/)
- [Webpack Bundle Optimization](https://webpack.js.org/guides/code-splitting/)
- [React Performance](https://reactjs.org/docs/optimizing-performance.html)
- [Nginx Optimization](https://nginx.org/en/docs/http/ngx_http_gzip_module.html)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Security](https://docs.docker.com/engine/security/)
