"""
Схемы тикетов
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.ticket import TicketPriority, TicketStatus


class TicketBase(BaseModel):
    """Базовая схема тикета"""
    subject: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    priority: TicketPriority = TicketPriority.NORMAL
    model_id: Optional[int] = None


class TicketCreate(TicketBase):
    """Схема создания тикета"""
    pass


class TicketUpdate(BaseModel):
    """Схема обновления тикета"""
    subject: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assignee_id: Optional[int] = None


class TicketInDB(TicketBase):
    """Схема тикета в БД"""
    id: int
    user_id: int
    status: TicketStatus
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Ticket(TicketInDB):
    """Публичная схема тикета"""
    is_open: bool
    is_closed: bool

    class Config:
        from_attributes = True


class TicketWithDetails(Ticket):
    """Схема тикета с деталями"""
    user: "User"
    model: Optional["Model"] = None
    assignee: Optional["User"] = None
    messages: List["TicketMessage"] = []

    class Config:
        from_attributes = True


class TicketList(BaseModel):
    """Схема списка тикетов"""
    items: List[Ticket]
    total: int
    page: int
    page_size: int
    pages: int


class TicketFilters(BaseModel):
    """Фильтры для поиска тикетов"""
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assignee_id: Optional[int] = None
    model_id: Optional[int] = None
    user_id: Optional[int] = None  # Только для админов


class TicketMessageBase(BaseModel):
    """Базовая схема сообщения тикета"""
    body: str = Field(..., min_length=1)
    attachments: Optional[List[Dict[str, Any]]] = None
    is_internal_note: bool = False


class TicketMessageCreate(TicketMessageBase):
    """Схема создания сообщения тикета"""
    pass


class TicketMessageInDB(TicketMessageBase):
    """Схема сообщения тикета в БД"""
    id: int
    ticket_id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TicketMessage(TicketMessageInDB):
    """Публичная схема сообщения тикета"""
    author: "User"

    class Config:
        from_attributes = True


class TicketStats(BaseModel):
    """Статистика тикетов"""
    total: int
    open: int
    in_progress: int
    resolved: int
    closed: int
    high_priority: int
