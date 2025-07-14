"""
Сервис для интеграции с HierSpeech_TTS API
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger(__name__)

class HierTTSService:
    """Сервис для работы с HierSpeech_TTS API"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:8001"):
        self.api_url = api_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        if self.session:
            await self.session.close()
    
    async def check_health(self) -> Dict[str, Any]:
        """Проверка состояния API сервера"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/health") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Health check failed: {response.status}")
                        return {"status": "error", "code": response.status}
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def synthesize_speech(
        self, 
        text: str, 
        language: str = "ru",
        reference_audio_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Синтез речи через HierSpeech_TTS API
        
        Args:
            text: Текст для синтеза
            language: Язык (ru/en)
            reference_audio_path: Путь к референсному аудио
            
        Returns:
            Путь к сгенерированному аудиофайлу или None при ошибке
        """
        try:
            # Подготавливаем данные запроса
            payload = {
                "text": text,
                "language": language
            }
            
            if reference_audio_path:
                payload["reference_audio_path"] = reference_audio_path
            
            # Отправляем запрос на синтез
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/synthesize",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        audio_path = result.get("audio_path")
                        
                        if audio_path:
                            # Копируем файл в локальную директорию
                            local_path = await self._copy_audio_file(audio_path)
                            logger.info(f"Синтез речи успешен: {local_path}")
                            return local_path
                        else:
                            logger.error("API не вернул путь к аудиофайлу")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка синтеза речи: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Ошибка синтеза речи: {e}")
            return None
    
    async def _copy_audio_file(self, remote_path: str) -> str:
        """
        Копирует аудиофайл с API сервера в локальную директорию
        
        Args:
            remote_path: Путь к файлу на API сервере
            
        Returns:
            Локальный путь к скопированному файлу
        """
        try:
            # Извлекаем имя файла из пути
            filename = Path(remote_path).name
            
            # Создаём локальную директорию для аудио
            local_dir = Path("temp_audio")
            local_dir.mkdir(exist_ok=True)
            
            local_path = local_dir / filename
            
            # Скачиваем файл с API сервера
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/audio/{filename}") as response:
                    if response.status == 200:
                        with open(local_path, "wb") as f:
                            f.write(await response.read())
                        return str(local_path)
                    else:
                        logger.error(f"Ошибка скачивания файла: {response.status}")
                        return remote_path  # Возвращаем оригинальный путь как fallback
                        
        except Exception as e:
            logger.error(f"Ошибка копирования файла: {e}")
            return remote_path  # Возвращаем оригинальный путь как fallback
    
    async def upload_reference_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Загружает референсное аудио на API сервер
        
        Args:
            audio_file_path: Путь к аудиофайлу
            
        Returns:
            Путь к файлу на сервере или None при ошибке
        """
        try:
            async with aiohttp.ClientSession() as session:
                with open(audio_file_path, "rb") as f:
                    data = aiohttp.FormData()
                    data.add_field(
                        "file",
                        f,
                        filename=Path(audio_file_path).name,
                        content_type="audio/wav"
                    )
                    
                    async with session.post(
                        f"{self.api_url}/upload_reference",
                        data=data
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            return result.get("file_path")
                        else:
                            error_text = await response.text()
                            logger.error(f"Ошибка загрузки файла: {response.status} - {error_text}")
                            return None
                            
        except Exception as e:
            logger.error(f"Ошибка загрузки референсного аудио: {e}")
            return None

# Глобальный экземпляр сервиса
hier_tts_service = HierTTSService()

async def get_hier_tts_service() -> HierTTSService:
    """Получение экземпляра сервиса HierSpeech_TTS"""
    return hier_tts_service 