"""
Основной модуль FastAPI приложения для системы цифрового аватара.

Содержит настройку приложения, middleware, CORS, роутеры и WebSocket соединения.

Автор: Авабот
Версия: 1.0.0
"""

import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import json

from .config import settings
from .routers import api_router
from .services.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

# Менеджер WebSocket соединений
websocket_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для жизненного цикла приложения.
    
    Инициализирует ресурсы при запуске и очищает их при завершении.
    """
    # Startup
    logger.info("Запуск приложения цифрового аватара v1.0.0")
    
    # Проверка доступности GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"GPU доступен: {gpu_name}, память: {gpu_memory} ГБ")
        else:
            logger.warning("GPU недоступен, будет использоваться CPU")
    except ImportError:
        logger.warning("PyTorch не установлен")
    
    # Проверка Redis
    try:
        import redis
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        logger.info("Redis подключение установлено")
    except Exception as e:
        logger.error(f"Ошибка подключения к Redis: {e}")
    
    yield
    
    # Shutdown
    logger.info("Завершение работы приложения")
    
    # Очистка GPU памяти
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("GPU память очищена")
    except ImportError:
        pass


# Создание FastAPI приложения
app = FastAPI(
    title="Цифровой Аватар API",
    description="API для системы цифрового аватара с клонированием голоса и ИИ-общением",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка Trusted Hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# Модели для API
class HealthResponse(BaseModel):
    """Модель ответа для health check."""
    status: str
    version: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Модель ответа для ошибок."""
    error: str
    detail: str
    timestamp: str


# Обработчики ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик исключений."""
    logger.error(f"Необработанное исключение: {exc}, path: {request.url.path}, method: {request.method}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Внутренняя ошибка сервера",
            "detail": str(exc) if settings.DEBUG else "Произошла ошибка при обработке запроса",
            "timestamp": datetime.now().isoformat()
        }
    )


# Основные endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Корневой endpoint с информацией о приложении."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint для real-time коммуникации.
    
    Args:
        websocket: WebSocket соединение
        client_id: Уникальный идентификатор клиента
    """
    await websocket_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Получение сообщения от клиента
            data = await websocket.receive_text()
            logger.info(f"Получено WebSocket сообщение от {client_id}: {data}")
            
            # Обработка сообщения (здесь будет логика AI)
            response = await process_websocket_message(client_id, data)
            
            # Отправка ответа клиенту
            await websocket_manager.send_personal_message(response, client_id)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket соединение закрыто: {client_id}")
        websocket_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Ошибка в WebSocket {client_id}: {e}")
        websocket_manager.disconnect(client_id)


# Простой WebSocket endpoint без client_id
@app.websocket("/ws")
async def simple_websocket_endpoint(websocket: WebSocket):
    """
    Простой WebSocket endpoint для совместимости с frontend.
    
    Args:
        websocket: WebSocket соединение
    """
    client_id = f"client_{len(websocket_manager.active_connections)}"
    await websocket_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Получение сообщения от клиента
            data = await websocket.receive_text()
            logger.info(f"Получено WebSocket сообщение: {data}")
            
            # Обработка сообщения (здесь будет логика AI)
            response = await process_websocket_message(client_id, data)
            
            # Отправка ответа клиенту
            await websocket_manager.send_personal_message(response, client_id)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket соединение закрыто: {client_id}")
        websocket_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Ошибка в WebSocket: {e}")
        websocket_manager.disconnect(client_id)


async def process_websocket_message(client_id: str, message: str) -> str:
    """
    Обработка WebSocket сообщений.
    
    Args:
        client_id: Идентификатор клиента
        message: Сообщение от клиента
        
    Returns:
        Ответ для клиента (JSON-строка)
    """
    # TODO: Интеграция с AI пайплайном
    # 1. Распознавание речи (Whisper)
    # 2. Генерация ответа (Ollama + Llama)
    # 3. Синтез речи (Coqui TTS)
    # 4. Анимация лица (SadTalker)

    response = {
        "type": "pong",
        "message": f"Получено сообщение: {message}"
    }
    return json.dumps(response, ensure_ascii=False)


# Подключение API роутеров
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 