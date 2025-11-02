"""
Routers package for Royal Taxi API
"""
from .auth import router as auth_router
from .users import router as users_router
from .admin import router as admin_router
from .files import router as files_router

__all__ = [
    "auth_router",
    "users_router", 
    "admin_router",
    "files_router",
]
