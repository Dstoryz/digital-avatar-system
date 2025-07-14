#!/usr/bin/env python3
"""
Скрипт для подготовки данных TTS
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def setup_directories():
    """Создает необходимые директории"""
    print("🔧 Создание директорий...")
    
    dirs = [
        "models/tts_data",
        "models/tts_data/wavs", 
        "models/tts_data/metadata",
        "models/tts_output"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ {dir_path}")
    
    return True

def convert_audio_files():
    """Конвертирует аудиофайлы с помощью FFmpeg"""
    print("🔄 Конвертация аудиофайлов...")
    
    input_dir = Path("data/audio")
    output_dir = Path("models/tts_data/wavs")
    
    if not input_dir.exists():
        print("❌ Директория data/audio не найдена")
        return False
    
    ogg_files = list(input_dir.glob("*.ogg"))
    if not ogg_files:
        print("❌ OGG файлы не найдены")
        return False
    
    converted_count = 0
    for ogg_file in ogg_files:
        wav_file = output_dir / f"{ogg_file.stem}.wav"
        
        try:
            # Конвертируем с помощью FFmpeg
            cmd = [
                "ffmpeg", "-i", str(ogg_file),
                "-ar", "22050",  # Sample rate
                "-ac", "1",      # Mono
                "-y",            # Overwrite
                str(wav_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {ogg_file.name} -> {wav_file.name}")
                converted_count += 1
            else:
                print(f"❌ Ошибка конвертации {ogg_file.name}")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print(f"✅ Конвертировано {converted_count} файлов")
    return converted_count > 0

def create_metadata():
    """Создает метаданные для обучения"""
    print("📝 Создание метаданных...")
    
    wav_dir = Path("models/tts_data/wavs")
    metadata_file = Path("models/tts_data/metadata/metadata.csv")
    
    if not wav_dir.exists():
        print("❌ Директория с WAV файлами не найдена")
        return False
    
    wav_files = list(wav_dir.glob("*.wav"))
    if not wav_files:
        print("❌ WAV файлы не найдены")
        return False
    
    # Создаем метаданные
    metadata_lines = []
    sample_texts = [
        "Привет, это тестовый аудиосэмпл для обучения TTS модели.",
        "Здравствуйте, сегодня прекрасный день для обучения.",
        "Добро пожаловать в мир искусственного интеллекта.",
        "Это голос, который мы будем клонировать.",
        "Технологии синтеза речи развиваются очень быстро.",
        "Наша модель будет говорить как вы.",
        "Качество синтеза зависит от качества данных.",
        "Чем больше образцов, тем лучше результат.",
        "Искусственный интеллект меняет мир.",
        "Будущее уже наступило."
    ]
    
    for i, wav_file in enumerate(wav_files):
        # Выбираем текст по кругу
        text = sample_texts[i % len(sample_texts)]
        
        # Формат: filename|text|normalized_text
        line = f"{wav_file.name}|{text}|{text}"
        metadata_lines.append(line)
    
    # Сохраняем метаданные
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(metadata_lines))
    
    print(f"✅ Созданы метаданные для {len(wav_files)} файлов")
    return True

def create_training_script():
    """Создает скрипт для обучения"""
    print("📜 Создание скрипта обучения...")
    
    script_content = '''#!/usr/bin/env python3
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
'''
    
    script_file = Path("scripts/train_tts_model.py")
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Делаем исполняемым
    os.chmod(script_file, 0o755)
    
    print("✅ Скрипт обучения создан: scripts/train_tts_model.py")
    return True

def create_config():
    """Создает базовую конфигурацию"""
    print("⚙️ Создание конфигурации...")
    
    config = {
        "model": "tts_models/multilingual/multi-dataset/your_tts",
        "run_name": "custom_voice_training",
        "run_description": "Обучение TTS на пользовательских аудиосэмплах",
        
        "audio": {
            "sample_rate": 22050,
            "max_wav_value": 32768.0,
            "mel_channels": 80,
            "mel_fmin": 0.0,
            "mel_fmax": 8000.0,
            "hop_length": 256,
            "win_length": 1024,
            "fft_size": 1024,
            "preemphasis": 0.0,
            "ref_level_db": 20,
            "signal_norm": True,
            "symmetric_norm": True,
            "max_norm": 4.0,
            "clip_norm": True,
            "griffin_lim_iters": 60,
            "do_trim_silence": True,
            "trim_silence_threshold": 0.1,
            "trim_silence_ratio": 0.5,
        },
        
        "training": {
            "batch_size": 8,  # Уменьшено для RTX 3060
            "eval_batch_size": 4,
            "num_loader_workers": 2,
            "num_eval_loader_workers": 2,
            "run_eval": True,
            "test_delay_epochs": -1,
            "epochs": 50,
            "text_cleaner": "multilingual_cleaners",
            "use_phonemes": False,
            "phoneme_language": "ru",
            "phoneme_cache_path": "models/tts_data/phoneme_cache",
            "print_step": 10,
            "print_eval": True,
            "mixed_precision": True,
            "output_path": "models/tts_output",
            "datasets": [
                {
                    "name": "custom_voice",
                    "path": "models/tts_data/metadata/metadata.csv",
                    "meta_file_train": "",
                    "meta_file_val": ""
                }
            ]
        },
        
        "optimizer": {
            "type": "AdamW",
            "params": {
                "lr": 0.001,
                "weight_decay": 0.01,
                "betas": [0.9, 0.998]
            }
        },
        
        "scheduler": {
            "type": "NoamLR",
            "params": {
                "warmup_steps": 1000,
                "last_epoch": -1
            }
        }
    }
    
    config_file = Path("models/tts_data/config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Конфигурация создана")
    return True

def main():
    """Основная функция"""
    print("🎤 Подготовка данных для обучения TTS")
    print("=" * 50)
    
    # Проверяем наличие аудиофайлов
    audio_dir = Path("data/audio")
    if not audio_dir.exists():
        print("❌ Директория data/audio не найдена")
        print("💡 Убедитесь, что аудиофайлы находятся в data/audio/")
        return 1
    
    ogg_files = list(audio_dir.glob("*.ogg"))
    if not ogg_files:
        print("❌ OGG файлы не найдены в data/audio/")
        return 1
    
    print(f"📁 Найдено {len(ogg_files)} аудиофайлов")
    
    # Создаем директории
    if not setup_directories():
        return 1
    
    # Конвертируем аудио
    if not convert_audio_files():
        return 1
    
    # Создаем метаданные
    if not create_metadata():
        return 1
    
    # Создаем конфигурацию
    if not create_config():
        return 1
    
    # Создаем скрипт обучения
    if not create_training_script():
        return 1
    
    print("\n🎉 Подготовка данных завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Установите TTS: pip install TTS")
    print("2. Активируйте окружение: source ai_env/bin/activate")
    print("3. Запустите обучение: python scripts/train_tts_model.py")
    print("\n💡 Рекомендации:")
    print("   - Минимум 10-20 аудиосэмплов")
    print("   - Качество записи 16kHz+")
    print("   - Разная интонация и эмоции")
    print("   - Чистая речь без шумов")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 