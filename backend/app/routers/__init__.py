"""
Роутеры для API endpoints.

Модуль содержит все API роутеры для системы цифрового аватара.

Автор: Авабот
Версия: 1.0.0
"""

from fastapi import APIRouter

# Создание основного API роутера
api_router = APIRouter()

# Здесь будут импортироваться и подключаться все роутеры
# from .avatar import router as avatar_router
# from .voice import router as voice_router
# from .chat import router as chat_router

# api_router.include_router(avatar_router, prefix="/avatar", tags=["avatar"])
# api_router.include_router(voice_router, prefix="/voice", tags=["voice"])
# api_router.include_router(chat_router, prefix="/chat", tags=["chat"]) 