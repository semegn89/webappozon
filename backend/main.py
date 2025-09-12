"""
Простая версия FastAPI для тестирования
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Создание FastAPI приложения
app = FastAPI(
    title="Telegram Mini App API - Simple",
    description="Простая версия API для тестирования",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Временно разрешаем все домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Telegram Mini App API - Simple Version",
        "version": "1.0.0",
        "status": "running"
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
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "true")
    }

# Базовые эндпоинты для фронтенда
@app.post("/api/v1/auth/verify")
async def verify_auth():
    """Простая проверка аутентификации"""
    return {
        "success": True,
        "message": "Authentication successful",
        "user": {
            "id": 1,
            "username": "test_user",
            "role": "user"
        }
    }

@app.get("/api/v1/models")
async def get_models():
    """Получить список моделей"""
    return {
        "models": [
            {
                "id": 1,
                "name": "Test Model",
                "description": "Test model for demo",
                "category": "test"
            }
        ]
    }

@app.get("/api/v1/tickets")
async def get_tickets():
    """Получить список тикетов"""
    return {
        "tickets": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
