"""
Agregator Service - Главный файл приложения
Агрегатор услуг и исполнителей
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Импорты из локальных модулей
from database import engine, SessionLocal
from models import User, UserRole

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Проверяем подключение к базе данных
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Подключение к базе данных успешно установлено")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к базе данных: {e}")
        raise

    # Проверяем наличие администратора
    try:
        with SessionLocal() as db:
            admin = db.query(User).filter(User.username == "admin").first()
            if not admin:
                logger.warning("⚠️ Администратор не найден. Запустите: python3 create_admin.py")
            else:
                logger.info("✅ Администратор найден")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка проверки администратора: {e}")

    yield

# Создание приложения FastAPI
app = FastAPI(
    title="Agregator Service - Агрегатор услуг и исполнителей",
    description="Сервис для управления заказами услуг и исполнителями",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://91.222.236.58:3000",
        "http://91.222.236.58",
        "https://91.222.236.58:3000",
        "https://91.222.236.58",
        "http://localhost:3000",  # Для локальной разработки
        "http://127.0.0.1:3000",  # Для локальной разработки
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    # Логируем входящий запрос
    logger.info(f"🔍 {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Логируем время выполнения
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"⏱️ {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
    
    return response

# Простой тестовый endpoint
@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Agregator Service - Агрегатор услуг и исполнителей",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Обновляем forward references для Pydantic моделей (Pydantic v2)
from api.v1.schemas import RepairRequestResponse, ContractorResponseResponse

# Подключение роутеров
from api.v1.endpoints.auth import router as auth_router
app.include_router(auth_router, prefix="/api/v1/auth", tags=["🔐 Аутентификация"])

from api.v1.endpoints.contractor_verification import router as contractor_verification_router
app.include_router(contractor_verification_router, prefix="/api/v1", tags=["✅ Верификация исполнителей"])

from api.v1.endpoints.repair_requests import router as repair_requests_router
app.include_router(repair_requests_router, prefix="/api/v1/repair-requests", tags=["🔧 Заявки на ремонт"])

from api.v1.endpoints.contractors import router as contractors_router
app.include_router(contractors_router, prefix="/api/v1/contractors", tags=["👷 Исполнители"])

from api.v1.endpoints.customers import router as customers_router
app.include_router(customers_router, prefix="/api/v1/customers", tags=["👤 Заказчики"])

from api.v1.endpoints.request_workflow import router as request_workflow_router
app.include_router(request_workflow_router, prefix="/api/v1/workflow", tags=["🔄 Workflow заявок"])

from api.v1.endpoints.manager_dashboard import router as manager_dashboard_router
app.include_router(manager_dashboard_router, prefix="/api/v1/manager", tags=["📊 Дашборд менеджера"])

from api.v1.endpoints.security_verification import router as security_verification_router
app.include_router(security_verification_router, prefix="/api/v1/security", tags=["🔒 Служба безопасности"])

from api.v1.endpoints.hr_documents import router as hr_documents_router
app.include_router(hr_documents_router, prefix="/api/v1/hr", tags=["📋 HR документы"])

from api.v1.endpoints.telegram_bot import router as telegram_bot_router
app.include_router(telegram_bot_router, prefix="/api/v1/telegram", tags=["🤖 Telegram бот"])

from api.v1.endpoints.customer_cabinet import router as customer_cabinet_router
app.include_router(customer_cabinet_router, prefix="/api/v1/customer", tags=["👤 Личный кабинет заказчика"])

from api.v1.endpoints.admin_panel import router as admin_panel_router
app.include_router(admin_panel_router, prefix="/api/v1/admin", tags=["⚙️ Админ панель"])

from api.v1.endpoints.dashboard import router as dashboard_router
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["📊 Главная страница"])

from api.v1.endpoints.avatar import router as avatar_router
app.include_router(avatar_router, prefix="/api/v1/avatar", tags=["🖼️ Аватары"])

from api.v1.endpoints.users import router as users_router
app.include_router(users_router, prefix="/api/v1/users", tags=["👤 Пользователи"])

from api.v1.endpoints.telegram_chat import router as telegram_chat_router
app.include_router(telegram_chat_router, prefix="/api/v1/telegram-chat", tags=["💬 Telegram чат"])

# Глобальные обработчики исключений
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "http_exception",
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Внутренняя ошибка сервера",
            "type": "internal_error",
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)