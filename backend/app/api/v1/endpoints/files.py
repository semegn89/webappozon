"""
Эндпоинты для работы с файлами
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import io

from app.core.database import get_db
from app.models.file import File
from app.models.model import Model
from app.schemas.file import File as FileSchema, FileCreate, FileUpdate, FileList, FileDownload
from app.schemas.user import User
from app.api.v1.endpoints.auth import get_current_user
from app.services.file import FileService
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()
file_service = FileService()


@router.get("/", response_model=FileList)
async def get_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    model_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка файлов"""
    query = select(File).options(selectinload(File.model))
    
    if model_id:
        query = query.where(File.model_id == model_id)
    
    # Применяем пагинацию
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    files = result.scalars().all()
    
    # Подсчет общего количества
    count_query = select(File)
    if model_id:
        count_query = count_query.where(File.model_id == model_id)
    
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())
    
    file_schemas = [FileSchema.model_validate(file) for file in files]
    
    return FileList(
        items=file_schemas,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/{file_id}", response_model=FileSchema)
async def get_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение информации о файле"""
    stmt = select(File).options(selectinload(File.model)).where(File.id == file_id)
    result = await db.execute(stmt)
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileSchema.model_validate(file)


@router.get("/{file_id}/download", response_class=StreamingResponse)
async def download_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Скачивание файла"""
    stmt = select(File).where(File.id == file_id)
    result = await db.execute(stmt)
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Получаем содержимое файла
    content = file_service.get_file_content(file.storage_key)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File content not found"
        )
    
    # Определяем имя файла для скачивания
    filename = f"{file.title}.{file.file_type}"
    
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{file_id}/download-url", response_model=FileDownload)
async def get_download_url(
    file_id: int,
    expires_in_minutes: int = Query(15, ge=1, le=60),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение подписанной ссылки для скачивания"""
    stmt = select(File).where(File.id == file_id)
    result = await db.execute(stmt)
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        download_url = file_service.generate_download_url(file, expires_in_minutes)
        
        from datetime import datetime, timedelta
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        return FileDownload(
            download_url=download_url,
            expires_at=expires_at,
            filename=f"{file.title}.{file.file_type}",
            size_bytes=file.size_bytes
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download URL: {str(e)}"
        )


@router.post("/", response_model=FileSchema)
async def upload_file(
    model_id: int,
    file: UploadFile = FastAPIFile(...),
    title: str = Query(...),
    version: str = Query(None),
    is_public: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Загрузка файла (только для админов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Проверяем существование модели
    stmt = select(Model).where(Model.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    try:
        # Загружаем файл
        file_data = await file_service.upload_file(file, model_id)
        
        # Создаем запись в БД
        db_file = File(
            model_id=model_id,
            title=title,
            file_type=file_data['file_type'],
            storage_key=file_data['storage_key'],
            size_bytes=file_data['size_bytes'],
            is_public=is_public,
            version=version
        )
        
        db.add(db_file)
        await db.commit()
        await db.refresh(db_file)
        
        return FileSchema.model_validate(db_file)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{file_id}", response_model=FileSchema)
async def update_file(
    file_id: int,
    file_data: FileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление информации о файле (только для админов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    stmt = select(File).where(File.id == file_id)
    result = await db.execute(stmt)
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Обновляем поля
    update_data = file_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(file, field, value)
    
    await db.commit()
    await db.refresh(file)
    
    return FileSchema.model_validate(file)


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление файла (только для админов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    stmt = select(File).where(File.id == file_id)
    result = await db.execute(stmt)
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Удаляем файл из хранилища
    file_service.delete_file(file.storage_key)
    
    # Удаляем запись из БД
    await db.delete(file)
    await db.commit()
    
    return {"message": "File deleted successfully"}
