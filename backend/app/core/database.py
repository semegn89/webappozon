"""
Настройка базы данных
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from fastapi import HTTPException
from app.core.config import settings


# Создание асинхронного движка БД
engine = None
AsyncSessionLocal = None

if settings.DATABASE_URL and settings.DATABASE_URL != "postgresql://user:password@localhost:5432/telegram_mini_app":
    try:
        print(f"🔍 Creating database engine with URL: {settings.DATABASE_URL}")
        async_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        print(f"🔍 Async URL: {async_url}")
        
        engine = create_async_engine(
            async_url,
            echo=settings.DEBUG,
            future=True
        )
        
        # Создание фабрики сессий
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        print("✅ Database engine created successfully")
    except Exception as e:
        print(f"⚠️ Failed to create database engine: {e}")
        print(f"⚠️ Error type: {type(e)}")
        import traceback
        print(f"⚠️ Traceback: {traceback.format_exc()}")
        engine = None
        AsyncSessionLocal = None
else:
    print(f"⚠️ DATABASE_URL not configured or is default: {settings.DATABASE_URL}")


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


async def get_db() -> AsyncSession:
    """Dependency для получения сессии БД"""
    if AsyncSessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Database not available"
        )
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
