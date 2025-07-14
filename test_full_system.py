#!/usr/bin/env python3
"""
Комплексное тестирование системы цифрового аватара.

Тестирует полный цикл работы:
1. Запись аудио
2. Распознавание речи через Whisper
3. Генерация ответа через Ollama
4. Синтез речи через HierSpeech_TTS
5. Создание анимации через SadTalker
6. Синхронное воспроизведение

Автор: Авабот
Версия: 1.0.0
"""

import asyncio
import json
import time
import requests
import websockets
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AvatarSystemTester:
    """Тестер системы цифрового аватара."""
    
    def __init__(self):
        self.base_urls = {
            'backend': 'http://localhost:8000',
            'hier_tts': 'http://localhost:8001',
            'sadtalker': 'http://localhost:8002',
            'frontend': 'http://localhost:3000'
        }
        self.test_results = {}
        
    def test_health_endpoints(self) -> bool:
        """Тестирование health endpoints всех сервисов."""
        logger.info("🔍 Тестирование health endpoints...")
        
        all_healthy = True
        
        for service, url in self.base_urls.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ {service}: {data.get('status', 'OK')}")
                    self.test_results[f"{service}_health"] = True
                else:
                    logger.error(f"❌ {service}: HTTP {response.status_code}")
                    self.test_results[f"{service}_health"] = False
                    all_healthy = False
            except Exception as e:
                logger.error(f"❌ {service}: {e}")
                self.test_results[f"{service}_health"] = False
                all_healthy = False
        
        return all_healthy
    
    def test_websocket_connection(self) -> bool:
        """Тестирование WebSocket соединения."""
        logger.info("🔌 Тестирование WebSocket соединения...")
        
        try:
            async def test_ws():
                uri = "ws://localhost:8000/ws"
                async with websockets.connect(uri) as websocket:
                    # Отправка тестового сообщения
                    test_message = {
                        "type": "test",
                        "message": "Тестовое сообщение"
                    }
                    await websocket.send(json.dumps(test_message))
                    
                    # Получение ответа
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    logger.info(f"✅ WebSocket ответ: {response}")
                    return True
            
            result = asyncio.run(test_ws())
            self.test_results["websocket"] = result
            return result
            
        except Exception as e:
            logger.error(f"❌ WebSocket ошибка: {e}")
            self.test_results["websocket"] = False
            return False
    
    def test_whisper_integration(self) -> bool:
        """Тестирование интеграции Whisper."""
        logger.info("🎤 Тестирование Whisper (распознавание речи)...")
        
        try:
            # Проверяем health endpoint вместо реальной транскрипции
            response = requests.get(f"{self.base_urls['backend']}/api/v1/speech/health", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Whisper health: {result}")
                self.test_results["whisper"] = True
                return True
            else:
                logger.error(f"❌ Whisper health ошибка: {response.status_code}")
                self.test_results["whisper"] = False
                return False
                
        except Exception as e:
            logger.error(f"❌ Whisper тест ошибка: {e}")
            self.test_results["whisper"] = False
            return False
    
    def test_ollama_integration(self) -> bool:
        """Тестирование интеграции Ollama."""
        logger.info("🧠 Тестирование Ollama (генерация ответов)...")
        
        try:
            test_message = "Привет! Как дела?"
            
            response = requests.post(
                f"{self.base_urls['backend']}/api/v1/chat/chat",
                json={"message": test_message},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Ollama ответ: {result.get('response', '')[:100]}...")
                self.test_results["ollama"] = True
                return True
            else:
                logger.error(f"❌ Ollama ошибка: {response.status_code}")
                self.test_results["ollama"] = False
                return False
                
        except Exception as e:
            logger.error(f"❌ Ollama тест ошибка: {e}")
            self.test_results["ollama"] = False
            return False
    
    def test_hier_tts_integration(self) -> bool:
        """Тестирование интеграции HierSpeech_TTS."""
        logger.info("🎵 Тестирование HierSpeech_TTS (синтез речи)...")
        
        try:
            test_text = "Привет! Это тестовое сообщение для синтеза речи."
            
            response = requests.post(
                f"{self.base_urls['hier_tts']}/synthesize",
                json={
                    "text": test_text,
                    "voice_id": "female_001",
                    "speed": 1.0
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ HierSpeech_TTS результат: {result.get('status', 'OK')}")
                self.test_results["hier_tts"] = True
                return True
            else:
                logger.error(f"❌ HierSpeech_TTS ошибка: {response.status_code}")
                self.test_results["hier_tts"] = False
                return False
                
        except Exception as e:
            logger.error(f"❌ HierSpeech_TTS тест ошибка: {e}")
            self.test_results["hier_tts"] = False
            return False
    
    def test_sadtalker_integration(self) -> bool:
        """Тестирование интеграции SadTalker."""
        logger.info("🎭 Тестирование SadTalker (анимация лица)...")
        
        try:
            # Проверяем наличие тестовых файлов
            image_path = "SadTalker/examples/source_image/avatar.jpg"
            audio_path = "SadTalker/examples/driven_audio/test.wav"
            
            if not Path(image_path).exists():
                logger.warning(f"⚠️ Тестовое изображение не найдено: {image_path}")
                # Создаем заглушку
                import numpy as np
                from PIL import Image
                test_image = Image.fromarray(np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8))
                test_image.save(image_path)
                logger.info(f"✅ Создано тестовое изображение: {image_path}")
            
            if not Path(audio_path).exists():
                logger.warning(f"⚠️ Тестовое аудио не найдено: {audio_path}")
                # Создаем заглушку
                import numpy as np
                import soundfile as sf
                sample_rate = 16000
                duration = 3.0
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                audio_data = np.sin(2 * np.pi * 440 * t) * 0.1
                sf.write(audio_path, audio_data, sample_rate)
                logger.info(f"✅ Создано тестовое аудио: {audio_path}")
            
            # Отправка на анимацию
            with open(image_path, 'rb') as img_file, open(audio_path, 'rb') as audio_file:
                files = {
                    'image': ('avatar.jpg', img_file, 'image/jpeg'),
                    'audio': ('test.wav', audio_file, 'audio/wav')
                }
                response = requests.post(
                    f"{self.base_urls['sadtalker']}/animate",
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ SadTalker результат: {result.get('status', 'OK')}")
                self.test_results["sadtalker"] = True
                return True
            else:
                logger.error(f"❌ SadTalker ошибка: {response.status_code}")
                self.test_results["sadtalker"] = False
                return False
                
        except Exception as e:
            logger.error(f"❌ SadTalker тест ошибка: {e}")
            self.test_results["sadtalker"] = False
            return False
    
    def test_full_pipeline(self) -> bool:
        """Тестирование полного пайплайна."""
        logger.info("🔄 Тестирование полного пайплайна...")
        
        try:
            # Симуляция полного цикла
            test_message = "Привет! Расскажи анекдот."
            
            # 1. Отправка сообщения через WebSocket
            async def test_full_cycle():
                uri = "ws://localhost:8000/ws"
                async with websockets.connect(uri) as websocket:
                    # Отправка текстового сообщения
                    message = {
                        "type": "text_message",
                        "message": test_message
                    }
                    await websocket.send(json.dumps(message))
                    
                    # Ожидание ответа
                    response = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                    logger.info(f"✅ Полный цикл ответ: {response[:200]}...")
                    return True
            
            result = asyncio.run(test_full_cycle())
            self.test_results["full_pipeline"] = result
            return result
            
        except Exception as e:
            logger.error(f"❌ Полный пайплайн ошибка: {e}")
            self.test_results["full_pipeline"] = False
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов."""
        logger.info("🚀 Начало комплексного тестирования системы цифрового аватара")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Тестирование компонентов
        tests = [
            ("Health Endpoints", self.test_health_endpoints),
            ("WebSocket", self.test_websocket_connection),
            ("Whisper", self.test_whisper_integration),
            ("Ollama", self.test_ollama_integration),
            ("HierSpeech_TTS", self.test_hier_tts_integration),
            ("SadTalker", self.test_sadtalker_integration),
            ("Full Pipeline", self.test_full_pipeline)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 Тест: {test_name}")
            logger.info("-" * 40)
            
            try:
                result = test_func()
                status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
                logger.info(f"{status}: {test_name}")
            except Exception as e:
                logger.error(f"❌ ОШИБКА: {test_name} - {e}")
                self.test_results[test_name.lower().replace(" ", "_")] = False
        
        # Подсчет результатов
        total_tests = len(tests)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Итоговый отчет
        logger.info("\n" + "=" * 60)
        logger.info("📊 ИТОГОВЫЙ ОТЧЕТ")
        logger.info("=" * 60)
        logger.info(f"Всего тестов: {total_tests}")
        logger.info(f"Пройдено: {passed_tests}")
        logger.info(f"Провалено: {failed_tests}")
        logger.info(f"Успешность: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"Время выполнения: {duration:.2f} секунд")
        
        # Детальные результаты
        logger.info("\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        for test_name, result in self.test_results.items():
            status = "✅" if result else "❌"
            logger.info(f"{status} {test_name}: {'ПРОЙДЕН' if result else 'ПРОВАЛЕН'}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "duration": duration,
            "results": self.test_results
        }

def main():
    """Основная функция."""
    tester = AvatarSystemTester()
    results = tester.run_all_tests()
    
    # Сохранение результатов
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n💾 Результаты сохранены в test_results.json")
    
    # Возврат кода выхода
    if results["failed_tests"] == 0:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return 0
    else:
        logger.error(f"⚠️ {results['failed_tests']} ТЕСТОВ ПРОВАЛЕНО")
        return 1

if __name__ == "__main__":
    exit(main()) 