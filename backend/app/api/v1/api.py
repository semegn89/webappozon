"""
Главный роутер API v1
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, models, files, tickets, admin

api_router = APIRouter()

# Подключение роутеров
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
