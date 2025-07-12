"""
WebSocket менеджер для управления соединениями клиентов.

Обеспечивает подключение, отключение и отправку сообщений клиентам.

Автор: Авабот
Версия: 1.0.0
"""

import json
from typing import Dict, List

import structlog
from fastapi import WebSocket

logger = structlog.get_logger(__name__)


class WebSocketManager:
    """Менеджер WebSocket соединений."""
    
    def __init__(self):
        """Инициализация менеджера."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_info: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Подключение клиента.
        
        Args:
            websocket: WebSocket соединение
            client_id: Уникальный идентификатор клиента
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_info[client_id] = {
            "connected_at": structlog.processors.TimeStamper(fmt="iso")(),
            "status": "connected"
        }
        
        logger.info("Клиент подключен", client_id=client_id)
    
    def disconnect(self, client_id: str):
        """
        Отключение клиента.
        
        Args:
            client_id: Уникальный идентификатор клиента
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
        if client_id in self.connection_info:
            self.connection_info[client_id]["status"] = "disconnected"
            self.connection_info[client_id]["disconnected_at"] = structlog.processors.TimeStamper(fmt="iso")()
        
        logger.info("Клиент отключен", client_id=client_id)
    
    async def send_personal_message(self, message: str, client_id: str):
        """
        Отправка персонального сообщения клиенту.
        
        Args:
            message: Сообщение для отправки
            client_id: Идентификатор клиента
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
                logger.debug("Сообщение отправлено", client_id=client_id, message=message)
            except Exception as e:
                logger.error("Ошибка отправки сообщения", client_id=client_id, error=str(e))
                self.disconnect(client_id)
    
    async def send_json_message(self, data: dict, client_id: str):
        """
        Отправка JSON сообщения клиенту.
        
        Args:
            data: Данные для отправки
            client_id: Идентификатор клиента
        """
        message = json.dumps(data, ensure_ascii=False)
        await self.send_personal_message(message, client_id)
    
    async def broadcast(self, message: str):
        """
        Отправка сообщения всем подключенным клиентам.
        
        Args:
            message: Сообщение для отправки
        """
        disconnected_clients = []
        
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
                logger.debug("Broadcast сообщение отправлено", client_id=client_id)
            except Exception as e:
                logger.error("Ошибка broadcast", client_id=client_id, error=str(e))
                disconnected_clients.append(client_id)
        
        # Удаление отключенных клиентов
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    def get_connected_clients(self) -> List[str]:
        """
        Получение списка подключенных клиентов.
        
        Returns:
            Список идентификаторов клиентов
        """
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """
        Получение количества активных соединений.
        
        Returns:
            Количество активных соединений
        """
        return len(self.active_connections)
    
    def get_connection_info(self, client_id: str) -> Dict:
        """
        Получение информации о соединении клиента.
        
        Args:
            client_id: Идентификатор клиента
            
        Returns:
            Информация о соединении
        """
        return self.connection_info.get(client_id, {}) 