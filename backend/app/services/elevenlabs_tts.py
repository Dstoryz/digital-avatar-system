"""
Сервис для интеграции ElevenLabs TTS в backend.

Предоставляет функции для клонирования голоса и синтеза русской речи.

Автор: AI Assistant
Версия: 1.0.0
"""

import os
import requests
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ElevenLabsTTSService:
    """Сервис для работы с ElevenLabs TTS."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация сервиса.
        
        Args:
            api_key: API ключ ElevenLabs
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            logger.warning("ElevenLabs API ключ не установлен")
            logger.info("Установите переменную окружения ELEVENLABS_API_KEY")
        
        logger.info("ElevenLabs TTS сервис инициализирован")
    
    async def clone_voice(self, voice_name: str, audio_file_path: str) -> Dict[str, Any]:
        """
        Клонирование голоса из аудиофайла.
        
        Args:
            voice_name: Название для нового голоса
            audio_file_path: Путь к аудиофайлу
            
        Returns:
            Результат клонирования
        """
        if not self.api_key:
            return {"error": "API ключ не установлен"}
        
        if not os.path.exists(audio_file_path):
            return {"error": f"Аудиофайл не найден: {audio_file_path}"}
        
        try:
            with open(audio_file_path, 'rb') as f:
                files = {'files': f}
                data = {
                    'name': voice_name,
                    'description': f'Клонированный голос из {audio_file_path}'
                }
                
                response = requests.post(
                    f"{self.base_url}/voices/add",
                    headers={"xi-api-key": self.api_key},
                    data=data,
                    files=files
                )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Голос '{voice_name}' успешно клонирован")
                return result
            else:
                logger.error(f"Ошибка клонирования: {response.status_code} - {response.text}")
                return {"error": f"Ошибка клонирования: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Ошибка клонирования голоса: {e}")
            return {"error": str(e)}
    
    async def synthesize_speech(self, text: str, voice_id: str, output_path: str) -> Dict[str, Any]:
        """
        Синтез речи с клонированным голосом.
        
        Args:
            text: Текст для синтеза (поддерживает русский)
            voice_id: ID клонированного голоса
            output_path: Путь для сохранения аудио
            
        Returns:
            Результат синтеза
        """
        if not self.api_key:
            return {"error": "API ключ не установлен"}
        
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # Поддерживает русский
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(
                url,
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            if response.status_code == 200:
                # Создаем директорию если не существует
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Сохранение аудио
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Речь синтезирована и сохранена: {output_path}")
                return {"success": True, "output_path": output_path}
            else:
                logger.error(f"Ошибка синтеза: {response.status_code} - {response.text}")
                return {"error": f"Ошибка синтеза: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Ошибка синтеза речи: {e}")
            return {"error": str(e)}
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Получение списка доступных голосов."""
        if not self.api_key:
            return {"error": "API ключ не установлен"}
        
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers={"xi-api-key": self.api_key}
            )
            
            if response.status_code == 200:
                voices = response.json()
                logger.info(f"Найдено {len(voices.get('voices', []))} голосов")
                return voices
            else:
                logger.error(f"Ошибка получения голосов: {response.status_code}")
                return {"error": f"Ошибка API: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Ошибка получения голосов: {e}")
            return {"error": str(e)}
    
    async def delete_voice(self, voice_id: str) -> Dict[str, Any]:
        """Удаление клонированного голоса."""
        if not self.api_key:
            return {"error": "API ключ не установлен"}
        
        try:
            response = requests.delete(
                f"{self.base_url}/voices/{voice_id}",
                headers={"xi-api-key": self.api_key}
            )
            
            if response.status_code == 200:
                logger.info(f"Голос {voice_id} успешно удален")
                return {"success": True}
            else:
                logger.error(f"Ошибка удаления голоса: {response.status_code}")
                return {"error": f"Ошибка удаления: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Ошибка удаления голоса: {e}")
            return {"error": str(e)}
    
    def is_available(self) -> bool:
        """Проверка доступности сервиса."""
        return self.api_key is not None

# Создание глобального экземпляра сервиса
elevenlabs_tts_service = ElevenLabsTTSService() 