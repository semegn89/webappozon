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

@app.post("/api/v1/models")
async def create_model(model_data: dict):
    """Создать новую модель"""
    return {
        "id": 2,
        "name": model_data.get("name", "New Model"),
        "description": model_data.get("description", ""),
        "category": model_data.get("category", "general"),
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.get("/api/v1/models/{model_id}")
async def get_model(model_id: int):
    """Получить модель по ID"""
    return {
        "id": model_id,
        "name": f"Model {model_id}",
        "description": f"Description for model {model_id}",
        "category": "test",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "files": []
    }

@app.put("/api/v1/models/{model_id}")
async def update_model(model_id: int, model_data: dict):
    """Обновить модель"""
    return {
        "id": model_id,
        "name": model_data.get("name", f"Updated Model {model_id}"),
        "description": model_data.get("description", ""),
        "category": model_data.get("category", "general"),
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.delete("/api/v1/models/{model_id}")
async def delete_model(model_id: int):
    """Удалить модель"""
    return {"message": "Model deleted successfully"}

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
async def create_ticket(ticket_data: dict):
    """Создать новый тикет"""
    return {
        "id": 2,
        "subject": ticket_data.get("subject", "New Ticket"),
        "description": ticket_data.get("description", ""),
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
        "subject": f"Ticket {ticket_id}",
        "description": f"Description for ticket {ticket_id}",
        "status": "open",
        "priority": "normal",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.get("/api/v1/tickets/{ticket_id}/messages")
async def get_ticket_messages(ticket_id: int):
    """Получить сообщения тикета"""
    return [
        {
            "id": 1,
            "ticket_id": ticket_id,
            "user_id": 1,
            "message": "Test message",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]

@app.post("/api/v1/tickets/{ticket_id}/messages")
async def create_ticket_message(ticket_id: int, message_data: dict):
    """Создать сообщение в тикете"""
    return {
        "id": 2,
        "ticket_id": ticket_id,
        "user_id": message_data.get("user_id", 1),
        "message": message_data.get("body", message_data.get("message", "")),
        "created_at": "2024-01-01T00:00:00Z"
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

# ===== FILE ENDPOINTS =====

@app.get("/api/v1/models/{model_id}/files")
async def get_model_files(model_id: int):
    """Получить список файлов модели"""
    return [
        {
            "id": 1,
            "filename": "test.pdf",
            "filepath": "/uploads/test.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf",
            "comment": "",
            "created_at": "2024-01-01T00:00:00Z",
            "url": "https://api.gakshop.com/uploads/test.pdf"
        }
    ]

@app.post("/api/v1/models/{model_id}/files")
async def upload_model_file(model_id: int, file_data: dict):
    """Загрузить файл для модели"""
    return {
        "id": 2,
        "filename": "uploaded.pdf",
        "filepath": "/uploads/uploaded.pdf",
        "file_size": 2048,
        "mime_type": "application/pdf",
        "comment": "",
        "created_at": "2024-01-01T00:00:00Z",
        "url": "https://api.gakshop.com/uploads/uploaded.pdf"
    }

@app.delete("/api/v1/models/{model_id}/files/{file_id}")
async def delete_model_file(model_id: int, file_id: int):
    """Удалить файл модели"""
    return {"message": "File deleted successfully"}

@app.get("/api/v1/files/{file_id}/download")
async def download_file(file_id: int):
    """Скачать файл по ID"""
    return {
        "id": file_id,
        "filename": "test.pdf",
        "url": "https://api.gakshop.com/uploads/test.pdf",
        "mime_type": "application/pdf"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)