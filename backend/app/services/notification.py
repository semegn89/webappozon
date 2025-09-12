"""
Сервис уведомлений
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.ticket import TicketMessage
from app.services.telegram import TelegramService
from app.core.config import settings


class NotificationService:
    """Сервис уведомлений"""

    def __init__(self):
        self.telegram_service = TelegramService()

    async def notify_ticket_created(self, ticket: Ticket, db: AsyncSession) -> None:
        """
        Уведомление о создании нового тикета
        
        Args:
            ticket: Созданный тикет
            db: Сессия БД
        """
        # Уведомление пользователя
        user_message = (
            f"✅ <b>Тикет создан</b>\n\n"
            f"<b>Тема:</b> {ticket.subject}\n"
            f"<b>Номер:</b> #{ticket.id}\n"
            f"<b>Статус:</b> {self._get_status_text(ticket.status)}\n\n"
            f"Мы свяжемся с вами в ближайшее время."
        )
        
        await self.telegram_service.send_notification(
            ticket.user.telegram_user_id,
            user_message
        )
        
        # Уведомление админов
        admin_message = (
            f"🔔 <b>Новый тикет</b>\n\n"
            f"<b>Тема:</b> {ticket.subject}\n"
            f"<b>Номер:</b> #{ticket.id}\n"
            f"<b>Пользователь:</b> {ticket.user.full_name}\n"
            f"<b>Приоритет:</b> {self._get_priority_text(ticket.priority)}\n"
            f"<b>Статус:</b> {self._get_status_text(ticket.status)}"
        )
        
        if ticket.model:
            admin_message += f"\n<b>Модель:</b> {ticket.model.name}"
        
        await self.telegram_service.send_admin_notification(admin_message)

    async def notify_ticket_status_changed(self, ticket: Ticket, old_status: TicketStatus) -> None:
        """
        Уведомление об изменении статуса тикета
        
        Args:
            ticket: Тикет
            old_status: Предыдущий статус
        """
        if ticket.status == old_status:
            return
        
        status_emoji = {
            TicketStatus.OPEN: "📝",
            TicketStatus.IN_PROGRESS: "🔄",
            TicketStatus.RESOLVED: "✅",
            TicketStatus.CLOSED: "🔒"
        }
        
        message = (
            f"{status_emoji.get(ticket.status, '📋')} <b>Статус тикета изменен</b>\n\n"
            f"<b>Тикет:</b> #{ticket.id} - {ticket.subject}\n"
            f"<b>Новый статус:</b> {self._get_status_text(ticket.status)}\n"
            f"<b>Предыдущий статус:</b> {self._get_status_text(old_status)}"
        )
        
        if ticket.assignee:
            message += f"\n<b>Ответственный:</b> {ticket.assignee.full_name}"
        
        await self.telegram_service.send_notification(
            ticket.user.telegram_user_id,
            message
        )

    async def notify_ticket_message(self, message: TicketMessage) -> None:
        """
        Уведомление о новом сообщении в тикете
        
        Args:
            message: Сообщение
        """
        # Не уведомляем о внутренних заметках
        if message.is_internal_note:
            return
        
        # Определяем получателя уведомления
        if message.author_id == message.ticket.user_id:
            # Сообщение от пользователя - уведомляем админов
            admin_message = (
                f"💬 <b>Новое сообщение в тикете</b>\n\n"
                f"<b>Тикет:</b> #{message.ticket.id} - {message.ticket.subject}\n"
                f"<b>От:</b> {message.author.full_name}\n"
                f"<b>Сообщение:</b> {message.body[:200]}{'...' if len(message.body) > 200 else ''}"
            )
            
            await self.telegram_service.send_admin_notification(admin_message)
        else:
            # Сообщение от админа - уведомляем пользователя
            user_message = (
                f"💬 <b>Новое сообщение в тикете</b>\n\n"
                f"<b>Тикет:</b> #{message.ticket.id} - {message.ticket.subject}\n"
                f"<b>От:</b> {message.author.full_name}\n"
                f"<b>Сообщение:</b> {message.body[:200]}{'...' if len(message.body) > 200 else ''}"
            )
            
            await self.telegram_service.send_notification(
                message.ticket.user.telegram_user_id,
                user_message
            )

    async def notify_high_priority_ticket(self, ticket: Ticket) -> None:
        """
        Уведомление о тикете с высоким приоритетом
        
        Args:
            ticket: Тикет
        """
        if ticket.priority != TicketPriority.HIGH:
            return
        
        message = (
            f"🚨 <b>ВЫСОКИЙ ПРИОРИТЕТ</b>\n\n"
            f"<b>Тикет:</b> #{ticket.id} - {ticket.subject}\n"
            f"<b>Пользователь:</b> {ticket.user.full_name}\n"
            f"<b>Приоритет:</b> {self._get_priority_text(ticket.priority)}\n"
            f"<b>Описание:</b> {ticket.description[:200]}{'...' if len(ticket.description) > 200 else ''}"
        )
        
        if ticket.model:
            message += f"\n<b>Модель:</b> {ticket.model.name}"
        
        await self.telegram_service.send_admin_notification(message)

    def _get_status_text(self, status: TicketStatus) -> str:
        """Получение текста статуса на русском"""
        status_texts = {
            TicketStatus.OPEN: "Открыт",
            TicketStatus.IN_PROGRESS: "В работе",
            TicketStatus.RESOLVED: "Решен",
            TicketStatus.CLOSED: "Закрыт"
        }
        return status_texts.get(status, status.value)

    def _get_priority_text(self, priority: TicketPriority) -> str:
        """Получение текста приоритета на русском"""
        priority_texts = {
            TicketPriority.LOW: "Низкий",
            TicketPriority.NORMAL: "Обычный",
            TicketPriority.HIGH: "Высокий"
        }
        return priority_texts.get(priority, priority.value)
