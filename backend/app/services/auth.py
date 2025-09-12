"""
Сервис аутентификации
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User, UserRole
from app.schemas.auth import Token, TokenData
from app.services.telegram import TelegramService


class AuthService:
    """Сервис аутентификации"""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.telegram_service = TelegramService()

    def create_access_token(self, user_id: int, telegram_user_id: int, role: str) -> Token:
        """
        Создание JWT токена
        
        Args:
            user_id: ID пользователя в БД
            telegram_user_id: Telegram user ID
            role: Роль пользователя
            
        Returns:
            JWT токен
        """
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "sub": str(user_id),
            "telegram_user_id": telegram_user_id,
            "role": role,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        return Token(
            access_token=encoded_jwt,
            expires_at=expire
        )

    def verify_token(self, token: str) -> TokenData:
        """
        Проверка JWT токена
        
        Args:
            token: JWT токен
            
        Returns:
            Данные токена
            
        Raises:
            AuthenticationError: Если токен неверен
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            telegram_user_id: int = payload.get("telegram_user_id")
            role: str = payload.get("role")
            
            if user_id is None or telegram_user_id is None or role is None:
                raise AuthenticationError("Invalid token payload")
            
            return TokenData(
                user_id=int(user_id),
                telegram_user_id=telegram_user_id,
                role=role
            )
        except JWTError:
            raise AuthenticationError("Invalid token")

    async def authenticate_telegram(self, init_data: str, db: AsyncSession) -> tuple[User, Token]:
        """
        Аутентификация через Telegram WebApp
        
        Args:
            init_data: initData от Telegram
            db: Сессия БД
            
        Returns:
            Кортеж (пользователь, токен)
            
        Raises:
            AuthenticationError: Если аутентификация не удалась
        """
        # Проверяем подпись Telegram
        telegram_data = self.telegram_service.verify_init_data(init_data)
        
        telegram_user_id = telegram_data['telegram_user_id']
        if not telegram_user_id:
            raise AuthenticationError("Missing telegram user ID")
        
        # Ищем пользователя в БД
        stmt = select(User).where(User.telegram_user_id == telegram_user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        # Создаем пользователя если не найден
        if not user:
            user = User(
                telegram_user_id=telegram_user_id,
                username=telegram_data.get('username'),
                first_name=telegram_data.get('first_name'),
                last_name=telegram_data.get('last_name'),
                language_code=telegram_data.get('language_code', 'ru'),
                role=UserRole.ADMIN if telegram_user_id in settings.admin_user_ids_list else UserRole.USER
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            # Обновляем данные пользователя
            user.username = telegram_data.get('username') or user.username
            user.first_name = telegram_data.get('first_name') or user.first_name
            user.last_name = telegram_data.get('last_name') or user.last_name
            user.language_code = telegram_data.get('language_code', user.language_code)
            
            # Проверяем роль админа
            if telegram_user_id in settings.admin_user_ids_list:
                user.role = UserRole.ADMIN
            
            await db.commit()
            await db.refresh(user)
        
        # Создаем токен
        token = self.create_access_token(user.id, user.telegram_user_id, user.role.value)
        
        return user, token

    async def get_current_user(self, token: str, db: AsyncSession) -> User:
        """
        Получение текущего пользователя по токену
        
        Args:
            token: JWT токен
            db: Сессия БД
            
        Returns:
            Пользователь
            
        Raises:
            AuthenticationError: Если пользователь не найден
        """
        token_data = self.verify_token(token)
        
        stmt = select(User).where(User.id == token_data.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            raise AuthenticationError("User not found")
        
        if user.is_blocked:
            raise AuthenticationError("User is blocked")
        
        return user

    def require_admin(self, user: User) -> None:
        """
        Проверка прав администратора
        
        Args:
            user: Пользователь
            
        Raises:
            AuthorizationError: Если нет прав администратора
        """
        if user.role != UserRole.ADMIN:
            raise AuthorizationError("Admin access required")

    def require_user(self, user: User) -> None:
        """
        Проверка что пользователь не заблокирован
        
        Args:
            user: Пользователь
            
        Raises:
            AuthorizationError: Если пользователь заблокирован
        """
        if user.is_blocked:
            raise AuthorizationError("User is blocked")
