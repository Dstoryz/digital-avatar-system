#!/usr/bin/env python3
"""
Детальный тест обучения системы цифрового аватара на наших данных
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import requests
import shutil
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DetailedTrainingTester:
    """Детальный тест обучения системы"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.test_data_dir = self.base_dir / "test_data"
        self.audio_dir = self.test_data_dir / "audio"
        self.training_dir = self.base_dir / "training_data"
        self.training_dir.mkdir(exist_ok=True)
        
        # Конфигурация
        self.config = {
            "backend_url": "http://127.0.0.1:8000",
            "hier_speech_url": "http://127.0.0.1:8001",
            "training_samples": 10,
            "test_phrases": [
                "Привет, это тест системы цифрового аватара",
                "Сегодня мы тестируем качество синтеза речи",
                "Искусственный интеллект создает реалистичную речь",
                "Технологии будущего уже доступны сегодня",
                "Русский язык поддерживается отлично"
            ]
        }
    
    def prepare_training_dataset(self) -> Dict[str, Any]:
        """Подготовка набора данных для обучения"""
        logger.info("📁 Подготавливаем набор данных для обучения...")
        
        audio_files = list(self.audio_dir.glob("*.ogg"))
        logger.info(f"Найдено {len(audio_files)} аудиофайлов")
        
        # Выбираем разнообразные файлы для обучения
        # Сортируем по размеру и выбираем разные размеры
        audio_files.sort(key=lambda x: x.stat().st_size)
        
        # Выбираем файлы разного размера для разнообразия
        small_files = audio_files[:3]
        medium_files = audio_files[len(audio_files)//2-2:len(audio_files)//2+3]
        large_files = audio_files[-3:]
        
        training_files = small_files + medium_files + large_files
        training_files = training_files[:self.config["training_samples"]]
        
        # Копируем файлы в папку обучения
        training_data = {
            "files": [],
            "total_size_mb": 0,
            "formats": set()
        }
        
        for i, file in enumerate(training_files):
            try:
                # Копируем файл
                new_name = f"training_sample_{i+1:02d}.ogg"
                new_path = self.training_dir / new_name
                shutil.copy2(file, new_path)
                
                size_mb = file.stat().st_size / (1024 * 1024)
                
                file_info = {
                    "original_name": file.name,
                    "training_name": new_name,
                    "path": str(new_path),
                    "size_mb": size_mb,
                    "estimated_duration_min": size_mb  # Примерно 1MB = 1 минута
                }
                
                training_data["files"].append(file_info)
                training_data["total_size_mb"] += size_mb
                training_data["formats"].add(file.suffix[1:])
                
                logger.info(f"  - {new_name} ({size_mb:.2f} MB) - {file.name}")
                
            except Exception as e:
                logger.error(f"Ошибка при копировании {file}: {e}")
        
        training_data["formats"] = list(training_data["formats"])
        
        logger.info(f"✅ Подготовлено {len(training_data['files'])} файлов для обучения")
        logger.info(f"📊 Общий размер: {training_data['total_size_mb']:.1f} MB")
        logger.info(f"⏱️ Примерная длительность: {training_data['total_size_mb']:.1f} минут")
        
        return training_data
    
    async def test_voice_cloning_with_training_data(self, training_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Тестирование клонирования голоса на обучающих данных"""
        logger.info("🎤 Тестируем клонирование голоса на обучающих данных...")
        
        cloning_results = []
        
        for file_info in training_data["files"][:5]:  # Тестируем первые 5 файлов
            logger.info(f"Тестируем клонирование: {file_info['training_name']}")
            
            try:
                audio_file = Path(file_info["path"])
                with open(audio_file, 'rb') as f:
                    files = {'audio': (audio_file.name, f, 'audio/ogg')}
                    
                    response = requests.post(
                        f"{self.config['backend_url']}/api/voice/clone",
                        files=files,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"✅ Клонирование успешно: {file_info['training_name']}")
                        cloning_results.append({
                            "file": file_info["training_name"],
                            "success": True,
                            "voice_id": result.get('voice_id'),
                            "processing_time": result.get('processing_time', 0),
                            "message": result.get('message', 'OK')
                        })
                    else:
                        logger.warning(f"⚠️ Ошибка клонирования {file_info['training_name']}: {response.status_code}")
                        cloning_results.append({
                            "file": file_info["training_name"],
                            "success": False,
                            "error": f"HTTP {response.status_code}"
                        })
                        
            except Exception as e:
                logger.error(f"❌ Ошибка при клонировании {file_info['training_name']}: {e}")
                cloning_results.append({
                    "file": file_info["training_name"],
                    "success": False,
                    "error": str(e)
                })
        
        return cloning_results
    
    async def test_tts_with_cloned_voices(self, cloning_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Тестирование TTS с клонированными голосами"""
        logger.info("🔊 Тестируем TTS с клонированными голосами...")
        
        tts_results = []
        
        for clone_result in cloning_results:
            if clone_result.get("success"):
                voice_id = clone_result.get("voice_id")
                file_name = clone_result.get("file")
                
                logger.info(f"Тестируем TTS для голоса {voice_id} (из {file_name})")
                
                for phrase in self.config["test_phrases"]:
                    try:
                        response = requests.post(
                            f"{self.config['hier_speech_url']}/synthesize",
                            json={
                                "text": phrase,
                                "voice_id": voice_id,
                                "language": "ru"
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            logger.info(f"✅ TTS успешен: '{phrase[:30]}...'")
                            tts_results.append({
                                "voice_id": voice_id,
                                "source_file": file_name,
                                "phrase": phrase,
                                "success": True,
                                "audio_path": result.get('audio_path'),
                                "processing_time": result.get('processing_time', 0)
                            })
                        else:
                            logger.warning(f"⚠️ Ошибка TTS: {response.status_code}")
                            tts_results.append({
                                "voice_id": voice_id,
                                "source_file": file_name,
                                "phrase": phrase,
                                "success": False,
                                "error": f"HTTP {response.status_code}"
                            })
                            
                    except Exception as e:
                        logger.error(f"❌ Ошибка при TTS: {e}")
                        tts_results.append({
                            "voice_id": voice_id,
                            "source_file": file_name,
                            "phrase": phrase,
                            "success": False,
                            "error": str(e)
                        })
        
        return tts_results
    
    def analyze_audio_quality(self, tts_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ качества аудио"""
        logger.info("📊 Анализируем качество аудио...")
        
        successful_results = [r for r in tts_results if r.get("success")]
        
        if not successful_results:
            return {"quality_score": 0, "message": "Нет успешных результатов для анализа"}
        
        # Простой анализ на основе времени обработки и размера файлов
        processing_times = [r.get("processing_time", 0) for r in successful_results]
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        # Проверяем размеры аудиофайлов
        audio_sizes = []
        for result in successful_results:
            audio_path = result.get("audio_path")
            if audio_path:
                full_path = self.base_dir / "HierSpeech_TTS" / audio_path
                if full_path.exists():
                    size_mb = full_path.stat().st_size / (1024 * 1024)
                    audio_sizes.append(size_mb)
        
        avg_audio_size = sum(audio_sizes) / len(audio_sizes) if audio_sizes else 0
        
        # Простая оценка качества
        quality_score = 0.0
        
        # Оценка по времени обработки (быстрее = лучше)
        if avg_processing_time < 5000:  # менее 5 секунд
            quality_score += 0.3
        elif avg_processing_time < 10000:  # менее 10 секунд
            quality_score += 0.2
        else:
            quality_score += 0.1
        
        # Оценка по размеру аудио (больше = лучше качество)
        if avg_audio_size > 0.05:  # более 50KB
            quality_score += 0.3
        elif avg_audio_size > 0.02:  # более 20KB
            quality_score += 0.2
        else:
            quality_score += 0.1
        
        # Оценка по количеству успешных результатов
        success_rate = len(successful_results) / len(tts_results) if tts_results else 0
        quality_score += success_rate * 0.4
        
        return {
            "quality_score": min(quality_score, 1.0),
            "avg_processing_time_ms": avg_processing_time,
            "avg_audio_size_mb": avg_audio_size,
            "success_rate": success_rate,
            "total_tests": len(tts_results),
            "successful_tests": len(successful_results)
        }
    
    async def run_detailed_training_test(self) -> Dict[str, Any]:
        """Запуск детального теста обучения"""
        logger.info("🎯 Запускаем детальный тест обучения...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "training_data": {},
            "voice_cloning": [],
            "tts_synthesis": [],
            "quality_analysis": {},
            "overall_score": 0
        }
        
        try:
            # 1. Подготовка данных
            results["training_data"] = self.prepare_training_dataset()
            
            # 2. Тест клонирования голоса
            results["voice_cloning"] = await self.test_voice_cloning_with_training_data(results["training_data"])
            
            # 3. Тест TTS
            results["tts_synthesis"] = await self.test_tts_with_cloned_voices(results["voice_cloning"])
            
            # 4. Анализ качества
            results["quality_analysis"] = self.analyze_audio_quality(results["tts_synthesis"])
            
            # 5. Вычисление общего балла
            cloning_success_rate = sum(1 for r in results["voice_cloning"] if r.get("success")) / len(results["voice_cloning"]) if results["voice_cloning"] else 0
            tts_success_rate = sum(1 for r in results["tts_synthesis"] if r.get("success")) / len(results["tts_synthesis"]) if results["tts_synthesis"] else 0
            quality_score = results["quality_analysis"].get("quality_score", 0)
            
            results["overall_score"] = (cloning_success_rate + tts_success_rate + quality_score) / 3
            
            logger.info(f"📊 Общий балл: {results['overall_score']:.2f}/1.0")
            
        except Exception as e:
            logger.error(f"❌ Ошибка в детальном тесте: {e}")
            results["error"] = str(e)
        
        return results
    
    def save_detailed_results(self, results: Dict[str, Any]):
        """Сохранение детальных результатов"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.base_dir / f"detailed_training_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Детальные результаты сохранены в {results_file}")
        
        # Создаем подробный отчет
        report_file = self.base_dir / f"detailed_training_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ДЕТАЛЬНЫЙ ОТЧЕТ ОБ ОБУЧЕНИИ СИСТЕМЫ ЦИФРОВОГО АВАТАРА\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("ДАННЫЕ ДЛЯ ОБУЧЕНИЯ:\n")
            f.write(f"- Файлов подготовлено: {len(results['training_data'].get('files', []))}\n")
            f.write(f"- Общий размер: {results['training_data'].get('total_size_mb', 0):.1f} MB\n")
            f.write(f"- Форматы: {', '.join(results['training_data'].get('formats', []))}\n\n")
            
            f.write("КЛОНИРОВАНИЕ ГОЛОСА:\n")
            cloning_results = results.get('voice_cloning', [])
            successful_cloning = sum(1 for r in cloning_results if r.get('success'))
            f.write(f"- Успешно: {successful_cloning}/{len(cloning_results)}\n")
            for result in cloning_results:
                status = "✅" if result.get('success') else "❌"
                f.write(f"  {status} {result.get('file', 'Unknown')}\n")
            f.write("\n")
            
            f.write("СИНТЕЗ РЕЧИ:\n")
            tts_results = results.get('tts_synthesis', [])
            successful_tts = sum(1 for r in tts_results if r.get('success'))
            f.write(f"- Успешно: {successful_tts}/{len(tts_results)}\n")
            f.write(f"- Протестировано голосов: {len(set(r.get('voice_id') for r in tts_results if r.get('voice_id')))}\n\n")
            
            f.write("АНАЛИЗ КАЧЕСТВА:\n")
            quality = results.get('quality_analysis', {})
            f.write(f"- Балл качества: {quality.get('quality_score', 0):.2f}/1.0\n")
            f.write(f"- Среднее время обработки: {quality.get('avg_processing_time_ms', 0):.0f} мс\n")
            f.write(f"- Средний размер аудио: {quality.get('avg_audio_size_mb', 0):.3f} MB\n")
            f.write(f"- Процент успеха: {quality.get('success_rate', 0)*100:.1f}%\n\n")
            
            f.write("ИТОГОВЫЙ РЕЗУЛЬТАТ:\n")
            overall_score = results.get('overall_score', 0)
            f.write(f"- Общий балл: {overall_score:.2f}/1.0\n")
            
            if overall_score >= 0.8:
                f.write("- 🎉 Система готова к продакшену!\n")
            elif overall_score >= 0.6:
                f.write("- 👍 Система работает хорошо, можно использовать\n")
            elif overall_score >= 0.4:
                f.write("- ⚠️ Система требует доработки\n")
            else:
                f.write("- ❌ Система требует серьезной доработки\n")
        
        logger.info(f"✅ Подробный отчет сохранен в {report_file}")

async def main():
    """Главная функция"""
    print("🤖 ДЕТАЛЬНЫЙ ТЕСТ ОБУЧЕНИЯ СИСТЕМЫ ЦИФРОВОГО АВАТАРА")
    print("=" * 60)
    
    tester = DetailedTrainingTester()
    results = await tester.run_detailed_training_test()
    tester.save_detailed_results(results)
    
    print(f"\n📊 Общий балл системы: {results.get('overall_score', 0):.2f}/1.0")
    print("📁 Результаты сохранены в корневой папке проекта")

if __name__ == "__main__":
    asyncio.run(main()) 