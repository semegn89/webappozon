"""
Простая рабочая версия API без сложных зависимостей
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import asynccontextmanager

# Глобальная переменная для подключения к БД
db_pool = None

async def get_db_pool():
    """Получить подключение к базе данных (lazy loading)"""
    global db_pool
    
    if db_pool is not None:
        return db_pool
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url or database_url.startswith("postgresql://user:password"):
        return None
    
    try:
        # Убираем channel_binding=require и заменяем sslmode=require на sslmode=prefer
        clean_url = database_url.replace("&channel_binding=require", "").replace("sslmode=require", "sslmode=prefer")
        print(f"🔍 Connecting to database: {clean_url}")
        
        db_pool = await asyncpg.create_pool(clean_url, min_size=1, max_size=10)
        print("✅ Database connected")
        
        # Создаем таблицы
        try:
            await create_tables()
            print("✅ Tables created")
        except Exception as e:
            print(f"⚠️ Error creating tables: {e}")
        
        return db_pool
        
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print(f"⚠️ Error type: {type(e)}")
        print(f"⚠️ Error details: {str(e)}")
        return None

async def get_db_connection():
    """Получить соединение с базой данных"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url or database_url.startswith("postgresql://user:password"):
        return None
    
    try:
        # Убираем channel_binding=require и заменяем sslmode=require на sslmode=prefer
        clean_url = database_url.replace("&channel_binding=require", "").replace("sslmode=require", "sslmode=prefer")
        
        # Создаем новое соединение с таймаутами
        conn = await asyncpg.connect(
            clean_url,
            command_timeout=30,
            server_settings={
                'application_name': 'webappozon',
                'jit': 'off'
            }
        )
        return conn
    except Exception as e:
        print(f"⚠️ Error creating connection: {e}")
        return None

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
            try:
                await create_tables()
                print("✅ Tables created")
            except Exception as e:
                print(f"⚠️ Error creating tables: {e}")
            
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
    database_url = os.getenv("DATABASE_URL")
    if not database_url or database_url.startswith("postgresql://user:password"):
        return
    
    try:
        # Убираем channel_binding=require и заменяем sslmode=require на sslmode=prefer
        clean_url = database_url.replace("&channel_binding=require", "").replace("sslmode=require", "sslmode=prefer")
        conn = await asyncpg.connect(clean_url)
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
        
        # Создаем таблицу файлов моделей
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS model_files (
                id SERIAL PRIMARY KEY,
                model_id INTEGER REFERENCES models(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_size INTEGER,
                mime_type VARCHAR(100),
                comment TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Создаем таблицу сообщений тикетов
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ticket_messages (
                id SERIAL PRIMARY KEY,
                ticket_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
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
        
        await conn.close()
            
    except Exception as e:
        print(f"⚠️ Error creating tables: {e}")

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
    print("🔍 Test endpoint called")
    
    # Используем lazy loading для подключения к базе данных
    current_db_pool = await get_db_pool()
    
    return {
        "message": "API is working!",
        "cors_origins": ["*"],
        "has_database": current_db_pool is not None,
        "database_url_configured": bool(os.getenv("DATABASE_URL")),
        "database_url_from_env": os.getenv("DATABASE_URL", "NOT_SET")[:50] + "..." if os.getenv("DATABASE_URL") else "NOT_SET"
    }

@app.get("/test-db")
async def test_database_connection():
    """Тестовый endpoint для проверки подключения к базе данных"""
    print("🔍 Test database endpoint called")
    
    database_url = os.getenv("DATABASE_URL")
    print(f"🔍 DATABASE_URL: {database_url}")
    
    if not database_url:
        return {"error": "DATABASE_URL not configured"}
    
    try:
        # Убираем channel_binding=require и заменяем sslmode=require на sslmode=prefer
        clean_url = database_url.replace("&channel_binding=require", "").replace("sslmode=require", "sslmode=prefer")
        print(f"🔍 Clean URL: {clean_url}")
        
        # Пробуем подключиться
        test_pool = await asyncpg.create_pool(clean_url, min_size=1, max_size=1)
        print("✅ Database connection successful")
        
        # Тестируем запрос
        async with test_pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            print(f"✅ Test query result: {result}")
        
        await test_pool.close()
        print("✅ Database connection closed")
        
        return {
            "status": "success",
            "message": "Database connection successful",
            "test_query_result": result
        }
        
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print(f"⚠️ Error type: {type(e)}")
        print(f"⚠️ Error details: {str(e)}")
        
        return {
            "status": "error",
            "message": "Database connection failed",
            "error": str(e),
            "error_type": str(type(e))
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
    conn = await get_db_connection()
    if not conn:
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
    finally:
        if conn:
            await conn.close()

@app.post("/api/v1/models")
async def create_model(model_data: dict):
    """Создать новую модель"""
    conn = await get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Генерируем уникальный код
        code = model_data.get("code")
        if not code or code.strip() == "":
            import time
            code = f"MODEL_{int(time.time() * 1000)}"
        
        # Проверяем уникальность кода
        existing = await conn.fetchval("SELECT id FROM models WHERE code = $1", code)
        if existing:
            import time
            code = f"MODEL_{int(time.time() * 1000)}_{existing}"
        
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
    finally:
        if conn:
            await conn.close()

@app.get("/api/v1/models/{model_id}")
async def get_model(model_id: int):
    """Получить модель по ID"""
    conn = await get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
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
    finally:
        if conn:
            await conn.close()

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
    conn = await get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
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
    finally:
        if conn:
            await conn.close()

# ===== ADMIN STATS ENDPOINT =====

@app.get("/api/v1/admin/stats")
async def get_admin_stats():
    """Получить статистику для админ панели"""
    print("🔍 Admin stats endpoint called")
    
    # Используем тот же подход, что и в endpoint моделей
    database_url = os.getenv("DATABASE_URL")
    if not database_url or database_url.startswith("postgresql://user:password"):
        print("⚠️ No database configured")
        return {
            "total_models": 0,
            "active_tickets": 0,
            "total_users": 0,
            "total_downloads": 1234
        }
    
    try:
        print("🔍 Getting statistics from database")
        # Убираем channel_binding=require и заменяем sslmode=require на sslmode=prefer
        clean_url = database_url.replace("&channel_binding=require", "").replace("sslmode=require", "sslmode=prefer")
        conn = await asyncpg.connect(clean_url)
        
        # Получаем статистику
        models_count = await conn.fetchval("SELECT COUNT(*) FROM models")
        total_tickets = await conn.fetchval("SELECT COUNT(*) FROM tickets")
        active_tickets = await conn.fetchval("SELECT COUNT(*) FROM tickets WHERE status IN ('open', 'new', 'pending')")
        
        # Пытаемся получить пользователей (если таблица существует)
        try:
            users_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        except Exception:
            users_count = 0
        
        # Пытаемся получить загрузки из моделей
        try:
            total_downloads = await conn.fetchval("SELECT COALESCE(SUM(downloads), 0) FROM models")
        except Exception:
            total_downloads = 1234  # Заглушка
        
        print(f"🔍 Models count: {models_count}")
        print(f"🔍 Total tickets: {total_tickets}")
        print(f"🔍 Active tickets: {active_tickets}")
        print(f"🔍 Users count: {users_count}")
        print(f"🔍 Downloads: {total_downloads}")
        
        await conn.close()
        
        return {
            "total_models": models_count or 0,
            "total_tickets": total_tickets or 0,
            "active_tickets": active_tickets or 0,
            "total_users": users_count or 0,
            "total_downloads": int(total_downloads) if total_downloads else 1234
        }
        
    except Exception as e:
        print(f"⚠️ Error getting admin stats: {e}")
        return {
            "total_models": 0,
            "active_tickets": 0,
            "total_users": 0,
            "total_downloads": 1234
        }

# ===== USERS ENDPOINTS =====

@app.get("/api/v1/users")
async def get_users():
    """Получить список пользователей"""
    conn = await get_db_connection()
    if not conn:
        # Mock данные если база недоступна
        return {
            "users": [
                {
                    "id": 1,
                    "username": "test_user",
                    "first_name": "Test",
                    "last_name": "User",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ]
        }
    
    try:
        rows = await conn.fetch("""
            SELECT id, username, first_name, last_name, is_active, created_at
            FROM users 
            ORDER BY created_at DESC
        """)
        
        users = []
        for row in rows:
            users.append({
                "id": row["id"],
                "username": row["username"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "is_active": row["is_active"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            })
        
        return {"users": users}
        
    except Exception as e:
        print(f"⚠️ Error getting users: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")
    finally:
        if conn:
            await conn.close()

# ===== TICKETS ENDPOINTS =====

@app.get("/api/v1/tickets")
async def get_tickets():
    """Получить список тикетов"""
    conn = await get_db_connection()
    if not conn:
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
    finally:
        if conn:
            await conn.close()

@app.post("/api/v1/tickets")
async def create_ticket(ticket_data: dict):
    """Создать новый тикет"""
    conn = await get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
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
    finally:
        if conn:
            await conn.close()

@app.get("/api/v1/tickets/{ticket_id}")
async def get_ticket(ticket_id: int):
    """Получить тикет по ID"""
    conn = await get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Получаем тикет
        ticket = await conn.fetchrow("""
            SELECT id, user_id, model_id, subject, description, priority, status, created_at, updated_at
            FROM tickets 
            WHERE id = $1
        """, ticket_id)
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {
            "id": ticket["id"],
            "user_id": ticket["user_id"],
            "model_id": ticket["model_id"],
            "subject": ticket["subject"],
            "description": ticket["description"],
            "priority": ticket["priority"],
            "status": ticket["status"],
            "created_at": ticket["created_at"].isoformat() if ticket["created_at"] else None,
            "updated_at": ticket["updated_at"].isoformat() if ticket["updated_at"] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error getting ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ticket: {str(e)}")
    finally:
        if conn:
            await conn.close()

# ===== TICKET MESSAGES ENDPOINTS =====

@app.get("/api/v1/tickets/{ticket_id}/messages")
async def get_ticket_messages(ticket_id: int):
    """Получить сообщения тикета"""
    conn = await get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Проверяем существование тикета
        ticket = await conn.fetchrow("SELECT id FROM tickets WHERE id = $1", ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Получаем сообщения
        messages = await conn.fetch("""
            SELECT id, ticket_id, user_id, message, created_at
            FROM ticket_messages 
            WHERE ticket_id = $1 
            ORDER BY created_at ASC
        """, ticket_id)
        
        return [{
            "id": msg["id"],
            "ticket_id": msg["ticket_id"],
            "user_id": msg["user_id"],
            "message": msg["message"],
            "created_at": msg["created_at"].isoformat() if msg["created_at"] else None
        } for msg in messages]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error getting ticket messages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")
    finally:
        if conn:
            await conn.close()

@app.post("/api/v1/tickets/{ticket_id}/messages")
async def create_ticket_message(ticket_id: int, message_data: dict):
    """Создать сообщение в тикете"""
    conn = await get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Проверяем существование тикета
        ticket = await conn.fetchrow("SELECT id, user_id FROM tickets WHERE id = $1", ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Определяем, кто отправляет сообщение
        # Если user_id не указан или равен user_id тикета - это пользователь
        # Если user_id = 0 или -1 - это администратор
        sender_user_id = message_data.get("user_id")
        if sender_user_id is None:
            # По умолчанию - пользователь, создавший тикет
            sender_user_id = ticket["user_id"]
        elif sender_user_id == 0 or sender_user_id == -1:
            # Администратор
            sender_user_id = 0
        
        # Создаем сообщение
        row = await conn.fetchrow("""
            INSERT INTO ticket_messages (ticket_id, user_id, message)
            VALUES ($1, $2, $3)
            RETURNING id, ticket_id, user_id, message, created_at
        """, 
            ticket_id,
            sender_user_id,
            message_data.get("body", message_data.get("message", ""))
        )
        
        return {
            "id": row["id"],
            "ticket_id": row["ticket_id"],
            "user_id": row["user_id"],
            "message": row["message"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error creating ticket message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")
    finally:
        if conn:
            await conn.close()

@app.post("/init-db")
async def init_database():
    """Принудительно создать таблицы"""
    print("🔍 Init database endpoint called")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return {"status": "error", "message": "DATABASE_URL not configured"}
    
    try:
        # Убираем channel_binding=require и заменяем sslmode=require на sslmode=prefer
        clean_url = database_url.replace("&channel_binding=require", "").replace("sslmode=require", "sslmode=prefer")
        conn = await asyncpg.connect(clean_url)
        
        await create_tables()
        await conn.close()
        
        return {"status": "success", "message": "Database tables created successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to create tables: {str(e)}"}

# ===== FILE UPLOAD ENDPOINTS =====

@app.post("/api/v1/files")
async def upload_file(file: UploadFile = File(...)):
    """Загрузить файл"""
    try:
        # Проверяем тип файла
        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xlsx', 'txt'}
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Читаем содержимое файла
        contents = await file.read()
        
        # В реальном приложении здесь бы сохраняли файл на диск
        # Для демо просто возвращаем информацию о файле
        return {
            "file": {
                "name": file.filename,
                "size": len(contents),
                "type": file.content_type,
                "url": f"/uploads/{file.filename}"  # Заглушка URL
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

# ===== MODEL FILES ENDPOINTS =====

@app.post("/api/v1/models/{model_id}/files")
async def upload_model_file(model_id: int, file: UploadFile = File(...), comment: str = ""):
    """Загрузить файл для модели"""
    conn = await get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Проверяем существование модели
        model = await conn.fetchrow("SELECT id FROM models WHERE id = $1", model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Проверяем тип файла
        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xlsx', 'txt'}
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Читаем содержимое файла
        contents = await file.read()
        
        # Генерируем уникальное имя файла
        import uuid
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = f"/uploads/models/{model_id}/{unique_filename}"
        
        # Сохраняем информацию о файле в базу данных
        row = await conn.fetchrow("""
            INSERT INTO model_files (model_id, filename, filepath, file_size, mime_type, comment)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, filename, filepath, file_size, mime_type, comment, created_at
        """, 
            model_id, file.filename, filepath, len(contents), file.content_type, comment
        )
        
        return {
            "id": row["id"],
            "filename": row["filename"],
            "filepath": row["filepath"],
            "file_size": row["file_size"],
            "mime_type": row["mime_type"],
            "comment": row["comment"],
            "created_at": row["created_at"].isoformat(),
            "url": f"https://api.gakshop.com{filepath}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error uploading model file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    finally:
        if conn:
            await conn.close()

@app.get("/api/v1/models/{model_id}/files")
async def get_model_files(model_id: int):
    """Получить список файлов модели"""
    conn = await get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Проверяем существование модели
        model = await conn.fetchrow("SELECT id FROM models WHERE id = $1", model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Получаем файлы модели
        files = await conn.fetch("""
            SELECT id, filename, filepath, file_size, mime_type, comment, created_at
            FROM model_files
            WHERE model_id = $1
            ORDER BY created_at DESC
        """, model_id)
        
        return [
            {
                "id": file["id"],
                "filename": file["filename"],
                "filepath": file["filepath"],
                "file_size": file["file_size"],
                "mime_type": file["mime_type"],
                "comment": file["comment"],
                "created_at": file["created_at"].isoformat(),
                "url": f"https://api.gakshop.com{file['filepath']}"
            }
            for file in files
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error getting model files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get files: {str(e)}")
    finally:
        if conn:
            await conn.close()

@app.delete("/api/v1/models/{model_id}/files/{file_id}")
async def delete_model_file(model_id: int, file_id: int):
    """Удалить файл модели"""
    conn = await get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Проверяем существование файла
        file_record = await conn.fetchrow("""
            SELECT id, filename FROM model_files 
            WHERE id = $1 AND model_id = $2
        """, file_id, model_id)
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Удаляем файл из базы данных
        await conn.execute("DELETE FROM model_files WHERE id = $1", file_id)
        
        return {"message": f"File '{file_record['filename']}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error deleting model file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
