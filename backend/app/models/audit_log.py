"""
Модель аудит-лога
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class EntityType(str, enum.Enum):
    """Типы сущностей для аудита"""
    MODEL = "model"
    FILE = "file"
    TICKET = "ticket"
    USER = "user"


class ActionType(str, enum.Enum):
    """Типы действий для аудита"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ASSIGN = "assign"
    STATUS_CHANGE = "status_change"


class AuditLog(Base):
    """Модель аудит-лога"""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    entity_type = Column(Enum(EntityType), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(Enum(ActionType), nullable=False, index=True)
    diff = Column(JSON, nullable=True)  # Изменения в формате JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    actor = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, actor_id={self.actor_id}, action={self.action})>"
