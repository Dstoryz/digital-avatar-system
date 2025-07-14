#!/usr/bin/env python3
"""
Скрипт для обучения TTS модели
Запускать в виртуальном окружении: source ai_env/bin/activate
"""

import os
import sys
from pathlib import Path

def main():
    # Проверяем наличие TTS
    try:
        from TTS.api import TTS
        print("✅ TTS установлен")
    except ImportError:
        print("❌ TTS не установлен")
        print("💡 Установите: pip install TTS")
        return 1
    
    # Пути к данным
    metadata_path = "models/tts_data/metadata/metadata.csv"
    output_path = "models/tts_output"
    
    if not os.path.exists(metadata_path):
        print(f"❌ Метаданные не найдены: {metadata_path}")
        return 1
    
    print("🚀 Начинаем обучение TTS...")
    print("💡 Это может занять несколько часов")
    
    # Команда для обучения
    cmd = [
        sys.executable, "-m", "TTS.bin.train_tts",
        "--config_path", "models/tts_data/config.json",
        "--coqpit.datasets.0.path", metadata_path,
        "--coqpit.output_path", output_path,
        "--coqpit.audio.sample_rate", "22050",
        "--coqpit.training.batch_size", "8",  # Маленький batch для RTX 3060
        "--coqpit.training.epochs", "50",
        "--coqpit.training.mixed_precision", "True"
    ]
    
    print(" ".join(cmd))
    
    # Запускаем обучение
    os.system(" ".join(cmd))
    
    print("✅ Обучение завершено!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
