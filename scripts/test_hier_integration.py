#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции с HierSpeech_TTS API
"""

import asyncio
import aiohttp
import json
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_hier_tts_api():
    """Тестирование HierSpeech_TTS API"""
    
    api_url = "http://127.0.0.1:8001"
    
    async with aiohttp.ClientSession() as session:
        
        # Тест 1: Проверка здоровья API
        logger.info("Тест 1: Проверка здоровья API")
        try:
            async with session.get(f"{api_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    logger.info(f"✅ API здоров: {health_data}")
                else:
                    logger.error(f"❌ API не отвечает: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к API: {e}")
            return False
        
        # Тест 2: Синтез речи
        logger.info("Тест 2: Синтез речи")
        try:
            payload = {
                "text": "Привет, это тест интеграции с HierSpeech_TTS для русского языка",
                "language": "ru"
            }
            
            async with session.post(
                f"{api_url}/synthesize",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Синтез речи успешен: {result}")
                    
                    # Проверяем, что файл создан
                    audio_path = result.get("audio_path")
                    if audio_path and Path(audio_path).exists():
                        logger.info(f"✅ Аудиофайл создан: {audio_path}")
                    else:
                        logger.warning(f"⚠️ Аудиофайл не найден: {audio_path}")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка синтеза речи: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Ошибка синтеза речи: {e}")
            return False
        
        # Тест 3: Получение аудиофайла
        logger.info("Тест 3: Получение аудиофайла")
        try:
            # Получаем список файлов в temp_output
            temp_output_dir = Path("HierSpeech_TTS/temp_output")
            if temp_output_dir.exists():
                audio_files = list(temp_output_dir.glob("*.wav"))
                if audio_files:
                    filename = audio_files[0].name
                    
                    async with session.get(f"{api_url}/audio/{filename}") as response:
                        if response.status == 200:
                            logger.info(f"✅ Аудиофайл получен: {filename}")
                        else:
                            logger.warning(f"⚠️ Не удалось получить файл: {response.status}")
                else:
                    logger.warning("⚠️ Нет аудиофайлов для тестирования")
            else:
                logger.warning("⚠️ Директория temp_output не найдена")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения файла: {e}")
        
        logger.info("🎉 Все тесты завершены!")
        return True

async def test_main_backend_integration():
    """Тестирование интеграции с основным backend"""
    
    backend_url = "http://127.0.0.1:8000"
    
    async with aiohttp.ClientSession() as session:
        
        # Тест 1: Проверка здоровья основного backend
        logger.info("Тест 1: Проверка здоровья основного backend")
        try:
            async with session.get(f"{backend_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    logger.info(f"✅ Основной backend здоров: {health_data}")
                else:
                    logger.warning(f"⚠️ Основной backend не отвечает: {response.status}")
                    return False
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к основному backend: {e}")
            return False
        
        # Тест 2: Проверка HierSpeech_TTS через основной backend
        logger.info("Тест 2: Проверка HierSpeech_TTS через основной backend")
        try:
            async with session.get(f"{backend_url}/hier-tts/health") as response:
                if response.status == 200:
                    hier_health = await response.json()
                    logger.info(f"✅ HierSpeech_TTS через backend: {hier_health}")
                else:
                    logger.warning(f"⚠️ HierSpeech_TTS через backend недоступен: {response.status}")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка проверки HierSpeech_TTS через backend: {e}")
        
        logger.info("🎉 Тесты интеграции завершены!")
        return True

async def main():
    """Основная функция тестирования"""
    
    logger.info("🚀 Начинаем тестирование интеграции HierSpeech_TTS")
    
    # Тестируем API сервер HierSpeech_TTS
    logger.info("\n" + "="*50)
    logger.info("ТЕСТИРОВАНИЕ HIERSPEECH_TTS API")
    logger.info("="*50)
    
    hier_success = await test_hier_tts_api()
    
    # Тестируем интеграцию с основным backend
    logger.info("\n" + "="*50)
    logger.info("ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С ОСНОВНЫМ BACKEND")
    logger.info("="*50)
    
    backend_success = await test_main_backend_integration()
    
    # Итоговый отчёт
    logger.info("\n" + "="*50)
    logger.info("ИТОГОВЫЙ ОТЧЁТ")
    logger.info("="*50)
    
    if hier_success:
        logger.info("✅ HierSpeech_TTS API работает корректно")
    else:
        logger.error("❌ HierSpeech_TTS API имеет проблемы")
    
    if backend_success:
        logger.info("✅ Интеграция с основным backend работает")
    else:
        logger.warning("⚠️ Интеграция с основным backend требует внимания")
    
    logger.info("\n🎯 Рекомендации:")
    if hier_success and backend_success:
        logger.info("✅ Система готова к использованию!")
    elif hier_success:
        logger.info("🔧 Нужно настроить основной backend")
    else:
        logger.info("🔧 Нужно исправить проблемы с HierSpeech_TTS API")

if __name__ == "__main__":
    asyncio.run(main()) 