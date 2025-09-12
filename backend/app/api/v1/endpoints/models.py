"""
Эндпоинты для работы с моделями
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.model import Model
from app.models.file import File
from app.schemas.model import Model as ModelSchema, ModelCreate, ModelUpdate, ModelList, ModelFilters
from app.schemas.user import User
from app.api.v1.endpoints.auth import get_current_user
from app.core.exceptions import NotFoundError, AuthorizationError

router = APIRouter()


@router.get("/", response_model=ModelList)
async def get_models(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    filters: ModelFilters = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение списка моделей с фильтрацией и пагинацией
    """
    # Базовый запрос
    query = select(Model).options(selectinload(Model.files))
    
    # Применяем фильтры
    conditions = []
    
    if filters.q:
        search_term = f"%{filters.q}%"
        conditions.append(
            or_(
                Model.name.ilike(search_term),
                Model.code.ilike(search_term),
                Model.brand.ilike(search_term),
                Model.description.ilike(search_term)
            )
        )
    
    if filters.brand:
        conditions.append(Model.brand == filters.brand)
    
    if filters.category:
        conditions.append(Model.category == filters.category)
    
    if filters.year_from:
        conditions.append(Model.year_from >= filters.year_from)
    
    if filters.year_to:
        conditions.append(Model.year_to <= filters.year_to)
    
    if filters.has_files is not None:
        if filters.has_files:
            conditions.append(Model.files.any())
        else:
            conditions.append(~Model.files.any())
    
    if filters.is_active is not None:
        conditions.append(Model.is_active == filters.is_active)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Подсчет общего количества
    count_query = select(func.count(Model.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
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


@router.get("/{model_id}", response_model=ModelSchema)
async def get_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение модели по ID"""
    stmt = select(Model).options(selectinload(Model.files)).where(Model.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return ModelSchema.model_validate(model)


@router.post("/", response_model=ModelSchema)
async def create_model(
    model_data: ModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание новой модели (только для админов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Проверяем уникальность кода
    stmt = select(Model).where(Model.code == model_data.code)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model with this code already exists"
        )
    
    model = Model(**model_data.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model)
    
    return ModelSchema.model_validate(model)


@router.put("/{model_id}", response_model=ModelSchema)
async def update_model(
    model_id: int,
    model_data: ModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление модели (только для админов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    stmt = select(Model).where(Model.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Проверяем уникальность кода если он изменяется
    if model_data.code and model_data.code != model.code:
        stmt = select(Model).where(Model.code == model_data.code)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Model with this code already exists"
            )
    
    # Обновляем поля
    update_data = model_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)
    
    await db.commit()
    await db.refresh(model)
    
    return ModelSchema.model_validate(model)


@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление модели (только для админов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    stmt = select(Model).where(Model.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    await db.delete(model)
    await db.commit()
    
    return {"message": "Model deleted successfully"}


@router.get("/{model_id}/files")
async def get_model_files(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение файлов модели"""
    stmt = select(Model).options(selectinload(Model.files)).where(Model.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return {"files": model.files}
