#!/usr/bin/env python3
"""
Скрипт для обучения и тестирования системы цифрового аватара
на основе собственных аудиоданных
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import time
import requests
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DigitalAvatarTrainer:
    """Класс для обучения и тестирования системы цифрового аватара"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.test_data_dir = self.base_dir / "test_data"
        self.audio_dir = self.test_data_dir / "audio"
        self.results_dir = self.base_dir / "training_results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Конфигурация
        self.config = {
            "backend_url": "http://127.0.0.1:8000",
            "hier_speech_url": "http://127.0.0.1:8001",
            "test_phrases": [
                "Привет, как дела?",
                "Сегодня прекрасная погода",
                "Я изучаю искусственный интеллект",
                "Цифровой аватар работает отлично",
                "Технологии будущего уже здесь"
            ],
            "training_samples": 10,  # Количество файлов для обучения
            "test_samples": 5        # Количество файлов для тестирования
        }
        
    def analyze_audio_data(self) -> Dict[str, Any]:
        """Анализ аудиоданных для обучения"""
        logger.info("🔍 Анализируем аудиоданные...")
        
        audio_files = list(self.audio_dir.glob("*.ogg"))
        logger.info(f"Найдено {len(audio_files)} аудиофайлов")
        
        # Анализ размеров файлов
        file_sizes = []
        for file in audio_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            file_sizes.append(size_mb)
        
        analysis = {
            "total_files": len(audio_files),
            "total_size_mb": sum(file_sizes),
            "avg_size_mb": sum(file_sizes) / len(file_sizes) if file_sizes else 0,
            "min_size_mb": min(file_sizes) if file_sizes else 0,
            "max_size_mb": max(file_sizes) if file_sizes else 0,
            "file_list": [f.name for f in audio_files[:20]]  # Первые 20 файлов
        }
        
        logger.info(f"📊 Анализ данных: {analysis}")
        return analysis
    
    def select_training_files(self, analysis: Dict[str, Any]) -> List[Path]:
        """Выбор файлов для обучения"""
        logger.info("📁 Выбираем файлы для обучения...")
        
        audio_files = list(self.audio_dir.glob("*.ogg"))
        
        # Сортируем по размеру (выбираем средние по размеру файлы)
        audio_files.sort(key=lambda x: x.stat().st_size)
        
        # Выбираем файлы для обучения (средние по размеру)
        start_idx = len(audio_files) // 4
        training_files = audio_files[start_idx:start_idx + self.config["training_samples"]]
        
        logger.info(f"Выбрано {len(training_files)} файлов для обучения:")
        for file in training_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            logger.info(f"  - {file.name} ({size_mb:.2f} MB)")
        
        return training_files
    
    def prepare_training_data(self, training_files: List[Path]) -> Dict[str, Any]:
        """Подготовка данных для обучения"""
        logger.info("⚙️ Подготавливаем данные для обучения...")
        
        training_data = {
            "files": [],
            "total_duration": 0,
            "formats": set(),
            "sample_rates": []
        }
        
        for file in training_files:
            try:
                # Получаем информацию о файле
                size_mb = file.stat().st_size / (1024 * 1024)
                
                # Простая оценка длительности (приблизительно)
                # Предполагаем, что 1 MB ≈ 1 минута аудио
                estimated_duration = size_mb * 60
                
                file_info = {
                    "name": file.name,
                    "path": str(file),
                    "size_mb": size_mb,
                    "estimated_duration_sec": estimated_duration,
                    "format": file.suffix[1:]  # убираем точку
                }
                
                training_data["files"].append(file_info)
                training_data["total_duration"] += estimated_duration
                training_data["formats"].add(file.suffix[1:])
                
            except Exception as e:
                logger.error(f"Ошибка при обработке файла {file}: {e}")
        
        training_data["formats"] = list(training_data["formats"])
        
        logger.info(f"📋 Подготовлено {len(training_data['files'])} файлов")
        logger.info(f"⏱️ Общая длительность: {training_data['total_duration']/60:.1f} минут")
        
        return training_data
    
    async def test_hier_speech_connection(self) -> bool:
        """Тестирование подключения к HierSpeech TTS"""
        logger.info("🔗 Тестируем подключение к HierSpeech TTS...")
        
        try:
            response = requests.get(f"{self.config['hier_speech_url']}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ HierSpeech TTS доступен")
                return True
            else:
                logger.warning(f"⚠️ HierSpeech TTS ответил с кодом {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к HierSpeech TTS: {e}")
            return False
    
    async def test_backend_connection(self) -> bool:
        """Тестирование подключения к основному backend"""
        logger.info("🔗 Тестируем подключение к backend...")
        
        try:
            response = requests.get(f"{self.config['backend_url']}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Backend доступен")
                return True
            else:
                logger.warning(f"⚠️ Backend ответил с кодом {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к backend: {e}")
            return False
    
    async def test_voice_cloning(self, audio_file: Path) -> Dict[str, Any]:
        """Тестирование клонирования голоса"""
        logger.info(f"🎤 Тестируем клонирование голоса для {audio_file.name}")
        
        try:
            # Загружаем аудиофайл
            with open(audio_file, 'rb') as f:
                files = {'audio': (audio_file.name, f, 'audio/ogg')}
                
                # Отправляем запрос на клонирование
                response = requests.post(
                    f"{self.config['backend_url']}/api/voice/clone",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Клонирование успешно: {result.get('message', 'OK')}")
                    return {
                        "success": True,
                        "voice_id": result.get('voice_id'),
                        "duration_ms": result.get('processing_time', 0)
                    }
                else:
                    logger.error(f"❌ Ошибка клонирования: {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ Ошибка при клонировании голоса: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_tts_synthesis(self, text: str, voice_id: str | None = None) -> Dict[str, Any]:
        """Тестирование синтеза речи"""
        logger.info(f"🔊 Тестируем синтез речи: '{text[:50]}...'")
        
        try:
            # Тестируем HierSpeech TTS
            hier_response = requests.post(
                f"{self.config['hier_speech_url']}/synthesize",
                json={
                    "text": text,
                    "voice_id": voice_id or "default",
                    "language": "ru"
                },
                timeout=30
            )
            
            if hier_response.status_code == 200:
                hier_result = hier_response.json()
                logger.info(f"✅ HierSpeech TTS синтез успешен")
                return {
                    "success": True,
                    "hier_speech": {
                        "audio_path": hier_result.get('audio_path'),
                        "duration_ms": hier_result.get('processing_time', 0)
                    }
                }
            else:
                logger.error(f"❌ Ошибка HierSpeech TTS: {hier_response.status_code}")
                return {"success": False, "error": f"HierSpeech HTTP {hier_response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Ошибка при синтезе речи: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_comprehensive_test(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Запуск комплексного тестирования"""
        logger.info("🚀 Запускаем комплексное тестирование системы...")
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "connections": {},
            "voice_cloning": [],
            "tts_synthesis": [],
            "overall_score": 0
        }
        
        # Тестируем подключения
        test_results["connections"]["hier_speech"] = await self.test_hier_speech_connection()
        test_results["connections"]["backend"] = await self.test_backend_connection()
        
        # Тестируем клонирование голоса на нескольких файлах
        for i, file_info in enumerate(training_data["files"][:3]):  # Тестируем первые 3 файла
            audio_file = Path(file_info["path"])
            clone_result = await self.test_voice_cloning(audio_file)
            clone_result["file"] = file_info["name"]
            test_results["voice_cloning"].append(clone_result)
            
            # Если клонирование успешно, тестируем синтез
            if clone_result.get("success"):
                voice_id = clone_result.get("voice_id")
                if voice_id:  # Проверяем, что voice_id не None
                    for phrase in self.config["test_phrases"][:2]:  # Тестируем первые 2 фразы
                        tts_result = await self.test_tts_synthesis(phrase, voice_id)
                    tts_result["phrase"] = phrase
                    tts_result["voice_id"] = voice_id
                    test_results["tts_synthesis"].append(tts_result)
        
        # Вычисляем общий балл
        connection_score = sum(test_results["connections"].values()) / len(test_results["connections"])
        cloning_score = sum(1 for r in test_results["voice_cloning"] if r.get("success")) / len(test_results["voice_cloning"]) if test_results["voice_cloning"] else 0
        tts_score = sum(1 for r in test_results["tts_synthesis"] if r.get("success")) / len(test_results["tts_synthesis"]) if test_results["tts_synthesis"] else 0
        
        test_results["overall_score"] = (connection_score + cloning_score + tts_score) / 3
        
        logger.info(f"📊 Общий балл системы: {test_results['overall_score']:.2f}/1.0")
        
        return test_results
    
    def save_results(self, analysis: Dict[str, Any], training_data: Dict[str, Any], test_results: Dict[str, Any]):
        """Сохранение результатов"""
        logger.info("💾 Сохраняем результаты...")
        
        results = {
            "analysis": analysis,
            "training_data": training_data,
            "test_results": test_results,
            "config": self.config
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"training_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Результаты сохранены в {results_file}")
        
        # Создаем краткий отчет
        report_file = self.results_dir / f"training_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ОТЧЕТ ОБ ОБУЧЕНИИ И ТЕСТИРОВАНИИ СИСТЕМЫ ЦИФРОВОГО АВАТАРА\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("АНАЛИЗ ДАННЫХ:\n")
            f.write(f"- Всего файлов: {analysis['total_files']}\n")
            f.write(f"- Общий размер: {analysis['total_size_mb']:.1f} MB\n")
            f.write(f"- Средний размер файла: {analysis['avg_size_mb']:.2f} MB\n\n")
            
            f.write("ДАННЫЕ ДЛЯ ОБУЧЕНИЯ:\n")
            f.write(f"- Файлов для обучения: {len(training_data['files'])}\n")
            f.write(f"- Общая длительность: {training_data['total_duration']/60:.1f} минут\n")
            f.write(f"- Форматы: {', '.join(training_data['formats'])}\n\n")
            
            f.write("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:\n")
            f.write(f"- Подключения: {sum(test_results['connections'].values())}/{len(test_results['connections'])}\n")
            f.write(f"- Клонирование голоса: {sum(1 for r in test_results['voice_cloning'] if r.get('success'))}/{len(test_results['voice_cloning'])}\n")
            f.write(f"- Синтез речи: {sum(1 for r in test_results['tts_synthesis'] if r.get('success'))}/{len(test_results['tts_synthesis'])}\n")
            f.write(f"- Общий балл: {test_results['overall_score']:.2f}/1.0\n\n")
            
            f.write("РЕКОМЕНДАЦИИ:\n")
            if test_results['overall_score'] >= 0.8:
                f.write("- Система работает отлично! Можно использовать в продакшене.\n")
            elif test_results['overall_score'] >= 0.6:
                f.write("- Система работает хорошо, но есть возможности для улучшения.\n")
            else:
                f.write("- Система требует доработки перед использованием.\n")
        
        logger.info(f"✅ Отчет сохранен в {report_file}")
    
    async def run_training_pipeline(self):
        """Запуск полного пайплайна обучения и тестирования"""
        logger.info("🎯 Запускаем пайплайн обучения и тестирования...")
        
        try:
            # 1. Анализ данных
            analysis = self.analyze_audio_data()
            
            # 2. Выбор файлов для обучения
            training_files = self.select_training_files(analysis)
            
            # 3. Подготовка данных
            training_data = self.prepare_training_data(training_files)
            
            # 4. Комплексное тестирование
            test_results = await self.run_comprehensive_test(training_data)
            
            # 5. Сохранение результатов
            self.save_results(analysis, training_data, test_results)
            
            logger.info("🎉 Пайплайн обучения и тестирования завершен!")
            
            return {
                "success": True,
                "overall_score": test_results["overall_score"],
                "summary": f"Система протестирована с баллом {test_results['overall_score']:.2f}/1.0"
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка в пайплайне обучения: {e}")
            return {"success": False, "error": str(e)}

async def main():
    """Главная функция"""
    print("🤖 СИСТЕМА ОБУЧЕНИЯ И ТЕСТИРОВАНИЯ ЦИФРОВОГО АВАТАРА")
    print("=" * 60)
    
    trainer = DigitalAvatarTrainer()
    result = await trainer.run_training_pipeline()
    
    if result["success"]:
        print(f"\n✅ {result['summary']}")
        print("\n📁 Результаты сохранены в папке training_results/")
    else:
        print(f"\n❌ Ошибка: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main()) 