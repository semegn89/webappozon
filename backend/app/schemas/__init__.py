"""
Pydantic схемы для API
"""

from .user import User, UserCreate, UserUpdate, UserInDB
from .model import Model, ModelCreate, ModelUpdate, ModelInDB
from .file import File, FileCreate, FileUpdate, FileInDB
from .ticket import Ticket, TicketCreate, TicketUpdate, TicketInDB, TicketMessage, TicketMessageCreate
from .auth import Token, TokenData, TelegramAuth

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "Model", "ModelCreate", "ModelUpdate", "ModelInDB", 
    "File", "FileCreate", "FileUpdate", "FileInDB",
    "Ticket", "TicketCreate", "TicketUpdate", "TicketInDB",
    "TicketMessage", "TicketMessageCreate",
    "Token", "TokenData", "TelegramAuth"
]
