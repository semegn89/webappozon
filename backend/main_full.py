"""
Telegram Mini App Backend
FastAPI приложение для каталога моделей, инструкций и поддержки
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.core.exceptions import setup_exception_handlers


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("🚀 Starting Telegram Mini App Backend...")
    
    # Создание таблиц БД только если есть DATABASE_URL
    if engine is not None:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created")
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            print("🔄 Running without database...")
    else:
        print("⚠️ No database configured, running in API-only mode")
    
    print("✅ Application startup complete")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")


# Создание FastAPI приложения
app = FastAPI(
    title="Telegram Mini App API",
    description="API для каталога моделей, инструкций и поддержки",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["gakshop.com", "*.gakshop.com", "*.vercel.app"]
    )

# Статические файлы
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключение роутеров (только если база данных доступна)
if engine is not None:
    app.include_router(api_router, prefix="/api/v1")
else:
    print("⚠️ API routes disabled - no database connection")

# Обработчики исключений
setup_exception_handlers(app)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Telegram Mini App API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
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
        "cors_origins": settings.CORS_ORIGINS,
        "has_database": bool(settings.DATABASE_URL and not settings.DATABASE_URL.startswith("postgresql://user:password"))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
