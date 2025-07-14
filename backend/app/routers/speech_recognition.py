"""
API роутер для распознавания речи с помощью Whisper.

Обеспечивает endpoints для транскрипции аудиофайлов и аудиоданных.

Автор: Авабот
Версия: 1.0.0
"""

import logging
import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile

from ..services.whisper_service import get_whisper_service, transcribe_audio

logger = logging.getLogger(__name__)

router = APIRouter()


class TranscriptionRequest(BaseModel):
    """Модель запроса на транскрипцию."""
    language: str = "ru"
    model_name: str = "base"


class TranscriptionResponse(BaseModel):
    """Модель ответа транскрипции."""
    text: str
    language: str
    confidence: float
    duration: float
    segments: list
    model_name: str


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio_file(
    file: UploadFile = File(...),
    language: str = Form("ru"),
    model_name: str = Form("base")
):
    """
    Транскрипция загруженного аудиофайла.
    
    Args:
        file: Аудиофайл для транскрипции
        language: Язык аудио (ru, en, etc.)
        model_name: Модель Whisper (tiny, base, small, medium, large)
        
    Returns:
        Результат транскрипции
    """
    try:
        # Проверяем тип файла
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400, 
                detail="Файл должен быть аудиофайлом"
            )
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Получаем сервис
            service = get_whisper_service(model_name)
            
            # Проверяем поддержку языка
            if not service.is_language_supported(language):
                raise HTTPException(
                    status_code=400,
                    detail=f"Язык {language} не поддерживается"
                )
            
            # Транскрибируем
            result = service.transcribe_audio_file(temp_path, language)
            
            return TranscriptionResponse(
                text=result["text"],
                language=result["language"],
                confidence=result["confidence"],
                duration=result["duration"],
                segments=result["segments"],
                model_name=model_name
            )
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        logger.error(f"Ошибка транскрипции: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe-url")
async def transcribe_audio_url(
    request: TranscriptionRequest,
    audio_url: str = Form(...)
):
    """
    Транскрипция аудиофайла по URL.
    
    Args:
        request: Параметры транскрипции
        audio_url: URL аудиофайла
        
    Returns:
        Результат транскрипции
    """
    try:
        import requests
        
        # Загружаем файл по URL
        response = requests.get(audio_url, timeout=30)
        response.raise_for_status()
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        try:
            # Транскрибируем
            result = transcribe_audio(temp_path, request.language, request.model_name)
            
            return TranscriptionResponse(
                text=result["text"],
                language=result["language"],
                confidence=result["confidence"],
                duration=result["duration"],
                segments=result["segments"],
                model_name=request.model_name
            )
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        logger.error(f"Ошибка транскрипции по URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """
    Получение информации о доступных моделях.
    
    Returns:
        Информация о моделях
    """
    try:
        service = get_whisper_service("base")
        return service.get_model_info()
    except Exception as e:
        logger.error(f"Ошибка получения информации о моделях: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_supported_languages():
    """
    Получение списка поддерживаемых языков.
    
    Returns:
        Список языков
    """
    try:
        service = get_whisper_service("base")
        return {
            "languages": service.get_supported_languages(),
            "count": len(service.get_supported_languages())
        }
    except Exception as e:
        logger.error(f"Ошибка получения языков: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Проверка здоровья сервиса распознавания речи.
    
    Returns:
        Статус сервиса
    """
    try:
        service = get_whisper_service("base")
        model_info = service.get_model_info()
        
        return {
            "status": "healthy",
            "model": model_info["model_name"],
            "device": model_info["device"],
            "cuda_available": model_info["cuda_available"],
            "supported_languages_count": len(model_info["supported_languages"])
        }
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        ) 