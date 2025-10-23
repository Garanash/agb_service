# Multi-stage Dockerfile для frontend
# Этап 1: Сборка приложения
FROM node:18-alpine as builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install --silent

# Копируем исходный код
COPY . ./

# Сборка приложения для продакшена
RUN DISABLE_ESLINT_PLUGIN=true TSC_COMPILE_ON_ERROR=true npm run build

# Этап 2: Production образ с nginx
FROM nginx:alpine as production

# Устанавливаем curl для health check
RUN apk add --no-cache curl

# Копируем собранное приложение
COPY --from=builder /app/build /usr/share/nginx/html

# Копируем конфигурацию nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Создаем пользователя для безопасности (если не существует)
RUN if ! id nginx >/dev/null 2>&1; then \
      addgroup -g 1001 -S nginx && \
      adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx; \
    fi

# Устанавливаем права доступа
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d

# Переключаемся на непривилегированного пользователя
USER nginx

# Открываем порт
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1

# Команда запуска
CMD ["nginx", "-g", "daemon off;"]