"""
Сервис для работы с Telegram API
"""

import hashlib
import hmac
import json
import urllib.parse
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
from app.core.config import settings
from app.core.exceptions import AuthenticationError


class TelegramService:
    """Сервис для работы с Telegram API"""

    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.bot_username = settings.TELEGRAM_BOT_USERNAME

    def verify_init_data(self, init_data: str) -> Dict[str, Any]:
        """
        Проверка подписи initData от Telegram WebApp
        
        Args:
            init_data: Строка initData от Telegram
            
        Returns:
            Dict с данными пользователя
            
        Raises:
            AuthenticationError: Если подпись неверна
        """
        try:
            # Парсим initData
            parsed_data = urllib.parse.parse_qs(init_data)
            
            # Извлекаем hash и остальные данные
            received_hash = parsed_data.get('hash', [None])[0]
            if not received_hash:
                raise AuthenticationError("Missing hash in init data")
            
            # Создаем строку для проверки подписи
            data_check_string = []
            for key, value in parsed_data.items():
                if key != 'hash':
                    data_check_string.append(f"{key}={value[0]}")
            
            data_check_string.sort()
            data_check_string = '\n'.join(data_check_string)
            
            # Создаем секретный ключ
            secret_key = hmac.new(
                "WebAppData".encode(),
                self.bot_token.encode(),
                hashlib.sha256
            ).digest()
            
            # Проверяем подпись
            calculated_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(calculated_hash, received_hash):
                raise AuthenticationError("Invalid signature")
            
            # Проверяем время (не старше 24 часов)
            auth_date = int(parsed_data.get('auth_date', [0])[0])
            if datetime.now().timestamp() - auth_date > 86400:  # 24 часа
                raise AuthenticationError("Init data expired")
            
            # Парсим user данные
            user_data = json.loads(parsed_data.get('user', ['{}'])[0])
            
            return {
                'telegram_user_id': user_data.get('id'),
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'language_code': user_data.get('language_code', 'ru'),
                'auth_date': auth_date
            }
            
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            raise AuthenticationError(f"Invalid init data format: {str(e)}")

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """
        Отправка сообщения пользователю
        
        Args:
            chat_id: ID чата
            text: Текст сообщения
            parse_mode: Режим парсинга (HTML или Markdown)
            
        Returns:
            True если сообщение отправлено успешно
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": parse_mode
                    }
                )
                return response.status_code == 200
        except Exception:
            return False

    async def send_notification(self, user_id: int, message: str) -> bool:
        """
        Отправка уведомления пользователю
        
        Args:
            user_id: Telegram user ID
            message: Текст уведомления
            
        Returns:
            True если уведомление отправлено
        """
        return await self.send_message(user_id, message)

    async def send_admin_notification(self, message: str) -> bool:
        """
        Отправка уведомления всем админам
        
        Args:
            message: Текст уведомления
            
        Returns:
            True если уведомления отправлены
        """
        success = True
        for admin_id in settings.admin_user_ids_list:
            if not await self.send_message(admin_id, message):
                success = False
        return success

    def get_webapp_url(self, path: str = "") -> str:
        """
        Получение URL для WebApp
        
        Args:
            path: Путь в приложении
            
        Returns:
            URL WebApp
        """
        base_url = settings.TELEGRAM_WEBAPP_URL.rstrip('/')
        if path:
            path = path.lstrip('/')
            return f"{base_url}/{path}"
        return base_url
