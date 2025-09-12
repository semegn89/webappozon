"""
Конфигурация приложения
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    PROJECT_NAME: str = "Telegram Mini App"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # База данных
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/telegram_mini_app"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_WEBAPP_URL: str = ""
    TELEGRAM_BOT_USERNAME: str = ""
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Админы
    ADMIN_USER_IDS: str = ""  # comma-separated
    
    # Файловое хранилище
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET_NAME: str = "telegram-mini-app-files"
    S3_REGION: str = "us-east-1"
    
    # Локальное хранилище файлов
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 104857600  # 100MB
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # seconds
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://yourdomain.com"]
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    @property
    def admin_user_ids_list(self) -> List[int]:
        """Список ID админов"""
        if not self.ADMIN_USER_IDS:
            return []
        return [int(uid.strip()) for uid in self.ADMIN_USER_IDS.split(",") if uid.strip()]
    
    @property
    def use_s3_storage(self) -> bool:
        """Использовать S3 хранилище"""
        return all([
            self.S3_ENDPOINT_URL,
            self.S3_ACCESS_KEY_ID,
            self.S3_SECRET_ACCESS_KEY
        ])
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Глобальный экземпляр настроек
settings = Settings()
