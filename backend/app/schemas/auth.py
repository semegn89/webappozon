"""
Схемы аутентификации
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TelegramAuth(BaseModel):
    """Схема данных аутентификации Telegram"""
    init_data: str = Field(..., description="Telegram WebApp initData")


class Token(BaseModel):
    """Схема токена"""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class TokenData(BaseModel):
    """Данные токена"""
    user_id: Optional[int] = None
    telegram_user_id: Optional[int] = None
    role: Optional[str] = None


class AuthResponse(BaseModel):
    """Ответ аутентификации"""
    token: Token
    user: "User"
    is_admin: bool
