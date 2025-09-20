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

# CORS middleware - более агрессивные настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gakshop.com",
        "https://www.gakshop.com", 
        "https://api.gakshop.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "https://localhost:3000",
        "https://localhost:5173",
        "*"  # Временно разрешаем все домены для отладки
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# ===== BASIC ENDPOINTS =====

@app.options("/{path:path}")
async def options_handler(path: str):
    """Обработчик OPTIONS запросов для CORS"""
    from fastapi import Response
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "600"
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

# Глобальное хранилище данных (постоянное решение)
models_storage = [
    {
        "id": 1,
        "name": "Test Model 1",
        "description": "Test model for demo purposes",
        "category": "test",
        "brand": "Test Brand",
        "code": "TM001",
        "image_url": "https://example.com/image1.jpg",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": 2,
        "name": "Test Model 2",
        "description": "Another test model",
        "category": "demo",
        "brand": "Demo Brand",
        "code": "TM002",
        "image_url": "https://example.com/image2.jpg",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": 3,
        "name": "Test Model 3",
        "description": "Third test model",
        "category": "example",
        "brand": "Example Brand",
        "code": "TM003",
        "image_url": "https://example.com/image3.jpg",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]

# Хранилище файлов моделей
model_files_storage = [
    {
        "id": 1,
        "model_id": 1,
        "filename": "test.pdf",
        "filepath": "/uploads/test.pdf",
        "file_size": 1024,
        "mime_type": "application/pdf",
        "comment": "Test file",
        "created_at": "2024-01-01T00:00:00Z",
        "url": "https://api.gakshop.com/uploads/test.pdf"
    },
    {
        "id": 2,
        "model_id": 3,
        "filename": "model3_manual.pdf",
        "filepath": "/uploads/model3_manual.pdf",
        "file_size": 2048,
        "mime_type": "application/pdf",
        "comment": "Manual for model 3",
        "created_at": "2024-01-01T00:00:00Z",
        "url": "https://api.gakshop.com/uploads/model3_manual.pdf"
    }
]

# Хранилище тикетов
tickets_storage = [
    {
        "id": 1,
        "subject": "Test Ticket",
        "description": "Test ticket description",
        "status": "open",
        "priority": "normal",
        "user_id": 1,
        "model_id": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "closed_at": None
    }
]

# Хранилище сообщений тикетов
ticket_messages_storage = [
    {
        "id": 1,
        "ticket_id": 1,
        "user_id": 1,
        "message": "Initial ticket message",
        "created_at": "2024-01-01T00:00:00Z"
    }
]

@app.get("/api/v1/models")
async def get_models():
    """Получить список моделей"""
    print(f"[API] Getting models, count: {len(models_storage)}")
    return {
        "models": models_storage
    }

@app.post("/api/v1/models")
async def create_model(model_data: dict):
    """Создать новую модель"""
    import time
    
    # Генерируем новый ID
    new_id = max([m["id"] for m in models_storage], default=0) + 1
    
    # Создаем новую модель
    new_model = {
        "id": new_id,
        "name": model_data.get("name", "New Model"),
        "description": model_data.get("description", ""),
        "category": model_data.get("category", "general"),
        "brand": model_data.get("brand", ""),
        "code": model_data.get("code", ""),
        "image_url": model_data.get("image_url", ""),
        "is_active": model_data.get("is_active", True),
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    
    # Добавляем в хранилище
    models_storage.append(new_model)
    
    print(f"[API] Created model: {new_model}")
    
    return new_model

@app.get("/api/v1/models/{model_id}")
async def get_model(model_id: int):
    """Получить модель по ID"""
    print(f"[API] Getting model {model_id}")
    # Ищем модель в хранилище
    for model in models_storage:
        if model["id"] == model_id:
            print(f"[API] Found model: {model['name']}")
            return model
    
    # Если не найдена, возвращаем ошибку
    print(f"[API] Model {model_id} not found")
    raise HTTPException(status_code=404, detail="Model not found")

@app.put("/api/v1/models/{model_id}")
async def update_model(model_id: int, model_data: dict):
    """Обновить модель"""
    # Ищем модель в хранилище
    for i, model in enumerate(models_storage):
        if model["id"] == model_id:
            # Обновляем модель
            updated_model = {
                **model,
                "name": model_data.get("name", model["name"]),
                "description": model_data.get("description", model["description"]),
                "category": model_data.get("category", model["category"]),
                "brand": model_data.get("brand", model.get("brand", "")),
                "code": model_data.get("code", model.get("code", "")),
                "image_url": model_data.get("image_url", model.get("image_url", "")),
                "is_active": model_data.get("is_active", model.get("is_active", True)),
                "updated_at": "2024-01-01T00:00:00Z"
            }
            models_storage[i] = updated_model
            
            print(f"[API] Updated model: {updated_model}")
            return updated_model
    
    # Если не найдена, возвращаем ошибку
    raise HTTPException(status_code=404, detail="Model not found")

@app.delete("/api/v1/models/{model_id}")
async def delete_model(model_id: int):
    """Удалить модель"""
    # Ищем модель в хранилище
    for i, model in enumerate(models_storage):
        if model["id"] == model_id:
            # Удаляем модель
            deleted_model = models_storage.pop(i)
            print(f"[API] Deleted model: {deleted_model}")
            return {"message": "Model deleted successfully"}
    
    # Если не найдена, возвращаем ошибку
    raise HTTPException(status_code=404, detail="Model not found")

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
    print(f"[API] Getting messages for ticket {ticket_id}")
    # Фильтруем сообщения по ticket_id
    messages = [m for m in ticket_messages_storage if m["ticket_id"] == ticket_id]
    print(f"[API] Found {len(messages)} messages for ticket {ticket_id}")
    return messages

@app.post("/api/v1/tickets/{ticket_id}/messages")
async def create_ticket_message(ticket_id: int, message_data: dict):
    """Создать сообщение в тикете"""
    import time
    
    # Генерируем новый ID для сообщения
    new_message_id = max([m["id"] for m in ticket_messages_storage], default=0) + 1
    
    # Создаем новое сообщение
    new_message = {
        "id": new_message_id,
        "ticket_id": ticket_id,
        "user_id": message_data.get("user_id", 1),
        "message": message_data.get("body", message_data.get("message", "")),
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    # Добавляем в хранилище
    ticket_messages_storage.append(new_message)
    
    print(f"[API] Created message: {new_message}")
    return new_message

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
    try:
        print(f"[API] Getting files for model {model_id}")
        # Фильтруем файлы по model_id
        model_files = [f for f in model_files_storage if f["model_id"] == model_id]
        print(f"[API] Found {len(model_files)} files for model {model_id}")
        return model_files
    except Exception as e:
        print(f"[API] Error getting files for model {model_id}: {e}")
        return []

@app.post("/api/v1/models/{model_id}/files")
async def upload_model_file(model_id: int, file_data: dict):
    """Загрузить файл для модели"""
    import time
    
    # Генерируем новый ID для файла
    new_file_id = max([f["id"] for f in model_files_storage], default=0) + 1
    
    # Создаем новый файл
    new_file = {
        "id": new_file_id,
        "model_id": model_id,
        "filename": file_data.get("filename", "uploaded_file.pdf"),
        "filepath": f"/uploads/model_{model_id}/file_{new_file_id}.pdf",
        "file_size": file_data.get("file_size", 2048),
        "mime_type": file_data.get("mime_type", "application/pdf"),
        "comment": file_data.get("comment", ""),
        "created_at": "2024-01-01T00:00:00Z",
        "url": f"https://api.gakshop.com/uploads/model_{model_id}/file_{new_file_id}.pdf"
    }
    
    # Добавляем в хранилище
    model_files_storage.append(new_file)
    
    print(f"[API] Uploaded file: {new_file}")
    return new_file

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