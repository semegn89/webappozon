"""
Эндпоинты для работы с тикетами
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.ticket import Ticket, TicketMessage, TicketStatus, TicketPriority
from app.models.user import User
from app.models.model import Model
from app.schemas.ticket import (
    Ticket as TicketSchema, 
    TicketCreate, 
    TicketUpdate, 
    TicketList, 
    TicketFilters,
    TicketMessage as TicketMessageSchema,
    TicketMessageCreate,
    TicketWithDetails,
    TicketStats
)
from app.schemas.user import User as UserSchema
from app.api.v1.endpoints.auth import get_current_user
from app.services.notification import NotificationService
from app.core.exceptions import NotFoundError, AuthorizationError

router = APIRouter()
notification_service = NotificationService()


@router.get("/", response_model=TicketList)
async def get_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    filters: TicketFilters = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка тикетов"""
    query = select(Ticket).options(
        selectinload(Ticket.user),
        selectinload(Ticket.model),
        selectinload(Ticket.assignee)
    )
    
    # Применяем фильтры
    conditions = []
    
    # Пользователи видят только свои тикеты, админы - все
    if not current_user.is_admin:
        conditions.append(Ticket.user_id == current_user.id)
    elif filters.user_id:
        conditions.append(Ticket.user_id == filters.user_id)
    
    if filters.status:
        conditions.append(Ticket.status == filters.status)
    
    if filters.priority:
        conditions.append(Ticket.priority == filters.priority)
    
    if filters.assignee_id:
        conditions.append(Ticket.assignee_id == filters.assignee_id)
    
    if filters.model_id:
        conditions.append(Ticket.model_id == filters.model_id)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Подсчет общего количества
    count_query = select(func.count(Ticket.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Применяем пагинацию
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Выполняем запрос
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    # Конвертируем в схемы
    ticket_schemas = [TicketSchema.model_validate(ticket) for ticket in tickets]
    
    return TicketList(
        items=ticket_schemas,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/stats", response_model=TicketStats)
async def get_ticket_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение статистики тикетов (только для админов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Общее количество
    total_result = await db.execute(select(func.count(Ticket.id)))
    total = total_result.scalar()
    
    # По статусам
    open_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.OPEN)
    )
    open_count = open_result.scalar()
    
    in_progress_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.IN_PROGRESS)
    )
    in_progress_count = in_progress_result.scalar()
    
    resolved_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.RESOLVED)
    )
    resolved_count = resolved_result.scalar()
    
    closed_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.CLOSED)
    )
    closed_count = closed_result.scalar()
    
    # Высокий приоритет
    high_priority_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.priority == TicketPriority.HIGH)
    )
    high_priority_count = high_priority_result.scalar()
    
    return TicketStats(
        total=total,
        open=open_count,
        in_progress=in_progress_count,
        resolved=resolved_count,
        closed=closed_count,
        high_priority=high_priority_count
    )


@router.get("/{ticket_id}", response_model=TicketWithDetails)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение тикета по ID"""
    stmt = select(Ticket).options(
        selectinload(Ticket.user),
        selectinload(Ticket.model),
        selectinload(Ticket.assignee),
        selectinload(Ticket.messages).selectinload(TicketMessage.author)
    ).where(Ticket.id == ticket_id)
    
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Проверяем права доступа
    if not current_user.is_admin and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return TicketWithDetails.model_validate(ticket)


@router.post("/", response_model=TicketSchema)
async def create_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание нового тикета"""
    # Проверяем существование модели если указана
    if ticket_data.model_id:
        stmt = select(Model).where(Model.id == ticket_data.model_id)
        result = await db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
    
    # Создаем тикет
    ticket = Ticket(
        user_id=current_user.id,
        **ticket_data.model_dump()
    )
    
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    
    # Загружаем связанные данные для уведомления
    await db.refresh(ticket, ['user', 'model'])
    
    # Отправляем уведомления
    await notification_service.notify_ticket_created(ticket, db)
    
    # Уведомляем о высоком приоритете
    if ticket.priority == TicketPriority.HIGH:
        await notification_service.notify_high_priority_ticket(ticket)
    
    return TicketSchema.model_validate(ticket)


@router.put("/{ticket_id}", response_model=TicketSchema)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление тикета"""
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Проверяем права доступа
    if not current_user.is_admin and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Сохраняем старый статус для уведомления
    old_status = ticket.status
    
    # Обновляем поля
    update_data = ticket_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)
    
    # Устанавливаем время закрытия если статус изменился на закрытый
    if ticket.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED] and old_status not in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
        from datetime import datetime
        ticket.closed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(ticket)
    
    # Загружаем связанные данные для уведомления
    await db.refresh(ticket, ['user', 'assignee'])
    
    # Отправляем уведомление об изменении статуса
    if old_status != ticket.status:
        await notification_service.notify_ticket_status_changed(ticket, old_status)
    
    return TicketSchema.model_validate(ticket)


@router.get("/{ticket_id}/messages", response_model=List[TicketMessageSchema])
async def get_ticket_messages(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение сообщений тикета"""
    # Проверяем существование тикета и права доступа
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if not current_user.is_admin and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Получаем сообщения
    stmt = select(TicketMessage).options(
        selectinload(TicketMessage.author)
    ).where(TicketMessage.ticket_id == ticket_id).order_by(TicketMessage.created_at)
    
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
    # Фильтруем внутренние заметки для обычных пользователей
    if not current_user.is_admin:
        messages = [msg for msg in messages if not msg.is_internal_note]
    
    return [TicketMessageSchema.model_validate(msg) for msg in messages]


@router.post("/{ticket_id}/messages", response_model=TicketMessageSchema)
async def create_ticket_message(
    ticket_id: int,
    message_data: TicketMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание сообщения в тикете"""
    # Проверяем существование тикета и права доступа
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if not current_user.is_admin and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Обычные пользователи не могут создавать внутренние заметки
    if message_data.is_internal_note and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create internal notes"
        )
    
    # Создаем сообщение
    message = TicketMessage(
        ticket_id=ticket_id,
        author_id=current_user.id,
        **message_data.model_dump()
    )
    
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    # Загружаем связанные данные для уведомления
    await db.refresh(message, ['author', 'ticket'])
    await db.refresh(message.ticket, ['user'])
    
    # Отправляем уведомление
    await notification_service.notify_ticket_message(message)
    
    return TicketMessageSchema.model_validate(message)
