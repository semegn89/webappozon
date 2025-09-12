"""
Схемы пользователей
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: str = "ru"
    role: UserRole = UserRole.USER
    is_blocked: bool = False


class UserCreate(UserBase):
    """Схема создания пользователя"""
    telegram_user_id: int


class UserUpdate(BaseModel):
    """Схема обновления пользователя"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    role: Optional[UserRole] = None
    is_blocked: Optional[bool] = None


class UserInDB(UserBase):
    """Схема пользователя в БД"""
    id: int
    telegram_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    """Публичная схема пользователя"""
    full_name: str

    class Config:
        from_attributes = True


class UserList(BaseModel):
    """Схема списка пользователей"""
    items: List[User]
    total: int
    page: int
    page_size: int
    pages: int
