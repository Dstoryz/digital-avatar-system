#!/usr/bin/env python3
"""
Комплексный тест системы цифрового аватара.

Тестирует все компоненты:
1. Backend (FastAPI) - порт 8000
2. HierSpeech_TTS - порт 8001  
3. SadTalker - порт 8002
4. Frontend - порт 3001
5. WebSocket соединения
6. Аудио синтез и воспроизведение

Автор: Авабот
Версия: 1.0.0
"""

import asyncio
import aiohttp
import json
import time
import requests
from typing import Dict, List, Any
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AvatarSystemTester:
    """Тестер системы цифрового аватара."""
    
    def __init__(self):
        """Инициализация тестера."""
        self.base_urls = {
            'backend': 'http://127.0.0.1:8000',
            'hier_tts': 'http://127.0.0.1:8001',
            'sadtalker': 'http://127.0.0.1:8002',
            'frontend': 'http://127.0.0.1:3001'
        }
        self.results = {}
        
    async def test_backend(self) -> Dict[str, Any]:
        """Тест backend API."""
        logger.info("🔧 Тестирование Backend API...")
        
        try:
            # Health check
            response = await self._make_request(f"{self.base_urls['backend']}/health")
            if response and response.get('status') == 'healthy':
                logger.info("✅ Backend API работает")
                return {'status': 'success', 'message': 'Backend API работает'}
            else:
                logger.error("❌ Backend API не отвечает")
                return {'status': 'error', 'message': 'Backend API не отвечает'}
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования Backend: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def test_hier_tts(self) -> Dict[str, Any]:
        """Тест HierSpeech_TTS."""
        logger.info("🎤 Тестирование HierSpeech_TTS...")
        
        try:
            # Health check
            response = await self._make_request(f"{self.base_urls['hier_tts']}/health")
            if response and response.get('status') == 'healthy':
                logger.info("✅ HierSpeech_TTS работает")
                return {'status': 'success', 'message': 'HierSpeech_TTS работает'}
            else:
                logger.error("❌ HierSpeech_TTS не отвечает")
                return {'status': 'error', 'message': 'HierSpeech_TTS не отвечает'}
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования HierSpeech_TTS: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def test_sadtalker(self) -> Dict[str, Any]:
        """Тест SadTalker."""
        logger.info("🎭 Тестирование SadTalker...")
        
        try:
            # Health check
            response = await self._make_request(f"{self.base_urls['sadtalker']}/health")
            if response and response.get('status') == 'healthy':
                logger.info("✅ SadTalker работает")
                return {'status': 'success', 'message': 'SadTalker работает'}
            else:
                logger.error("❌ SadTalker не отвечает")
                return {'status': 'error', 'message': 'SadTalker не отвечает'}
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования SadTalker: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def test_frontend(self) -> Dict[str, Any]:
        """Тест Frontend."""
        logger.info("🌐 Тестирование Frontend...")
        
        try:
            # Проверка доступности
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_urls['frontend']) as response:
                    if response.status == 200:
                        logger.info("✅ Frontend доступен")
                        return {'status': 'success', 'message': 'Frontend доступен'}
                    else:
                        logger.error(f"❌ Frontend недоступен: {response.status}")
                        return {'status': 'error', 'message': f'Frontend недоступен: {response.status}'}
                        
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования Frontend: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def test_websocket(self) -> Dict[str, Any]:
        """Тест WebSocket соединения."""
        logger.info("🔌 Тестирование WebSocket...")
        
        try:
            import websockets
            
            uri = "ws://127.0.0.1:8000/ws"
            async with websockets.connect(uri) as websocket:
                # Отправка тестового сообщения
                test_message = json.dumps({
                    'type': 'test',
                    'message': 'Hello from tester'
                })
                await websocket.send(test_message)
                
                # Получение ответа
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                logger.info("✅ WebSocket соединение работает")
                return {'status': 'success', 'message': 'WebSocket соединение работает'}
                
        except Exception as e:
            logger.error(f"❌ Ошибка WebSocket: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def test_audio_synthesis(self) -> Dict[str, Any]:
        """Тест синтеза речи."""
        logger.info("🎵 Тестирование синтеза речи...")
        
        try:
            # Тестовый текст
            test_text = "Привет! Это тест синтеза речи."
            
            # Запрос на синтез
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_urls['hier_tts']}/synthesize",
                    json={
                        'text': test_text,
                        'language': 'ru',
                        'reference_audio': 'default'
                    }
                ) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        if len(audio_data) > 0:
                            logger.info("✅ Синтез речи работает")
                            return {'status': 'success', 'message': 'Синтез речи работает'}
                        else:
                            logger.error("❌ Пустой аудио ответ")
                            return {'status': 'error', 'message': 'Пустой аудио ответ'}
                    else:
                        logger.error(f"❌ Ошибка синтеза речи: {response.status}")
                        return {'status': 'error', 'message': f'Ошибка синтеза речи: {response.status}'}
                        
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования синтеза речи: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def test_ai_chat(self) -> Dict[str, Any]:
        """Тест AI чата."""
        logger.info("🧠 Тестирование AI чата...")
        
        try:
            # Тестовое сообщение
            test_message = "Привет! Как дела?"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_urls['backend']}/api/v1/chat/chat",
                    json={
                        'message': test_message,
                        'model': 'llama3.2:3b',
                        'max_tokens': 100,
                        'temperature': 0.7
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'response' in result and len(result['response']) > 0:
                            logger.info("✅ AI чат работает")
                            return {'status': 'success', 'message': 'AI чат работает'}
                        else:
                            logger.error("❌ Пустой ответ от AI")
                            return {'status': 'error', 'message': 'Пустой ответ от AI'}
                    else:
                        logger.error(f"❌ Ошибка AI чата: {response.status}")
                        return {'status': 'error', 'message': f'Ошибка AI чата: {response.status}'}
                        
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования AI чата: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _make_request(self, url: str) -> Dict[str, Any]:
        """Выполнение HTTP запроса."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
        except Exception:
            return None
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов."""
        logger.info("🚀 Запуск комплексного тестирования системы...")
        
        tests = [
            ('backend', self.test_backend),
            ('hier_tts', self.test_hier_tts),
            ('sadtalker', self.test_sadtalker),
            ('frontend', self.test_frontend),
            ('websocket', self.test_websocket),
            ('audio_synthesis', self.test_audio_synthesis),
            ('ai_chat', self.test_ai_chat)
        ]
        
        for test_name, test_func in tests:
            self.results[test_name] = await test_func()
            await asyncio.sleep(1)  # Пауза между тестами
        
        return self.results
    
    def print_results(self):
        """Вывод результатов тестирования."""
        print("\n" + "="*60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ СИСТЕМЫ ЦИФРОВОГО АВАТАРА")
        print("="*60)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() if result['status'] == 'success')
        
        for test_name, result in self.results.items():
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_icon} {test_name.upper()}: {result['message']}")
        
        print("\n" + "-"*60)
        print(f"📈 ИТОГО: {successful_tests}/{total_tests} тестов прошли успешно")
        
        if successful_tests == total_tests:
            print("🎉 ВСЕ КОМПОНЕНТЫ РАБОТАЮТ ОТЛИЧНО!")
        elif successful_tests >= total_tests * 0.7:
            print("⚠️  БОЛЬШИНСТВО КОМПОНЕНТОВ РАБОТАЮТ")
        else:
            print("🚨 МНОГО ПРОБЛЕМ - ТРЕБУЕТСЯ ДИАГНОСТИКА")
        
        print("="*60)

async def main():
    """Основная функция."""
    tester = AvatarSystemTester()
    results = await tester.run_all_tests()
    tester.print_results()
    
    # Сохранение результатов
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"complete_system_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Результаты сохранены в файл: {filename}")

if __name__ == "__main__":
    asyncio.run(main()) 