"""
Эндпоинты аутентификации
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import TelegramAuth, AuthResponse, Token
from app.schemas.user import User
from app.services.auth import AuthService
from app.core.exceptions import AuthenticationError

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Получение текущего пользователя"""
    try:
        return await auth_service.get_current_user(credentials.credentials, db)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/verify", response_model=AuthResponse)
async def verify_telegram_auth(
    auth_data: TelegramAuth,
    db: AsyncSession = Depends(get_db)
):
    """
    Верификация аутентификации через Telegram WebApp
    
    Принимает initData от Telegram и возвращает JWT токен
    """
    try:
        user, token = await auth_service.authenticate_telegram(auth_data.init_data, db)
        
        return AuthResponse(
            token=token,
            user=user,
            is_admin=user.is_admin
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """Обновление токена"""
    token = auth_service.create_access_token(
        current_user.id,
        current_user.telegram_user_id,
        current_user.role.value
    )
    return token
