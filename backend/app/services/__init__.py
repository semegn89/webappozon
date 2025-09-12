"""
Сервисы приложения
"""

from .auth import AuthService
from .telegram import TelegramService
from .file import FileService
from .notification import NotificationService

__all__ = [
    "AuthService",
    "TelegramService", 
    "FileService",
    "NotificationService"
]
