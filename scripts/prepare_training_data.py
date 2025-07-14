#!/usr/bin/env python3
"""
Скрипт для подготовки данных для дообучения модели синтеза речи
"""

import os
import subprocess
import json
import random
from pathlib import Path
import logging
from typing import List, Dict, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrainingDataPreparator:
    def __init__(self, input_dir: str = "test_data/audio", output_dir: str = "training_data"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.wav_dir = self.output_dir / "wav"
        self.metadata_dir = self.output_dir / "metadata"
        
        # Создаём директории
        self.wav_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
    def convert_ogg_to_wav(self) -> List[str]:
        """Конвертирует .ogg файлы в .wav"""
        logger.info("🔄 Конвертация .ogg в .wav...")
        
        converted_files = []
        ogg_files = list(self.input_dir.glob("*.ogg"))
        
        for i, ogg_file in enumerate(ogg_files, 1):
            wav_file = self.wav_dir / f"{ogg_file.stem}.wav"
            
            logger.info(f"Конвертируем {i}/{len(ogg_files)}: {ogg_file.name}")
            
            try:
                # Конвертация с оптимальными параметрами для TTS
                cmd = [
                    "ffmpeg", "-i", str(ogg_file),
                    "-ar", "22050",  # Частота дискретизации
                    "-ac", "1",      # Моно
                    "-sample_fmt", "s16",  # 16-bit
                    "-y",  # Перезаписать существующий файл
                    str(wav_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    converted_files.append(str(wav_file))
                    logger.info(f"✅ Конвертирован: {wav_file.name}")
                else:
                    logger.error(f"❌ Ошибка конвертации {ogg_file.name}: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при конвертации {ogg_file.name}: {e}")
        
        logger.info(f"🎉 Конвертировано {len(converted_files)} файлов")
        return converted_files
    
    def create_dummy_transcriptions(self, wav_files: List[str]) -> List[Dict]:
        """Создаёт заглушки транскрипций (для демонстрации)"""
        logger.info("📝 Создание транскрипций...")
        
        # Примеры фраз для демонстрации
        sample_phrases = [
            "Привет, как дела?",
            "Сегодня прекрасная погода.",
            "Я очень рада вас видеть.",
            "Спасибо за внимание.",
            "До свидания!",
            "Как прошёл твой день?",
            "Что нового?",
            "Отличная идея!",
            "Я согласна с тобой.",
            "Это интересно.",
            "Расскажи подробнее.",
            "Я понимаю тебя.",
            "Всё будет хорошо.",
            "Не волнуйся.",
            "Я здесь для тебя."
        ]
        
        transcriptions = []
        
        for wav_file in wav_files:
            # Выбираем случайную фразу
            phrase = random.choice(sample_phrases)
            
            transcription = {
                "file": Path(wav_file).name,
                "text": phrase,
                "duration": self.get_audio_duration(wav_file)
            }
            
            transcriptions.append(transcription)
        
        logger.info(f"📝 Создано {len(transcriptions)} транскрипций")
        return transcriptions
    
    def get_audio_duration(self, wav_file: str) -> float:
        """Получает длительность аудиофайла"""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", wav_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                return 0.0
                
        except Exception as e:
            logger.warning(f"Не удалось получить длительность {wav_file}: {e}")
            return 0.0
    
    def split_train_val(self, transcriptions: List[Dict], train_ratio: float = 0.8) -> Tuple[List[Dict], List[Dict]]:
        """Разделяет данные на обучающую и валидационную выборки"""
        logger.info("📊 Разделение на train/val...")
        
        # Перемешиваем данные
        random.shuffle(transcriptions)
        
        # Разделяем
        split_idx = int(len(transcriptions) * train_ratio)
        train_data = transcriptions[:split_idx]
        val_data = transcriptions[split_idx:]
        
        logger.info(f"📊 Train: {len(train_data)}, Val: {len(val_data)}")
        return train_data, val_data
    
    def save_metadata(self, train_data: List[Dict], val_data: List[Dict]):
        """Сохраняет метаданные в нужном формате"""
        logger.info("💾 Сохранение метаданных...")
        
        # Формат для Coqui TTS
        train_metadata = []
        val_metadata = []
        
        for item in train_data:
            train_metadata.append(f"{item['file']}|{item['text']}")
        
        for item in val_data:
            val_metadata.append(f"{item['file']}|{item['text']}")
        
        # Сохраняем файлы
        train_file = self.metadata_dir / "train_metadata.csv"
        val_file = self.metadata_dir / "val_metadata.csv"
        
        with open(train_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(train_metadata))
        
        with open(val_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(val_metadata))
        
        # Сохраняем статистику
        stats = {
            "total_files": len(train_data) + len(val_data),
            "train_files": len(train_data),
            "val_files": len(val_data),
            "total_duration": sum(item['duration'] for item in train_data + val_data),
            "avg_duration": sum(item['duration'] for item in train_data + val_data) / (len(train_data) + len(val_data))
        }
        
        stats_file = self.metadata_dir / "stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Метаданные сохранены:")
        logger.info(f"   Train: {train_file}")
        logger.info(f"   Val: {val_file}")
        logger.info(f"   Stats: {stats_file}")
        
        return stats
    
    def create_training_config(self, stats: Dict):
        """Создаёт конфигурационный файл для обучения"""
        logger.info("⚙️ Создание конфигурации обучения...")
        
        config = {
            "model_name": "tts_models/multilingual/multi-dataset/your_tts",
            "run_name": "voice_cloning_finetune",
            "run_description": "Fine-tuning YourTTS на пользовательских данных",
            "data_path": str(self.wav_dir),
            "train_metadata": str(self.metadata_dir / "train_metadata.csv"),
            "val_metadata": str(self.metadata_dir / "val_metadata.csv"),
            "stats": stats,
            "training_params": {
                "batch_size": 8,
                "epochs": 1000,
                "learning_rate": 1e-4,
                "save_step": 1000,
                "eval_step": 500,
                "save_n_checkpoints": 5,
                "save_best_after": 10000,
                "target_loss": 0.5,
                "print_step": 25,
                "print_eval": True,
                "mixed_precision": True,
                "output_path": "tts_train_output",
                "datasets": [
                    {
                        "name": "voice_cloning",
                        "path": str(self.wav_dir),
                        "meta_file_train": str(self.metadata_dir / "train_metadata.csv"),
                        "meta_file_val": str(self.metadata_dir / "val_metadata.csv"),
                        "language": "ru"
                    }
                ]
            }
        }
        
        config_file = self.output_dir / "training_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"⚙️ Конфигурация сохранена: {config_file}")
        return config_file
    
    def run_preparation(self) -> Dict:
        """Запускает полную подготовку данных"""
        logger.info("🚀 Начинаем подготовку данных для обучения...")
        
        # 1. Конвертация
        wav_files = self.convert_ogg_to_wav()
        
        if not wav_files:
            raise ValueError("Не удалось конвертировать файлы!")
        
        # 2. Создание транскрипций
        transcriptions = self.create_dummy_transcriptions(wav_files)
        
        # 3. Разделение данных
        train_data, val_data = self.split_train_val(transcriptions)
        
        # 4. Сохранение метаданных
        stats = self.save_metadata(train_data, val_data)
        
        # 5. Создание конфигурации
        config_file = self.create_training_config(stats)
        
        logger.info("🎉 Подготовка данных завершена!")
        
        return {
            "wav_files": wav_files,
            "train_data": train_data,
            "val_data": val_data,
            "stats": stats,
            "config_file": str(config_file)
        }

def main():
    """Основная функция"""
    print("🎤 Подготовка данных для дообучения модели синтеза речи")
    print("=" * 60)
    
    try:
        preparator = TrainingDataPreparator()
        results = preparator.run_preparation()
        
        print("\n📊 Результаты подготовки:")
        print(f"   📁 WAV файлов: {len(results['wav_files'])}")
        print(f"   📝 Train записей: {len(results['train_data'])}")
        print(f"   📝 Val записей: {len(results['val_data'])}")
        print(f"   ⏱️ Общая длительность: {results['stats']['total_duration']:.1f} сек")
        print(f"   ⏱️ Средняя длительность: {results['stats']['avg_duration']:.1f} сек")
        print(f"   ⚙️ Конфигурация: {results['config_file']}")
        
        print("\n🎯 Следующие шаги:")
        print("   1. Установить YourTTS: pip install TTS")
        print("   2. Запустить обучение:")
        print(f"      tts --config_path {results['config_file']}")
        print("   3. Дождаться завершения обучения")
        print("   4. Протестировать модель")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при подготовке данных: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 