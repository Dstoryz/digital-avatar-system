"""
Сервис для ИИ-общения с помощью Ollama.

Обеспечивает генерацию ответов на русском языке с помощью локальных языковых моделей.

Автор: Авабот
Версия: 1.0.0
"""

import logging
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OllamaService:
    """Сервис для работы с Ollama."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        """
        Инициализация Ollama сервиса.
        
        Args:
            base_url: URL Ollama сервера
            model: Название модели
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = None
        self.conversation_history: List[Dict[str, str]] = []
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение HTTP сессии."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def check_connection(self) -> bool:
        """
        Проверка подключения к Ollama.
        
        Returns:
            True если подключение работает
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Ошибка подключения к Ollama: {e}")
            return False
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Получение списка доступных моделей.
        
        Returns:
            Список моделей
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("models", [])
                else:
                    logger.error(f"Ошибка получения моделей: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Ошибка получения моделей: {e}")
            return []
    
    async def generate_response(
        self, 
        prompt: str, 
        context: str = "", 
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Генерация ответа на основе промпта.
        
        Args:
            prompt: Входной текст
            context: Контекст разговора
            max_tokens: Максимальное количество токенов
            temperature: Температура генерации
            
        Returns:
            Сгенерированный ответ
        """
        try:
            # Формируем полный промпт с контекстом
            full_prompt = self._build_prompt(prompt, context)
            
            session = await self._get_session()
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Сохраняем в историю
                    self.conversation_history.append({
                        "user": prompt,
                        "assistant": data.get("response", ""),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    return {
                        "response": data.get("response", ""),
                        "model": self.model,
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "response_tokens": data.get("eval_count", 0),
                        "total_duration": data.get("total_duration", 0),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка генерации: {response.status} - {error_text}")
                    raise Exception(f"Ошибка генерации: {response.status}")
                    
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            raise
    
    def _build_prompt(self, prompt: str, context: str = "") -> str:
        """
        Построение полного промпта с контекстом.
        
        Args:
            prompt: Основной промпт
            context: Контекст разговора
            
        Returns:
            Полный промпт
        """
        system_prompt = """Ты - дружелюбный и полезный ассистент. Отвечай на русском языке.
Будь вежливым, понимающим и старайся давать полезные ответы.
Если не знаешь ответа, честно скажи об этом."""
        
        # Добавляем контекст разговора
        conversation_context = ""
        if self.conversation_history:
            recent_history = self.conversation_history[-5:]  # Последние 5 обменов
            for exchange in recent_history:
                conversation_context += f"Пользователь: {exchange['user']}\n"
                conversation_context += f"Ассистент: {exchange['assistant']}\n"
        
        # Собираем полный промпт
        full_prompt = f"{system_prompt}\n\n"
        
        if context:
            full_prompt += f"Контекст: {context}\n\n"
        
        if conversation_context:
            full_prompt += f"История разговора:\n{conversation_context}\n"
        
        full_prompt += f"Пользователь: {prompt}\nАссистент:"
        
        return full_prompt
    
    def add_to_history(self, user_message: str, assistant_message: str):
        """
        Добавление сообщения в историю разговора.
        
        Args:
            user_message: Сообщение пользователя
            assistant_message: Ответ ассистента
        """
        self.conversation_history.append({
            "user": user_message,
            "assistant": assistant_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Ограничиваем историю последними 20 сообщениями
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Получение истории разговора."""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Очистка истории разговора."""
        self.conversation_history.clear()
    
    async def close(self):
        """Закрытие сессии."""
        if self.session and not self.session.closed:
            await self.session.close()


# Глобальный экземпляр сервиса
ollama_service = None


async def get_ollama_service(model: str = "llama3.2:3b") -> OllamaService:
    """
    Получение глобального экземпляра Ollama сервиса.
    
    Args:
        model: Название модели
        
    Returns:
        Экземпляр OllamaService
    """
    global ollama_service
    
    if ollama_service is None or ollama_service.model != model:
        if ollama_service:
            await ollama_service.close()
        ollama_service = OllamaService(model=model)
    
    return ollama_service


async def generate_ai_response(
    prompt: str, 
    context: str = "", 
    model: str = "llama3.2:3b"
) -> Dict[str, Any]:
    """
    Удобная функция для генерации ответа.
    
    Args:
        prompt: Входной текст
        context: Контекст
        model: Модель
        
    Returns:
        Сгенерированный ответ
    """
    service = await get_ollama_service(model)
    return await service.generate_response(prompt, context)


if __name__ == "__main__":
    # Тестирование сервиса
    async def test():
        service = OllamaService()
        
        # Проверяем подключение
        if await service.check_connection():
            print("✅ Подключение к Ollama работает")
            
            # Получаем модели
            models = await service.get_available_models()
            print(f"Доступные модели: {[m['name'] for m in models]}")
            
            # Тестируем генерацию
            try:
                response = await service.generate_response("Привет! Как дела?")
                print(f"Ответ: {response['response']}")
            except Exception as e:
                print(f"Ошибка генерации: {e}")
        else:
            print("❌ Не удалось подключиться к Ollama")
        
        await service.close()
    
    asyncio.run(test()) 