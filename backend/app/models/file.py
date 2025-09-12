"""
Модель файла
"""

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class FileType(str, enum.Enum):
    """Типы файлов"""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    JPG = "jpg"
    PNG = "png"
    ZIP = "zip"
    OTHER = "other"


class File(Base):
    """Модель файла"""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    storage_key = Column(String(500), nullable=False)  # Путь в S3 или локальном хранилище
    size_bytes = Column(BigInteger, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    version = Column(String(50), nullable=True)
    tags = Column(JSON, nullable=True)  # Дополнительные теги
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    model = relationship("Model", back_populates="files")

    def __repr__(self):
        return f"<File(id={self.id}, title={self.title}, type={self.file_type})>"

    @property
    def size_mb(self) -> float:
        """Размер файла в мегабайтах"""
        return round(self.size_bytes / (1024 * 1024), 2)

    @property
    def is_image(self) -> bool:
        """Является ли файл изображением"""
        return self.file_type in [FileType.JPG, FileType.PNG]

    @property
    def is_document(self) -> bool:
        """Является ли файл документом"""
        return self.file_type in [FileType.PDF, FileType.DOCX, FileType.XLSX]

    @property
    def is_archive(self) -> bool:
        """Является ли файл архивом"""
        return self.file_type == FileType.ZIP
