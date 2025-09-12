"""
Обработчики исключений
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class CustomHTTPException(HTTPException):
    """Кастомное HTTP исключение"""
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class AuthenticationError(CustomHTTPException):
    """Ошибка аутентификации"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail, error_code="AUTH_ERROR")


class AuthorizationError(CustomHTTPException):
    """Ошибка авторизации"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=403, detail=detail, error_code="AUTHZ_ERROR")


class NotFoundError(CustomHTTPException):
    """Ошибка "не найдено" """
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail, error_code="NOT_FOUND")


class ValidationError(CustomHTTPException):
    """Ошибка валидации"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=422, detail=detail, error_code="VALIDATION_ERROR")


class RateLimitError(CustomHTTPException):
    """Ошибка превышения лимита запросов"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail, error_code="RATE_LIMIT")


async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик HTTP исключений"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": getattr(exc, 'error_code', f"HTTP_{exc.status_code}"),
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации"""
    logger.warning(f"Validation error: {exc.errors()} - {request.url}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": exc.errors()
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик общих исключений"""
    logger.error(f"Unhandled exception: {str(exc)} - {request.url}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error"
            }
        }
    )


def setup_exception_handlers(app: FastAPI):
    """Настройка обработчиков исключений"""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
