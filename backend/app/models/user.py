"""
Модель пользователя
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """Роли пользователей"""
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="ru")
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    tickets = relationship("Ticket", back_populates="user", foreign_keys="Ticket.user_id")
    ticket_messages = relationship("TicketMessage", back_populates="author")
    assigned_tickets = relationship("Ticket", back_populates="assignee", foreign_keys="Ticket.assignee_id")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_user_id={self.telegram_user_id}, username={self.username})>"

    @property
    def full_name(self) -> str:
        """Полное имя пользователя"""
        parts = [self.first_name, self.last_name]
        return " ".join(filter(None, parts)) or self.username or f"User {self.telegram_user_id}"

    @property
    def is_admin(self) -> bool:
        """Проверка, является ли пользователь админом"""
        return self.role == UserRole.ADMIN
