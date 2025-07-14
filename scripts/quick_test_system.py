#!/usr/bin/env python3
"""
Быстрое тестирование системы цифрового аватара
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

class QuickSystemTester:
    """Быстрое тестирование системы"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.test_data_dir = self.base_dir / "test_data"
        self.audio_dir = self.test_data_dir / "audio"
        
        # Конфигурация
        self.config = {
            "backend_url": "http://127.0.0.1:8000",
            "hier_speech_url": "http://127.0.0.1:8001",
            "test_phrases": [
                "Привет, как дела?",
                "Сегодня прекрасная погода",
                "Я изучаю искусственный интеллект"
            ]
        }
    
    def analyze_audio_files(self) -> Dict[str, Any]:
        """Быстрый анализ аудиофайлов"""
        logger.info("🔍 Анализируем аудиофайлы...")
        
        audio_files = list(self.audio_dir.glob("*.ogg"))
        logger.info(f"Найдено {len(audio_files)} аудиофайлов")
        
        # Выбираем несколько файлов для тестирования
        test_files = audio_files[:5]  # Первые 5 файлов
        
        analysis = {
            "total_files": len(audio_files),
            "test_files": [f.name for f in test_files],
            "test_file_paths": [str(f) for f in test_files]
        }
        
        return analysis
    
    async def test_connections(self) -> Dict[str, bool]:
        """Тестирование подключений"""
        logger.info("🔗 Тестируем подключения...")
        
        connections = {}
        
        # Тест HierSpeech TTS
        try:
            response = requests.get(f"{self.config['hier_speech_url']}/health", timeout=5)
            connections["hier_speech"] = response.status_code == 200
            logger.info(f"HierSpeech TTS: {'✅' if connections['hier_speech'] else '❌'}")
        except Exception as e:
            connections["hier_speech"] = False
            logger.error(f"HierSpeech TTS: ❌ {e}")
        
        # Тест Backend
        try:
            response = requests.get(f"{self.config['backend_url']}/health", timeout=5)
            connections["backend"] = response.status_code == 200
            logger.info(f"Backend: {'✅' if connections['backend'] else '❌'}")
        except Exception as e:
            connections["backend"] = False
            logger.error(f"Backend: ❌ {e}")
        
        return connections
    
    async def test_voice_cloning(self, audio_file_path: str) -> Dict[str, Any]:
        """Тестирование клонирования голоса"""
        logger.info(f"🎤 Тестируем клонирование голоса...")
        
        try:
            audio_file = Path(audio_file_path)
            with open(audio_file, 'rb') as f:
                files = {'audio': (audio_file.name, f, 'audio/ogg')}
                
                response = requests.post(
                    f"{self.config['backend_url']}/api/voice/clone",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("✅ Клонирование голоса успешно")
                    return {
                        "success": True,
                        "voice_id": result.get('voice_id'),
                        "message": result.get('message', 'OK')
                    }
                else:
                    logger.error(f"❌ Ошибка клонирования: {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ Ошибка при клонировании: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_tts_synthesis(self, text: str, voice_id: str = "default") -> Dict[str, Any]:
        """Тестирование синтеза речи"""
        logger.info(f"🔊 Тестируем синтез речи: '{text[:30]}...'")
        
        try:
            response = requests.post(
                f"{self.config['hier_speech_url']}/synthesize",
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
                    "processing_time": result.get('processing_time', 0)
                }
            else:
                logger.error(f"❌ Ошибка синтеза: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Ошибка при синтезе: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_quick_test(self) -> Dict[str, Any]:
        """Запуск быстрого тестирования"""
        logger.info("🚀 Запускаем быстрое тестирование...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "analysis": {},
            "connections": {},
            "voice_cloning": {},
            "tts_synthesis": [],
            "overall_score": 0
        }
        
        # 1. Анализ файлов
        results["analysis"] = self.analyze_audio_files()
        
        # 2. Тест подключений
        results["connections"] = await self.test_connections()
        
        # 3. Тест клонирования голоса (если есть файлы)
        if results["analysis"]["test_file_paths"]:
            audio_file = results["analysis"]["test_file_paths"][0]
            results["voice_cloning"] = await self.test_voice_cloning(audio_file)
        
        # 4. Тест синтеза речи
        voice_id = results["voice_cloning"].get("voice_id", "default")
        for phrase in self.config["test_phrases"]:
            tts_result = await self.test_tts_synthesis(phrase, voice_id)
            tts_result["phrase"] = phrase
            results["tts_synthesis"].append(tts_result)
        
        # Вычисляем общий балл
        connection_score = sum(results["connections"].values()) / len(results["connections"])
        cloning_score = 1.0 if results["voice_cloning"].get("success") else 0.0
        tts_score = sum(1 for r in results["tts_synthesis"] if r.get("success")) / len(results["tts_synthesis"]) if results["tts_synthesis"] else 0
        
        results["overall_score"] = (connection_score + cloning_score + tts_score) / 3
        
        logger.info(f"📊 Общий балл: {results['overall_score']:.2f}/1.0")
        
        return results
    
    def save_results(self, results: Dict[str, Any]):
        """Сохранение результатов"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.base_dir / f"quick_test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Результаты сохранены в {results_file}")
        
        # Выводим краткий отчет
        print("\n" + "="*50)
        print("ОТЧЕТ О БЫСТРОМ ТЕСТИРОВАНИИ")
        print("="*50)
        print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Всего файлов: {results['analysis']['total_files']}")
        print(f"Подключения: {sum(results['connections'].values())}/{len(results['connections'])}")
        print(f"Клонирование голоса: {'✅' if results['voice_cloning'].get('success') else '❌'}")
        print(f"Синтез речи: {sum(1 for r in results['tts_synthesis'] if r.get('success'))}/{len(results['tts_synthesis'])}")
        print(f"Общий балл: {results['overall_score']:.2f}/1.0")
        
        if results['overall_score'] >= 0.8:
            print("🎉 Система работает отлично!")
        elif results['overall_score'] >= 0.6:
            print("👍 Система работает хорошо")
        else:
            print("⚠️ Система требует доработки")

async def main():
    """Главная функция"""
    print("🤖 БЫСТРОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ ЦИФРОВОГО АВАТАРА")
    print("=" * 50)
    
    tester = QuickSystemTester()
    results = await tester.run_quick_test()
    tester.save_results(results)

if __name__ == "__main__":
    asyncio.run(main()) 