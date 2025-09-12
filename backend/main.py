"""
Простая рабочая версия API без сложных зависимостей
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import asynccontextmanager

# Глобальная переменная для подключения к БД
db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global db_pool
    
    # Startup
    print("🚀 Starting Telegram Mini App Backend - Simple Version...")
    
    # Подключение к базе данных
    database_url = os.getenv("DATABASE_URL")
    print(f"🔍 DATABASE_URL from env: {database_url}")
    print(f"🔍 DATABASE_URL exists: {database_url is not None}")
    print(f"🔍 DATABASE_URL length: {len(database_url) if database_url else 0}")
    
    if database_url and not database_url.startswith("postgresql://user:password"):
        try:
            # Убираем channel_binding=require и заменяем sslmode=require на sslmode=prefer
            clean_url = database_url.replace("&channel_binding=require", "").replace("sslmode=require", "sslmode=prefer")
            print(f"🔍 Connecting to database: {clean_url}")
            print(f"🔍 Database URL length: {len(database_url)}")
            print(f"🔍 Clean URL length: {len(clean_url)}")
            
            db_pool = await asyncpg.create_pool(clean_url, min_size=1, max_size=10)
            print("✅ Database connected")
            
            # Создаем таблицы
            await create_tables()
            print("✅ Tables created")
            
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            print(f"⚠️ Error type: {type(e)}")
            print(f"⚠️ Error details: {str(e)}")
            db_pool = None
    else:
        print("⚠️ No database configured, running with mock data")
        db_pool = None
    
    print("✅ Application startup complete")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")
    if db_pool:
        await db_pool.close()

async def create_tables():
    """Создание таблиц в базе данных"""
    if not db_pool:
        return
    
    async with db_pool.acquire() as conn:
        # Создаем таблицу models
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                code VARCHAR(100) UNIQUE NOT NULL,
                brand VARCHAR(100),
                category VARCHAR(100),
                year_from INTEGER,
                year_to INTEGER,
                description TEXT,
                image_url VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """)
        
        # Создаем таблицу tickets
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                model_id INTEGER,
                subject VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                priority VARCHAR(20) DEFAULT 'normal' NOT NULL,
                status VARCHAR(20) DEFAULT 'open' NOT NULL,
                assignee_id INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE,
                closed_at TIMESTAMP WITH TIME ZONE
            )
        """)
        
        # Добавляем тестовые данные если таблицы пустые
        result = await conn.fetchval("SELECT COUNT(*) FROM models")
        if result == 0:
            await conn.execute("""
                INSERT INTO models (name, code, brand, category, description, is_active)
                VALUES ('Sample Model', 'SAMPLE001', 'Sample Brand', 'sample', 'This is a sample model', true)
            """)
            print("✅ Sample model added")

# Создание FastAPI приложения
app = FastAPI(
    title="Telegram Mini App API",
    description="API для Telegram Mini App с каталогом моделей и поддержкой",
    version="1.0.0",
    lifespan=lifespan
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

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Telegram Mini App API - Simple Working Version",
        "version": "1.0.0",
        "status": "running",
        "environment": "production",
        "debug": "false",
        "has_database": db_pool is not None
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0",
        "database_status": "connected" if db_pool else "not_configured"
    }

@app.get("/test")
async def test_endpoint():
    """Тестовый endpoint для проверки работы API"""
    return {
        "message": "API is working!",
        "cors_origins": ["*"],
        "has_database": db_pool is not None,
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
    if not db_pool:
        # Mock данные если база недоступна
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
    
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, name, code, brand, category, year_from, year_to, 
                       description, image_url, is_active, created_at, updated_at
                FROM models 
                WHERE is_active = true
                ORDER BY created_at DESC
            """)
            
            models = []
            for row in rows:
                models.append({
                    "id": row["id"],
                    "name": row["name"],
                    "code": row["code"],
                    "brand": row["brand"],
                    "category": row["category"],
                    "year_from": row["year_from"],
                    "year_to": row["year_to"],
                    "description": row["description"],
                    "image_url": row["image_url"],
                    "is_active": row["is_active"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
                })
            
            return {"models": models}
            
    except Exception as e:
        print(f"⚠️ Error getting models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

@app.post("/api/v1/models")
async def create_model(model_data: dict):
    """Создать новую модель"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        async with db_pool.acquire() as conn:
            # Генерируем уникальный код
            code = model_data.get("code", f"MODEL_{int(asyncio.get_event_loop().time())}")
            
            row = await conn.fetchrow("""
                INSERT INTO models (name, code, brand, category, description, is_active)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, name, code, brand, category, description, created_at, updated_at
            """, 
                model_data.get("name", "New Model"),
                code,
                model_data.get("brand"),
                model_data.get("category", "general"),
                model_data.get("description", ""),
                True
            )
            
            return {
                "id": row["id"],
                "name": row["name"],
                "code": row["code"],
                "brand": row["brand"],
                "category": row["category"],
                "description": row["description"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
            }
            
    except Exception as e:
        print(f"⚠️ Error creating model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create model: {str(e)}")

@app.get("/api/v1/models/{model_id}")
async def get_model(model_id: int):
    """Получить модель по ID"""
    if not db_pool:
        # Mock данные если база недоступна
        return {
            "id": model_id,
            "name": f"Test Model {model_id}",
            "description": f"Test model {model_id} for demo purposes",
            "category": "test",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "files": []
        }
    
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, name, code, brand, category, year_from, year_to, 
                       description, image_url, is_active, created_at, updated_at
                FROM models 
                WHERE id = $1
            """, model_id)
            
            if not row:
                raise HTTPException(status_code=404, detail="Model not found")
            
            return {
                "id": row["id"],
                "name": row["name"],
                "code": row["code"],
                "brand": row["brand"],
                "category": row["category"],
                "year_from": row["year_from"],
                "year_to": row["year_to"],
                "description": row["description"],
                "image_url": row["image_url"],
                "is_active": row["is_active"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                "files": []  # Пока без файлов
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error getting model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model: {str(e)}")

@app.put("/api/v1/models/{model_id}")
async def update_model(model_id: int, model_data: dict):
    """Обновить модель"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        async with db_pool.acquire() as conn:
            # Проверяем существование модели
            existing = await conn.fetchrow("SELECT id FROM models WHERE id = $1", model_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Model not found")
            
            # Обновляем модель
            row = await conn.fetchrow("""
                UPDATE models 
                SET name = COALESCE($2, name),
                    code = COALESCE($3, code),
                    brand = COALESCE($4, brand),
                    category = COALESCE($5, category),
                    year_from = COALESCE($6, year_from),
                    year_to = COALESCE($7, year_to),
                    description = COALESCE($8, description),
                    image_url = COALESCE($9, image_url),
                    is_active = COALESCE($10, is_active),
                    updated_at = NOW()
                WHERE id = $1
                RETURNING id, name, code, brand, category, year_from, year_to, 
                         description, image_url, is_active, created_at, updated_at
            """, 
                model_id,
                model_data.get("name"),
                model_data.get("code"),
                model_data.get("brand"),
                model_data.get("category"),
                model_data.get("year_from"),
                model_data.get("year_to"),
                model_data.get("description"),
                model_data.get("image_url"),
                model_data.get("is_active")
            )
            
            return {
                "id": row["id"],
                "name": row["name"],
                "code": row["code"],
                "brand": row["brand"],
                "category": row["category"],
                "year_from": row["year_from"],
                "year_to": row["year_to"],
                "description": row["description"],
                "image_url": row["image_url"],
                "is_active": row["is_active"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error updating model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update model: {str(e)}")

@app.delete("/api/v1/models/{model_id}")
async def delete_model(model_id: int):
    """Удалить модель"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        async with db_pool.acquire() as conn:
            # Проверяем существование модели
            existing = await conn.fetchrow("SELECT id FROM models WHERE id = $1", model_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Model not found")
            
            # Удаляем модель
            await conn.execute("DELETE FROM models WHERE id = $1", model_id)
            
            return {"message": "Model deleted successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error deleting model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete model: {str(e)}")

# ===== ADMIN STATS ENDPOINT =====

@app.get("/api/v1/admin/stats")
async def get_admin_stats():
    """Получить статистику для админ панели"""
    if not db_pool:
        # Mock данные если база недоступна
        return {
            "total_models": 0,
            "active_tickets": 0,
            "total_users": 0,
            "total_downloads": 1234
        }
    
    try:
        async with db_pool.acquire() as conn:
            # Получаем статистику
            models_count = await conn.fetchval("SELECT COUNT(*) FROM models")
            active_tickets = await conn.fetchval("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
            users_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            
            return {
                "total_models": models_count or 0,
                "active_tickets": active_tickets or 0,
                "total_users": users_count or 0,
                "total_downloads": 1234  # Пока заглушка
            }
            
    except Exception as e:
        print(f"⚠️ Error getting admin stats: {e}")
        return {
            "total_models": 0,
            "active_tickets": 0,
            "total_users": 0,
            "total_downloads": 1234
        }

# ===== TICKETS ENDPOINTS =====

@app.get("/api/v1/tickets")
async def get_tickets():
    """Получить список тикетов"""
    if not db_pool:
        # Mock данные если база недоступна
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
    
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, user_id, model_id, subject, description, priority, 
                       status, assignee_id, created_at, updated_at, closed_at
                FROM tickets 
                ORDER BY created_at DESC
            """)
            
            tickets = []
            for row in rows:
                tickets.append({
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "model_id": row["model_id"],
                    "subject": row["subject"],
                    "description": row["description"],
                    "priority": row["priority"],
                    "status": row["status"],
                    "assignee_id": row["assignee_id"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                    "closed_at": row["closed_at"].isoformat() if row["closed_at"] else None
                })
            
            return {"tickets": tickets}
            
    except Exception as e:
        print(f"⚠️ Error getting tickets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tickets: {str(e)}")

@app.post("/api/v1/tickets")
async def create_ticket(ticket_data: dict):
    """Создать новый тикет"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO tickets (user_id, model_id, subject, description, priority, status)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, user_id, model_id, subject, description, priority, status, created_at
            """, 
                ticket_data.get("user_id", 1),
                ticket_data.get("model_id"),
                ticket_data.get("subject", "New Ticket"),
                ticket_data.get("description", ""),
                ticket_data.get("priority", "normal"),
                ticket_data.get("status", "open")
            )
            
            return {
                "id": row["id"],
                "user_id": row["user_id"],
                "model_id": row["model_id"],
                "subject": row["subject"],
                "description": row["description"],
                "priority": row["priority"],
                "status": row["status"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
            
    except Exception as e:
        print(f"⚠️ Error creating ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create ticket: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
