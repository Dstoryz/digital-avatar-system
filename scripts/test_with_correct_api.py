#!/usr/bin/env python3
"""
Тестирование системы с правильными API endpoints
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import requests
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CorrectAPITester:
    """Тестирование с правильными API endpoints"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.test_data_dir = self.base_dir / "test_data"
        self.audio_dir = self.test_data_dir / "audio"
        
        # Конфигурация с правильными endpoints
        self.config = {
            "backend_url": "http://127.0.0.1:8000",
            "hier_speech_url": "http://127.0.0.1:8001",
            "test_phrases": [
                "Привет, это тест системы цифрового аватара",
                "Сегодня мы тестируем качество синтеза речи",
                "Искусственный интеллект создает реалистичную речь"
            ]
        }
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Получение списка доступных голосов"""
        logger.info("🎤 Получаем список доступных голосов...")
        
        try:
            response = requests.get(f"{self.config['backend_url']}/api/v1/tts/voices")
            if response.status_code == 200:
                voices = response.json()
                logger.info(f"✅ Найдено {len(voices)} голосов")
                return voices
            else:
                logger.warning(f"⚠️ Ошибка получения голосов: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"❌ Ошибка при получении голосов: {e}")
            return []
    
    async def test_voice_cloning(self, audio_file_path: str) -> Dict[str, Any]:
        """Тестирование клонирования голоса с правильным endpoint"""
        logger.info(f"🎤 Тестируем клонирование голоса...")
        
        try:
            audio_file = Path(audio_file_path)
            with open(audio_file, 'rb') as f:
                files = {'audio': (audio_file.name, f, 'audio/ogg')}
                
                response = requests.post(
                    f"{self.config['backend_url']}/api/v1/tts/clone-voice",
                    files=files,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("✅ Клонирование голоса успешно")
                    return {
                        "success": True,
                        "voice_id": result.get('voice_id'),
                        "message": result.get('message', 'OK'),
                        "processing_time": result.get('processing_time', 0)
                    }
                else:
                    logger.error(f"❌ Ошибка клонирования: {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ Ошибка при клонировании: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_tts_synthesis(self, text: str, voice_id: str = "default") -> Dict[str, Any]:
        """Тестирование синтеза речи с правильным endpoint"""
        logger.info(f"🔊 Тестируем синтез речи: '{text[:30]}...'")
        
        try:
            response = requests.post(
                f"{self.config['backend_url']}/api/v1/tts/synthesize",
                json={
                    "text": text,
                    "voice_id": voice_id,
                    "language": "ru"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Синтез речи успешен")
                return {
                    "success": True,
                    "audio_path": result.get('audio_path'),
                    "processing_time": result.get('processing_time', 0),
                    "voice_id": voice_id
                }
            else:
                logger.error(f"❌ Ошибка синтеза: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Ошибка при синтезе: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_hier_speech_direct(self, text: str) -> Dict[str, Any]:
        """Прямое тестирование HierSpeech TTS"""
        logger.info(f"🔊 Прямое тестирование HierSpeech: '{text[:30]}...'")
        
        try:
            response = requests.post(
                f"{self.config['hier_speech_url']}/synthesize",
                json={
                    "text": text,
                    "voice_id": "default",
                    "language": "ru"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ HierSpeech TTS синтез успешен")
                return {
                    "success": True,
                    "audio_path": result.get('audio_path'),
                    "processing_time": result.get('processing_time', 0)
                }
            else:
                logger.error(f"❌ Ошибка HierSpeech: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Ошибка при HierSpeech синтезе: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_russian_tts(self) -> Dict[str, Any]:
        """Тестирование русского TTS"""
        logger.info("🇷🇺 Тестируем русский TTS...")
        
        try:
            response = requests.get(f"{self.config['backend_url']}/api/v1/tts/test-russian")
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Русский TTS тест успешен")
                return {
                    "success": True,
                    "result": result
                }
            else:
                logger.error(f"❌ Ошибка русского TTS: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"❌ Ошибка при тесте русского TTS: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Запуск комплексного тестирования"""
        logger.info("🚀 Запускаем комплексное тестирование с правильными API...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "available_voices": [],
            "voice_cloning": {},
            "backend_tts": [],
            "hier_speech_tts": [],
            "russian_tts_test": {},
            "overall_score": 0
        }
        
        # 1. Получаем доступные голоса
        results["available_voices"] = self.get_available_voices()
        
        # 2. Тестируем клонирование голоса
        audio_files = list(self.audio_dir.glob("*.ogg"))
        if audio_files:
            test_file = audio_files[0]  # Первый файл
            results["voice_cloning"] = await self.test_voice_cloning(str(test_file))
        
        # 3. Тестируем TTS через backend
        voice_id = results["voice_cloning"].get("voice_id", "default")
        for phrase in self.config["test_phrases"]:
            tts_result = await self.test_tts_synthesis(phrase, voice_id)
            tts_result["phrase"] = phrase
            results["backend_tts"].append(tts_result)
        
        # 4. Тестируем HierSpeech напрямую
        for phrase in self.config["test_phrases"][:2]:  # Первые 2 фразы
            hier_result = await self.test_hier_speech_direct(phrase)
            hier_result["phrase"] = phrase
            results["hier_speech_tts"].append(hier_result)
        
        # 5. Тестируем русский TTS
        results["russian_tts_test"] = await self.test_russian_tts()
        
        # Вычисляем общий балл
        scores = []
        
        # Балл за доступные голоса
        if results["available_voices"]:
            scores.append(1.0)
        else:
            scores.append(0.0)
        
        # Балл за клонирование
        if results["voice_cloning"].get("success"):
            scores.append(1.0)
        else:
            scores.append(0.0)
        
        # Балл за backend TTS
        backend_success = sum(1 for r in results["backend_tts"] if r.get("success"))
        backend_score = backend_success / len(results["backend_tts"]) if results["backend_tts"] else 0
        scores.append(backend_score)
        
        # Балл за HierSpeech TTS
        hier_success = sum(1 for r in results["hier_speech_tts"] if r.get("success"))
        hier_score = hier_success / len(results["hier_speech_tts"]) if results["hier_speech_tts"] else 0
        scores.append(hier_score)
        
        # Балл за русский TTS
        if results["russian_tts_test"].get("success"):
            scores.append(1.0)
        else:
            scores.append(0.0)
        
        results["overall_score"] = sum(scores) / len(scores)
        
        logger.info(f"📊 Общий балл: {results['overall_score']:.2f}/1.0")
        
        return results
    
    def save_results(self, results: Dict[str, Any]):
        """Сохранение результатов"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.base_dir / f"correct_api_test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Результаты сохранены в {results_file}")
        
        # Выводим краткий отчет
        print("\n" + "="*50)
        print("ОТЧЕТ О ТЕСТИРОВАНИИ С ПРАВИЛЬНЫМИ API")
        print("="*50)
        print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Доступных голосов: {len(results['available_voices'])}")
        print(f"Клонирование голоса: {'✅' if results['voice_cloning'].get('success') else '❌'}")
        print(f"Backend TTS: {sum(1 for r in results['backend_tts'] if r.get('success'))}/{len(results['backend_tts'])}")
        print(f"HierSpeech TTS: {sum(1 for r in results['hier_speech_tts'] if r.get('success'))}/{len(results['hier_speech_tts'])}")
        print(f"Русский TTS: {'✅' if results['russian_tts_test'].get('success') else '❌'}")
        print(f"Общий балл: {results['overall_score']:.2f}/1.0")
        
        if results['overall_score'] >= 0.8:
            print("🎉 Система работает отлично!")
        elif results['overall_score'] >= 0.6:
            print("👍 Система работает хорошо")
        else:
            print("⚠️ Система требует доработки")

async def main():
    """Главная функция"""
    print("🤖 ТЕСТИРОВАНИЕ С ПРАВИЛЬНЫМИ API ENDPOINTS")
    print("=" * 50)
    
    tester = CorrectAPITester()
    results = await tester.run_comprehensive_test()
    tester.save_results(results)

if __name__ == "__main__":
    asyncio.run(main()) 