"""
Версия FastAPI с поддержкой базы данных
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from contextlib import asynccontextmanager

# Попытка импорта модулей базы данных
HAS_DATABASE = False
try:
    from app.core.config import settings
    print(f"🔍 DATABASE_URL from settings: {settings.DATABASE_URL}")
    from app.core.database import engine, Base, get_db
    print(f"🔍 Engine created: {engine is not None}")
    from app.models.user import User
    from app.models.model import Model
    from app.models.file import File
    from app.models.ticket import Ticket, TicketMessage
    from sqlalchemy.orm import Session
    from sqlalchemy import select
    HAS_DATABASE = True
    print("✅ Database modules imported successfully")
except ImportError as e:
    print(f"⚠️ Database modules not available: {e}")
    HAS_DATABASE = False
except Exception as e:
    print(f"⚠️ Database modules error: {e}")
    HAS_DATABASE = False

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global HAS_DATABASE
    
    # Startup
    print("🚀 Starting Telegram Mini App Backend - With Database Support...")
    
    if HAS_DATABASE and engine is not None:
        try:
            # Создание таблиц БД
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created")
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            print("🔄 Running without database...")
            HAS_DATABASE = False
    else:
        print("⚠️ No database configured, running with mock data")
        HAS_DATABASE = False
    
    print("✅ Application startup complete")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")


# Создание FastAPI приложения
app = FastAPI(
    title="Telegram Mini App API",
    description="API для каталога моделей, инструкций и поддержки",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Временно разрешаем все домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["gakshop.com", "*.gakshop.com", "*.vercel.app"]
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Telegram Mini App API - With Database Support",
        "version": "1.0.0",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "true"),
        "has_database": HAS_DATABASE and engine is not None
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0",
        "database_status": "connected" if HAS_DATABASE and engine is not None else "not_configured"
    }


@app.get("/test")
async def test_endpoint():
    """Тестовый эндпоинт для проверки работы"""
    return {
        "message": "API is working!",
        "cors_origins": ["*"],
        "has_database": HAS_DATABASE and engine is not None,
        "database_url_configured": bool(os.getenv("DATABASE_URL")),
        "database_url_from_env": os.getenv("DATABASE_URL", "NOT_SET"),
        "database_url_from_settings": getattr(settings, 'DATABASE_URL', 'NOT_SET') if 'settings' in globals() else 'NOT_IMPORTED',
        "engine_available": engine is not None if 'engine' in globals() else False
    }


# ===== AUTH ENDPOINTS =====

@app.post("/api/v1/auth/verify")
@app.options("/api/v1/auth/verify")
async def verify_auth():
    """Проверка аутентификации через Telegram"""
    return {
        "token": {
            "access_token": "test_token_12345",
            "token_type": "bearer"
        },
        "user": {
            "id": 1,
            "telegram_user_id": 123456789,
            "username": "test_user",
            "first_name": "Test",
            "last_name": "User",
            "language_code": "ru",
            "role": "user",
            "is_blocked": False,
            "full_name": "Test User",
            "is_admin": False
        }
    }


@app.get("/api/v1/auth/me")
async def get_current_user():
    """Получить информацию о текущем пользователе"""
    return {
        "id": 1,
        "telegram_user_id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "language_code": "ru",
        "role": "user",
        "is_blocked": False,
        "full_name": "Test User",
        "is_admin": False
    }


# ===== MODELS ENDPOINTS =====

@app.get("/api/v1/models")
async def get_models():
    """Получить список моделей"""
    if HAS_DATABASE and engine is not None:
        try:
            # Здесь будет код для получения моделей из базы данных
            # Пока возвращаем mock данные
            pass
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock данные
    return {
        "models": [
            {
                "id": 1,
                "name": "Test Model 1",
                "description": "Test model for demo purposes",
                "category": "test",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "name": "Test Model 2",
                "description": "Another test model",
                "category": "demo",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
    }


@app.get("/api/v1/models/{model_id}")
async def get_model(model_id: int):
    """Получить модель по ID"""
    if HAS_DATABASE and engine is not None:
        try:
            # Здесь будет код для получения модели из базы данных
            pass
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock данные
    return {
        "id": model_id,
        "name": f"Test Model {model_id}",
        "description": f"Test model {model_id} for demo purposes",
        "category": "test",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "files": [
            {
                "id": 1,
                "name": "instruction.pdf",
                "type": "pdf",
                "size": 1024000,
                "url": "/api/v1/files/1/download"
            }
        ]
    }


# ===== FILES ENDPOINTS =====

@app.get("/api/v1/files")
async def get_files():
    """Получить список файлов"""
    if HAS_DATABASE and engine is not None:
        try:
            # Здесь будет код для получения файлов из базы данных
            pass
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock данные
    return {
        "files": [
            {
                "id": 1,
                "name": "instruction.pdf",
                "type": "pdf",
                "size": 1024000,
                "model_id": 1,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }


@app.get("/api/v1/files/{file_id}/download")
async def download_file(file_id: int):
    """Скачать файл"""
    return {
        "message": f"File {file_id} download would be available here",
        "file_id": file_id,
        "download_url": f"/api/v1/files/{file_id}/download"
    }


# ===== TICKETS ENDPOINTS =====

@app.get("/api/v1/tickets")
async def get_tickets():
    """Получить список тикетов"""
    if HAS_DATABASE and engine is not None:
        try:
            # Здесь будет код для получения тикетов из базы данных
            pass
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock данные
    return {
        "tickets": [
            {
                "id": 1,
                "subject": "Test Ticket",
                "description": "This is a test ticket",
                "status": "open",
                "priority": "normal",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
    }


@app.post("/api/v1/tickets")
async def create_ticket():
    """Создать новый тикет"""
    if HAS_DATABASE and engine is not None:
        try:
            # Здесь будет код для создания тикета в базе данных
            pass
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock данные
    return {
        "id": 2,
        "subject": "New Test Ticket",
        "description": "This is a new test ticket",
        "status": "open",
        "priority": "normal",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@app.get("/api/v1/tickets/{ticket_id}")
async def get_ticket(ticket_id: int):
    """Получить тикет по ID"""
    if HAS_DATABASE and engine is not None:
        try:
            # Здесь будет код для получения тикета из базы данных
            pass
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock данные
    return {
        "id": ticket_id,
        "subject": f"Test Ticket {ticket_id}",
        "description": f"This is test ticket {ticket_id}",
        "status": "open",
        "priority": "normal",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "messages": [
            {
                "id": 1,
                "body": "Initial message",
                "author_id": 1,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }


# ===== ADMIN ENDPOINTS =====

@app.get("/api/v1/admin/stats")
async def get_admin_stats():
    """Получить статистику для админа"""
    if HAS_DATABASE and engine is not None:
        try:
            # Здесь будет код для получения статистики из базы данных
            pass
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock данные
    return {
        "total_models": 2,
        "total_files": 1,
        "total_tickets": 1,
        "open_tickets": 1,
        "total_users": 1
    }


@app.get("/api/v1/admin/users")
async def get_admin_users():
    """Получить список пользователей для админа"""
    if HAS_DATABASE and engine is not None:
        try:
            # Здесь будет код для получения пользователей из базы данных
            pass
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock данные
    return {
        "users": [
            {
                "id": 1,
                "username": "test_user",
                "first_name": "Test",
                "last_name": "User",
                "role": "user",
                "is_blocked": False,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_with_db:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
