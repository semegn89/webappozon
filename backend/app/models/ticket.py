"""
Модели тикетов поддержки
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TicketPriority(str, enum.Enum):
    """Приоритеты тикетов"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class TicketStatus(str, enum.Enum):
    """Статусы тикетов"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Ticket(Base):
    """Модель тикета поддержки"""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.NORMAL, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Связи
    user = relationship("User", back_populates="tickets", foreign_keys=[user_id])
    model = relationship("Model", back_populates="tickets")
    assignee = relationship("User", back_populates="assigned_tickets", foreign_keys=[assignee_id])
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ticket(id={self.id}, subject={self.subject}, status={self.status})>"

    @property
    def is_open(self) -> bool:
        """Открыт ли тикет"""
        return self.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]

    @property
    def is_closed(self) -> bool:
        """Закрыт ли тикет"""
        return self.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]


class TicketMessage(Base):
    """Модель сообщения в тикете"""
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    body = Column(Text, nullable=False)
    attachments = Column(JSON, nullable=True)  # Список прикрепленных файлов
    is_internal_note = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    ticket = relationship("Ticket", back_populates="messages")
    author = relationship("User", back_populates="ticket_messages")

    def __repr__(self):
        return f"<TicketMessage(id={self.id}, ticket_id={self.ticket_id}, author_id={self.author_id})>"
