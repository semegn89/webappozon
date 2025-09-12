"""
Модель товара/устройства
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Model(Base):
    """Модель товара/устройства"""
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), unique=True, index=True, nullable=False)
    brand = Column(String(100), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    year_from = Column(Integer, nullable=True)
    year_to = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    files = relationship("File", back_populates="model", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="model")

    def __repr__(self):
        return f"<Model(id={self.id}, name={self.name}, code={self.code})>"

    @property
    def year_range(self) -> str:
        """Диапазон годов"""
        if self.year_from and self.year_to:
            if self.year_from == self.year_to:
                return str(self.year_from)
            return f"{self.year_from}-{self.year_to}"
        elif self.year_from:
            return f"{self.year_from}+"
        return ""

    @property
    def has_files(self) -> bool:
        """Есть ли файлы у модели"""
        return len(self.files) > 0
