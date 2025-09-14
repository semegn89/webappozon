"""
Простая рабочая версия API без сложных зависимостей
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

# Создаем приложение
app = FastAPI(
    title="Telegram Mini App API",
    description="API для Telegram Mini App с каталогом моделей и поддержкой",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== BASIC ENDPOINTS =====

@app.options("/{path:path}")
async def options_handler(path: str):
    """Обработчик OPTIONS запросов для CORS"""
    return {"message": "OK"}

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Telegram Mini App API - Simple Working Version",
        "version": "1.0.0",
        "status": "running",
        "environment": "production",
        "debug": "false"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

@app.get("/test")
async def test_endpoint():
    """Тестовый endpoint для проверки работы API"""
    return {
        "message": "API is working!",
        "cors_origins": ["*"],
        "has_database": False,
        "database_url_configured": bool(os.getenv("DATABASE_URL")),
        "database_url_from_env": os.getenv("DATABASE_URL", "NOT_SET")[:50] + "..." if os.getenv("DATABASE_URL") else "NOT_SET"
    }

# ===== AUTH ENDPOINTS =====

@app.get("/api/v1/auth/me")
async def get_current_user():
    """Получить текущего пользователя"""
    return {
        "id": 1,
        "telegram_user_id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
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
            }
        ]
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

# ===== ADMIN ENDPOINTS =====

@app.get("/api/v1/admin/stats")
async def get_admin_stats():
    """Получить статистику для админ панели"""
    return {
        "total_models": 1,
        "total_tickets": 1,
        "open_tickets": 1,
        "total_users": 1,
        "total_downloads": 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)