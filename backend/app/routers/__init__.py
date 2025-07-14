"""
Роутеры для API endpoints.

Модуль содержит все API роутеры для системы цифрового аватара.

Автор: Авабот
Версия: 1.0.0
"""

from fastapi import APIRouter

# Создание основного API роутера
api_router = APIRouter()

# Импорт и подключение роутеров
from .tts import router as tts_router
from .upload import router as upload_router
from .speech_recognition import router as speech_router
from .ai_chat import router as chat_router
from .hier_tts import router as hier_tts_router
from .whisper import router as whisper_router

# Подключение роутеров
api_router.include_router(tts_router, tags=["TTS"])
api_router.include_router(upload_router, tags=["Upload"])
api_router.include_router(speech_router, prefix="/speech", tags=["Speech Recognition"])
api_router.include_router(chat_router, prefix="/chat", tags=["AI Chat"])
api_router.include_router(hier_tts_router, prefix="/hier-tts", tags=["HierSpeech TTS"])
api_router.include_router(whisper_router, prefix="", tags=["Whisper ASR"]) 