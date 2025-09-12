"""
Схемы файлов
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.file import FileType


class FileBase(BaseModel):
    """Базовая схема файла"""
    title: str = Field(..., min_length=1, max_length=255)
    file_type: FileType
    is_public: bool = True
    version: Optional[str] = Field(None, max_length=50)
    tags: Optional[Dict[str, Any]] = None


class FileCreate(FileBase):
    """Схема создания файла"""
    model_id: int
    storage_key: str
    size_bytes: int


class FileUpdate(BaseModel):
    """Схема обновления файла"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    is_public: Optional[bool] = None
    version: Optional[str] = Field(None, max_length=50)
    tags: Optional[Dict[str, Any]] = None


class FileInDB(FileBase):
    """Схема файла в БД"""
    id: int
    model_id: int
    storage_key: str
    size_bytes: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class File(FileInDB):
    """Публичная схема файла"""
    size_mb: float
    is_image: bool
    is_document: bool
    is_archive: bool

    class Config:
        from_attributes = True


class FileWithModel(File):
    """Схема файла с моделью"""
    model: "Model"

    class Config:
        from_attributes = True


class FileList(BaseModel):
    """Схема списка файлов"""
    items: List[File]
    total: int
    page: int
    page_size: int
    pages: int


class FileDownload(BaseModel):
    """Схема для скачивания файла"""
    download_url: str
    expires_at: datetime
    filename: str
    size_bytes: int


class FileUpload(BaseModel):
    """Схема загрузки файла"""
    filename: str
    content_type: str
    size_bytes: int
