"""
Схемы моделей
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ModelBase(BaseModel):
    """Базовая схема модели"""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    year_from: Optional[int] = Field(None, ge=1900, le=2100)
    year_to: Optional[int] = Field(None, ge=1900, le=2100)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class ModelCreate(ModelBase):
    """Схема создания модели"""
    pass


class ModelUpdate(BaseModel):
    """Схема обновления модели"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    year_from: Optional[int] = Field(None, ge=1900, le=2100)
    year_to: Optional[int] = Field(None, ge=1900, le=2100)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class ModelInDB(ModelBase):
    """Схема модели в БД"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Model(ModelInDB):
    """Публичная схема модели"""
    year_range: str
    has_files: bool

    class Config:
        from_attributes = True


class ModelWithFiles(Model):
    """Схема модели с файлами"""
    files: List["File"] = []

    class Config:
        from_attributes = True


class ModelList(BaseModel):
    """Схема списка моделей"""
    items: List[Model]
    total: int
    page: int
    page_size: int
    pages: int


class ModelFilters(BaseModel):
    """Фильтры для поиска моделей"""
    q: Optional[str] = None  # Поисковый запрос
    brand: Optional[str] = None
    category: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    has_files: Optional[bool] = None
    is_active: Optional[bool] = True
