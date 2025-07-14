#!/usr/bin/env python3
"""
Скрипт для обучения Coqui TTS на аудиосэмплах девочки
Создает клонированный голос для цифрового аватара
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VoiceCloner:
    """Класс для клонирования голоса с помощью Coqui TTS"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.audio_dir = self.project_root / "uploads" / "audio"
        self.models_dir = self.project_root / "models"
        self.coqui_dir = self.models_dir / "coqui_tts"
        self.training_dir = self.project_root / "training"
        self.output_dir = self.project_root / "models" / "voice_clone"
        
        # Создаем необходимые директории
        self.training_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Конфигурация обучения
        self.training_config = {
            "model_name": "voice_clone",
            "language": "ru",
            "speaker_name": "girl_avatar",
            "sample_rate": 22050,
            "max_audio_length": 10.0,  # секунды
            "min_audio_length": 1.0,   # секунды
            "epochs": 1000,
            "batch_size": 8,
            "learning_rate": 0.001,
            "validation_split": 0.1
        }
    
    def print_header(self, title: str):
        """Вывод заголовка"""
        print(f"\n{'='*60}")
        print(f"🎤 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str):
        """Вывод шага"""
        print(f"\n📋 {step}")
        print("-" * 40)
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> bool:
        """Выполнение команды"""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                check=True
            )
            logger.info(f"Команда выполнена успешно: {' '.join(command)}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка выполнения команды: {e.stderr}")
            return False
    
    def prepare_audio_data(self) -> bool:
        """Подготовка аудиоданных для обучения"""
        self.print_step("Подготовка аудиоданных")
        
        if not self.audio_dir.exists():
            logger.error(f"Папка с аудио не найдена: {self.audio_dir}")
            return False
        
        # Создаем папку для подготовленных данных
        prepared_dir = self.training_dir / "prepared_audio"
        prepared_dir.mkdir(exist_ok=True)
        
        # Конвертируем OGG в WAV и нормализуем
        audio_files = list(self.audio_dir.glob("*.ogg"))
        logger.info(f"Найдено {len(audio_files)} аудиофайлов")
        
        converted_count = 0
        for audio_file in audio_files:
            output_file = prepared_dir / f"{audio_file.stem}.wav"
            
            # Конвертируем в WAV с нужными параметрами
            success = self.run_command([
                "ffmpeg", "-i", str(audio_file),
                "-ar", str(self.training_config["sample_rate"]),
                "-ac", "1",  # моно
                "-f", "wav",
                str(output_file)
            ])
            
            if success:
                converted_count += 1
                logger.info(f"Конвертирован: {audio_file.name}")
            else:
                logger.warning(f"Ошибка конвертации: {audio_file.name}")
        
        logger.info(f"Конвертировано {converted_count}/{len(audio_files)} файлов")
        return converted_count > 0
    
    def create_metadata(self) -> bool:
        """Создание метаданных для обучения"""
        self.print_step("Создание метаданных")
        
        prepared_dir = self.training_dir / "prepared_audio"
        metadata_file = self.training_dir / "metadata.csv"
        
        # Получаем список WAV файлов
        wav_files = list(prepared_dir.glob("*.wav"))
        
        if not wav_files:
            logger.error("Не найдены WAV файлы для обучения")
            return False
        
        # Создаем метаданные
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write("filename|text|speaker_name\n")
            
            for wav_file in wav_files:
                # Для клонирования голоса используем простой текст
                # В реальном проекте здесь должен быть транскрибированный текст
                text = "Привет, как дела?"
                speaker = self.training_config["speaker_name"]
                
                f.write(f"{wav_file.name}|{text}|{speaker}\n")
        
        logger.info(f"Создан файл метаданных: {metadata_file}")
        logger.info(f"Добавлено {len(wav_files)} записей")
        return True
    
    def create_training_config(self) -> bool:
        """Создание конфигурации для обучения"""
        self.print_step("Создание конфигурации обучения")
        
        config = {
            "model": "tts_models/multilingual/multi-dataset/your_tts",
            "run_name": self.training_config["model_name"],
            "run_description": "Voice cloning for digital avatar",
            
            "audio": {
                "sample_rate": self.training_config["sample_rate"],
                "max_audio_length": self.training_config["max_audio_length"],
                "min_audio_length": self.training_config["min_audio_length"]
            },
            
            "training": {
                "epochs": self.training_config["epochs"],
                "batch_size": self.training_config["batch_size"],
                "learning_rate": self.training_config["learning_rate"],
                "validation_split": self.training_config["validation_split"],
                "save_step": 100,
                "print_step": 10,
                "save_n_checkpoints": 5,
                "save_best_after": 1000,
                "target_loss": 0.5,
                "print_eval": True,
                "mixed_precision": True,
                "distributed_backend": "nccl",
                "distributed_url": "tcp://localhost:54321"
            },
            
            "paths": {
                "output_path": str(self.output_dir),
                "data_path": str(self.training_dir / "prepared_audio"),
                "meta_file_train": str(self.training_dir / "metadata.csv")
            }
        }
        
        config_file = self.training_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Конфигурация сохранена: {config_file}")
        return True
    
    def start_training(self) -> bool:
        """Запуск обучения"""
        self.print_step("Запуск обучения модели")
        
        if not self.coqui_dir.exists():
            logger.error("Coqui TTS не установлен")
            return False
        
        # Переходим в папку Coqui TTS
        os.chdir(self.coqui_dir)
        
        # Запускаем обучение
        training_command = [
            sys.executable, "TTS/bin/train_tts.py",
            "--config_path", str(self.training_dir / "config.json")
        ]
        
        logger.info("Запуск обучения...")
        logger.info(f"Команда: {' '.join(training_command)}")
        
        success = self.run_command(training_command, cwd=self.coqui_dir)
        
        # Возвращаемся в корневую папку
        os.chdir(self.project_root)
        
        if success:
            logger.info("✅ Обучение завершено успешно")
            return True
        else:
            logger.error("❌ Ошибка обучения")
            return False
    
    def test_voice_clone(self) -> bool:
        """Тестирование клонированного голоса"""
        self.print_step("Тестирование клонированного голоса")
        
        # Находим лучшую модель
        model_files = list(self.output_dir.glob("*.pth"))
        if not model_files:
            logger.error("Модели не найдены")
            return False
        
        # Берем последнюю модель
        best_model = max(model_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"Используем модель: {best_model}")
        
        # Создаем тестовый скрипт
        test_script = self.training_dir / "test_voice.py"
        
        test_code = f'''
import sys
import os
sys.path.append("{self.coqui_dir}")

from TTS.api import TTS

# Загружаем модель
tts = TTS(model_path="{best_model}")

# Тестовый текст
text = "Привет! Я цифровой аватар. Как дела?"

# Генерируем речь
output_path = "{self.output_dir}/test_output.wav"
tts.tts_to_file(text=text, file_path=output_path, speaker="{self.training_config['speaker_name']}")

print(f"Тестовый аудио сохранен: {{output_path}}")
'''
        
        with open(test_script, 'w') as f:
            f.write(test_code)
        
        # Запускаем тест
        success = self.run_command([
            sys.executable, str(test_script)
        ])
        
        if success:
            logger.info("✅ Тест голоса выполнен успешно")
            return True
        else:
            logger.error("❌ Ошибка тестирования")
            return False
    
    def create_voice_config(self) -> bool:
        """Создание конфигурации голоса"""
        self.print_step("Создание конфигурации голоса")
        
        # Находим лучшую модель
        model_files = list(self.output_dir.glob("*.pth"))
        if model_files:
            best_model = max(model_files, key=lambda x: x.stat().st_mtime)
        else:
            best_model = None
        
        voice_config = {
            "voice_clone": {
                "enabled": True,
                "model_path": str(best_model) if best_model else None,
                "speaker_name": self.training_config["speaker_name"],
                "language": self.training_config["language"],
                "sample_rate": self.training_config["sample_rate"],
                "training_info": {
                    "epochs": self.training_config["epochs"],
                    "batch_size": self.training_config["batch_size"],
                    "learning_rate": self.training_config["learning_rate"],
                    "audio_files_used": len(list((self.training_dir / "prepared_audio").glob("*.wav")))
                }
            }
        }
        
        config_file = self.output_dir / "voice_config.json"
        with open(config_file, 'w') as f:
            json.dump(voice_config, f, indent=2)
        
        logger.info(f"Конфигурация голоса сохранена: {config_file}")
        return True
    
    def run_voice_cloning(self) -> None:
        """Запуск полного процесса клонирования голоса"""
        self.print_header("КЛОНИРОВАНИЕ ГОЛОСА ДЛЯ ЦИФРОВОГО АВАТАРА")
        
        results = {}
        
        # Подготовка данных
        results["Подготовка аудио"] = self.prepare_audio_data()
        results["Создание метаданных"] = self.create_metadata()
        results["Конфигурация обучения"] = self.create_training_config()
        
        # Обучение (может занять много времени)
        print("\n⚠️  ВНИМАНИЕ: Обучение может занять несколько часов!")
        print("   Рекомендуется использовать GPU для ускорения")
        
        user_input = input("\nПродолжить обучение? (y/n): ")
        if user_input.lower() == 'y':
            results["Обучение модели"] = self.start_training()
            results["Тестирование голоса"] = self.test_voice_clone()
        else:
            results["Обучение модели"] = False
            results["Тестирование голоса"] = False
            print("Обучение пропущено")
        
        results["Конфигурация голоса"] = self.create_voice_config()
        
        # Отчет
        self.print_step("Отчет о клонировании голоса")
        
        print("\n📊 Результаты:")
        for step, status in results.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {step}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"\n🎯 Общий результат: {success_count}/{total_count} этапов выполнено")
        
        if success_count == total_count:
            print("🎉 Голос успешно клонирован!")
        else:
            print("⚠️  Некоторые этапы не выполнены")
        
        # Сохраняем отчет
        with open("voice_cloning_report.json", "w") as f:
            json.dump({
                "results": results,
                "training_config": self.training_config,
                "output_dir": str(self.output_dir),
                "total_steps": total_count,
                "successful_steps": success_count
            }, f, indent=2)
        
        print(f"\n💾 Отчет сохранен в voice_cloning_report.json")

def main():
    """Основная функция"""
    cloner = VoiceCloner()
    cloner.run_voice_cloning()

if __name__ == "__main__":
    main() 