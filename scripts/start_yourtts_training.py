#!/usr/bin/env python3
"""
Скрипт для запуска обучения YourTTS на пользовательских данных
"""

import os
import subprocess
import json
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_training_config():
    """Создаёт конфигурацию для обучения YourTTS"""
    config = {
        "run_name": "voice_cloning_finetune",
        "run_description": "Fine-tuning YourTTS на пользовательских данных",
        "model": "tts_models/multilingual/multi-dataset/your_tts",
        "datasets": [
            {
                "name": "voice_cloning",
                "path": "training_data/wav",
                "meta_file_train": "training_data/metadata/train_metadata.csv",
                "meta_file_val": "training_data/metadata/val_metadata.csv",
                "language": "en"  # YourTTS поддерживает только en, fr-fr, pt-br
            }
        ],
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
            "output_path": "tts_train_output"
        }
    }
    
    config_path = "training_data/yourtts_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Конфигурация сохранена: {config_path}")
    return config_path

def start_training(config_path):
    """Запускает обучение YourTTS"""
    logger.info("🚀 Запуск обучения YourTTS...")
    
    cmd = [
        "python", "-m", "TTS.bin.train_tts",
        "--config_path", config_path,
        "--coqpit.datasets.0.path", "training_data/wav",
        "--coqpit.datasets.0.meta_file_train", "training_data/metadata/train_metadata.csv",
        "--coqpit.datasets.0.meta_file_val", "training_data/metadata/val_metadata.csv",
        "--coqpit.training_params.batch_size", "8",
        "--coqpit.training_params.epochs", "1000",
        "--coqpit.training_params.learning_rate", "1e-4",
        "--coqpit.training_params.save_step", "1000",
        "--coqpit.training_params.eval_step", "500",
        "--coqpit.training_params.print_step", "25",
        "--coqpit.training_params.mixed_precision", "true",
        "--coqpit.output_path", "tts_train_output"
    ]
    
    logger.info(f"Команда: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        logger.info("✅ Обучение завершено успешно!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Ошибка при обучении: {e}")
        return False

def main():
    """Основная функция"""
    logger.info("🎤 Запуск обучения YourTTS на пользовательских данных")
    logger.info("=" * 60)
    
    # Проверяем наличие данных
    if not Path("training_data/wav").exists():
        logger.error("❌ Папка training_data/wav не найдена!")
        return False
    
    if not Path("training_data/metadata/train_metadata.csv").exists():
        logger.error("❌ Файл train_metadata.csv не найден!")
        return False
    
    # Создаём конфигурацию
    config_path = create_training_config()
    
    # Запускаем обучение
    success = start_training(config_path)
    
    if success:
        logger.info("🎉 Обучение YourTTS завершено успешно!")
        logger.info("📁 Результаты сохранены в: tts_train_output/")
        logger.info("🎤 Модель готова к использованию!")
    else:
        logger.error("❌ Обучение завершилось с ошибкой!")
    
    return success

if __name__ == "__main__":
    main() 