"""
API роутер для ИИ-общения с помощью Ollama.

Обеспечивает endpoints для генерации ответов и управления разговором.

Автор: Авабот
Версия: 1.0.0
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.ollama_service import get_ollama_service, generate_ai_response

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Модель запроса на генерацию ответа."""
    message: str
    context: str = ""
    model: str = "llama3.2:3b"
    max_tokens: int = 500
    temperature: float = 0.7


class ChatResponse(BaseModel):
    """Модель ответа чата."""
    response: str
    model: str
    prompt_tokens: int
    response_tokens: int
    total_duration: float
    timestamp: str


class ConversationMessage(BaseModel):
    """Модель сообщения в разговоре."""
    user: str
    assistant: str
    timestamp: str


class ConversationHistory(BaseModel):
    """Модель истории разговора."""
    messages: List[ConversationMessage]
    total_messages: int


@router.post("/chat", response_model=ChatResponse)
async def generate_chat_response(request: ChatRequest):
    """
    Генерация ответа на сообщение пользователя.
    
    Args:
        request: Запрос с сообщением и параметрами
        
    Returns:
        Сгенерированный ответ
    """
    try:
        # Получаем сервис
        service = await get_ollama_service(request.model)
        
        # Проверяем подключение
        if not await service.check_connection():
            raise HTTPException(
                status_code=503,
                detail="Ollama сервис недоступен"
            )
        
        # Генерируем ответ
        result = await service.generate_response(
            request.message,
            request.context,
            request.max_tokens,
            request.temperature
        )
        
        return ChatResponse(
            response=result["response"],
            model=result["model"],
            prompt_tokens=result["prompt_tokens"],
            response_tokens=result["response_tokens"],
            total_duration=result["total_duration"],
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Ошибка генерации ответа: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """
    Получение списка доступных моделей.
    
    Returns:
        Список моделей
    """
    try:
        service = await get_ollama_service()
        
        if not await service.check_connection():
            raise HTTPException(
                status_code=503,
                detail="Ollama сервис недоступен"
            )
        
        models = await service.get_available_models()
        return {
            "models": models,
            "count": len(models),
            "current_model": service.model
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения моделей: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=ConversationHistory)
async def get_conversation_history():
    """
    Получение истории разговора.
    
    Returns:
        История разговора
    """
    try:
        service = await get_ollama_service()
        history = service.get_conversation_history()
        
        messages = [
            ConversationMessage(
                user=msg["user"],
                assistant=msg["assistant"],
                timestamp=msg["timestamp"]
            )
            for msg in history
        ]
        
        return ConversationHistory(
            messages=messages,
            total_messages=len(messages)
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения истории: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history")
async def clear_conversation_history():
    """
    Очистка истории разговора.
    
    Returns:
        Подтверждение очистки
    """
    try:
        service = await get_ollama_service()
        service.clear_history()
        
        return {
            "message": "История разговора очищена",
            "timestamp": "2025-07-13T20:40:00.000000"
        }
        
    except Exception as e:
        logger.error(f"Ошибка очистки истории: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history/add")
async def add_to_history(message: ConversationMessage):
    """
    Добавление сообщения в историю разговора.
    
    Args:
        message: Сообщение для добавления
        
    Returns:
        Подтверждение добавления
    """
    try:
        service = await get_ollama_service()
        service.add_to_history(message.user, message.assistant)
        
        return {
            "message": "Сообщение добавлено в историю",
            "timestamp": "2025-07-13T20:40:00.000000"
        }
        
    except Exception as e:
        logger.error(f"Ошибка добавления в историю: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Проверка здоровья сервиса ИИ-чата.
    
    Returns:
        Статус сервиса
    """
    try:
        service = await get_ollama_service()
        
        # Проверяем подключение
        connection_ok = await service.check_connection()
        
        if connection_ok:
            # Получаем модели
            models = await service.get_available_models()
            
            return {
                "status": "healthy",
                "connection": "ok",
                "current_model": service.model,
                "available_models": len(models),
                "conversation_history_length": len(service.get_conversation_history())
            }
        else:
            return {
                "status": "unhealthy",
                "connection": "failed",
                "error": "Не удается подключиться к Ollama"
            }
            
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/test")
async def test_chat():
    """
    Тестовый endpoint для проверки работы чата.
    
    Returns:
        Тестовый ответ
    """
    try:
        service = await get_ollama_service()
        
        if not await service.check_connection():
            raise HTTPException(
                status_code=503,
                detail="Ollama сервис недоступен"
            )
        
        # Генерируем тестовый ответ
        result = await service.generate_response(
            "Привет! Как дела?",
            "",
            100,
            0.7
        )
        
        return {
            "test": True,
            "response": result["response"],
            "model": result["model"],
            "timestamp": result["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Ошибка тестирования: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 