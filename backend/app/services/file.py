"""
Сервис для работы с файлами
"""

import os
import uuid
import mimetypes
from datetime import datetime, timedelta
from typing import Optional, BinaryIO, Dict, Any
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ValidationError, NotFoundError
from app.models.file import File, FileType


class FileService:
    """Сервис для работы с файлами"""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.max_file_size = settings.MAX_FILE_SIZE
        self.use_s3 = settings.use_s3_storage
        
        # Создаем директорию для загрузок если используем локальное хранилище
        if not self.use_s3 and not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir, exist_ok=True)
        
        # Настройка S3 клиента
        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
                region_name=settings.S3_REGION
            )

    def get_file_type(self, filename: str) -> FileType:
        """
        Определение типа файла по расширению
        
        Args:
            filename: Имя файла
            
        Returns:
            Тип файла
        """
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        type_mapping = {
            'pdf': FileType.PDF,
            'docx': FileType.DOCX,
            'xlsx': FileType.XLSX,
            'jpg': FileType.JPG,
            'jpeg': FileType.JPG,
            'png': FileType.PNG,
            'zip': FileType.ZIP
        }
        
        return type_mapping.get(ext, FileType.OTHER)

    def generate_storage_key(self, filename: str) -> str:
        """
        Генерация уникального ключа для хранения файла
        
        Args:
            filename: Исходное имя файла
            
        Returns:
            Уникальный ключ
        """
        ext = filename.split('.')[-1] if '.' in filename else ''
        unique_id = str(uuid.uuid4())
        return f"files/{unique_id}.{ext}" if ext else f"files/{unique_id}"

    async def upload_file(self, file: UploadFile, model_id: int) -> Dict[str, Any]:
        """
        Загрузка файла
        
        Args:
            file: Файл для загрузки
            model_id: ID модели
            
        Returns:
            Данные загруженного файла
            
        Raises:
            ValidationError: Если файл не подходит
        """
        # Проверка размера файла
        if file.size and file.size > self.max_file_size:
            raise ValidationError(f"File size exceeds maximum allowed size of {self.max_file_size} bytes")
        
        # Определение типа файла
        file_type = self.get_file_type(file.filename)
        
        # Генерация ключа хранения
        storage_key = self.generate_storage_key(file.filename)
        
        # Чтение содержимого файла
        content = await file.read()
        file_size = len(content)
        
        # Загрузка в хранилище
        if self.use_s3:
            try:
                self.s3_client.put_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=storage_key,
                    Body=content,
                    ContentType=file.content_type or mimetypes.guess_type(file.filename)[0]
                )
            except ClientError as e:
                raise ValidationError(f"Failed to upload file to S3: {str(e)}")
        else:
            # Локальное сохранение
            file_path = os.path.join(self.upload_dir, storage_key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(content)
        
        return {
            'filename': file.filename,
            'storage_key': storage_key,
            'file_type': file_type,
            'size_bytes': file_size,
            'content_type': file.content_type
        }

    def generate_download_url(self, file: File, expires_in_minutes: int = 15) -> str:
        """
        Генерация подписанной ссылки для скачивания
        
        Args:
            file: Файл
            expires_in_minutes: Время жизни ссылки в минутах
            
        Returns:
            URL для скачивания
        """
        if self.use_s3:
            try:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': file.storage_key},
                    ExpiresIn=expires_in_minutes * 60
                )
                return url
            except ClientError:
                raise NotFoundError("File not found in storage")
        else:
            # Для локального хранилища возвращаем путь к API эндпоинту
            return f"/api/v1/files/{file.id}/download"

    def delete_file(self, storage_key: str) -> bool:
        """
        Удаление файла из хранилища
        
        Args:
            storage_key: Ключ файла в хранилище
            
        Returns:
            True если файл удален
        """
        try:
            if self.use_s3:
                self.s3_client.delete_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=storage_key
                )
            else:
                file_path = os.path.join(self.upload_dir, storage_key)
                if os.path.exists(file_path):
                    os.remove(file_path)
            return True
        except (ClientError, OSError):
            return False

    def get_file_content(self, storage_key: str) -> Optional[bytes]:
        """
        Получение содержимого файла
        
        Args:
            storage_key: Ключ файла в хранилище
            
        Returns:
            Содержимое файла или None
        """
        try:
            if self.use_s3:
                response = self.s3_client.get_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=storage_key
                )
                return response['Body'].read()
            else:
                file_path = os.path.join(self.upload_dir, storage_key)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        return f.read()
            return None
        except (ClientError, OSError):
            return None
