"""
Гибридная версия FastAPI - полные эндпоинты без базы данных
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from contextlib import asynccontextmanager

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("🚀 Starting Telegram Mini App Backend - Hybrid Version...")
    print("⚠️ Running without database - using mock data")
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
        "message": "Telegram Mini App API - Hybrid Version",
        "version": "1.0.0",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "true")
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }


@app.get("/test")
async def test_endpoint():
    """Тестовый эндпоинт для проверки работы"""
    return {
        "message": "API is working!",
        "cors_origins": ["*"],
        "has_database": False
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
        "main_hybrid:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
