"""
Админские эндпоинты
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.model import Model
from app.models.file import File
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.schemas.user import User as UserSchema, UserUpdate, UserList
from app.schemas.model import Model as ModelSchema, ModelList
from app.schemas.ticket import Ticket as TicketSchema, TicketList, TicketStats
from app.api.v1.endpoints.auth import get_current_user
from app.core.exceptions import AuthorizationError

router = APIRouter()


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Проверка прав администратора"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/users", response_model=UserList)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: UserRole = Query(None),
    is_blocked: bool = Query(None),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Получение списка пользователей"""
    query = select(User)
    
    # Применяем фильтры
    conditions = []
    
    if role:
        conditions.append(User.role == role)
    
    if is_blocked is not None:
        conditions.append(User.is_blocked == is_blocked)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Подсчет общего количества
    count_query = select(func.count(User.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Применяем пагинацию
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Выполняем запрос
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Конвертируем в схемы
    user_schemas = [UserSchema.model_validate(user) for user in users]
    
    return UserList(
        items=user_schemas,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Обновление пользователя"""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Нельзя изменить роль самого себя
    if user_id == admin_user.id and user_data.role and user_data.role != admin_user.role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    # Обновляем поля
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return UserSchema.model_validate(user)


@router.get("/models", response_model=ModelList)
async def get_all_models(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: bool = Query(None),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Получение всех моделей для админов"""
    query = select(Model).options(selectinload(Model.files))
    
    if is_active is not None:
        query = query.where(Model.is_active == is_active)
    
    # Подсчет общего количества
    count_query = select(func.count(Model.id))
    if is_active is not None:
        count_query = count_query.where(Model.is_active == is_active)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Применяем пагинацию
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Выполняем запрос
    result = await db.execute(query)
    models = result.scalars().all()
    
    # Конвертируем в схемы
    model_schemas = [ModelSchema.model_validate(model) for model in models]
    
    return ModelList(
        items=model_schemas,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/tickets", response_model=TicketList)
async def get_all_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: TicketStatus = Query(None),
    priority: TicketPriority = Query(None),
    assignee_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Получение всех тикетов для админов"""
    query = select(Ticket).options(
        selectinload(Ticket.user),
        selectinload(Ticket.model),
        selectinload(Ticket.assignee)
    )
    
    # Применяем фильтры
    conditions = []
    
    if status:
        conditions.append(Ticket.status == status)
    
    if priority:
        conditions.append(Ticket.priority == priority)
    
    if assignee_id:
        conditions.append(Ticket.assignee_id == assignee_id)
    
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


@router.get("/stats", response_model=dict)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Получение общей статистики для админов"""
    # Статистика пользователей
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()
    
    admin_users_result = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.ADMIN)
    )
    admin_users = admin_users_result.scalar()
    
    blocked_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_blocked == True)
    )
    blocked_users = blocked_users_result.scalar()
    
    # Статистика моделей
    total_models_result = await db.execute(select(func.count(Model.id)))
    total_models = total_models_result.scalar()
    
    active_models_result = await db.execute(
        select(func.count(Model.id)).where(Model.is_active == True)
    )
    active_models = active_models_result.scalar()
    
    # Статистика файлов
    total_files_result = await db.execute(select(func.count(File.id)))
    total_files = total_files_result.scalar()
    
    # Статистика тикетов
    total_tickets_result = await db.execute(select(func.count(Ticket.id)))
    total_tickets = total_tickets_result.scalar()
    
    open_tickets_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.OPEN)
    )
    open_tickets = open_tickets_result.scalar()
    
    high_priority_tickets_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.priority == TicketPriority.HIGH)
    )
    high_priority_tickets = high_priority_tickets_result.scalar()
    
    return {
        "users": {
            "total": total_users,
            "admins": admin_users,
            "blocked": blocked_users
        },
        "models": {
            "total": total_models,
            "active": active_models
        },
        "files": {
            "total": total_files
        },
        "tickets": {
            "total": total_tickets,
            "open": open_tickets,
            "high_priority": high_priority_tickets
        }
    }
