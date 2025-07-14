#!/usr/bin/env python3
"""
Скрипт для обучения TTS модели на аудиосэмплах пользователя
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import librosa
import soundfile as sf

def setup_tts_environment():
    """Настраивает окружение для TTS"""
    print("🔧 Настройка окружения для TTS...")
    
    # Создаем директории
    os.makedirs("models/tts_data", exist_ok=True)
    os.makedirs("models/tts_data/wavs", exist_ok=True)
    os.makedirs("models/tts_data/metadata", exist_ok=True)
    os.makedirs("models/tts_output", exist_ok=True)
    
    print("✅ Директории созданы")

def convert_ogg_to_wav():
    """Конвертирует OGG файлы в WAV"""
    print("🔄 Конвертация OGG в WAV...")
    
    input_dir = Path("data/audio")
    output_dir = Path("models/tts_data/wavs")
    
    if not input_dir.exists():
        print("❌ Директория с аудио не найдена")
        return False
    
    ogg_files = list(input_dir.glob("*.ogg"))
    if not ogg_files:
        print("❌ OGG файлы не найдены")
        return False
    
    converted_count = 0
    for ogg_file in ogg_files:
        wav_file = output_dir / f"{ogg_file.stem}.wav"
        
        try:
            # Загружаем аудио
            y, sr = librosa.load(ogg_file, sr=22050)
            
            # Нормализуем громкость
            y = librosa.util.normalize(y)
            
            # Сохраняем как WAV
            sf.write(wav_file, y, sr)
            converted_count += 1
            
            print(f"✅ {ogg_file.name} -> {wav_file.name}")
            
        except Exception as e:
            print(f"❌ Ошибка конвертации {ogg_file.name}: {e}")
    
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
    
    # Создаем простые метаданные
    metadata_lines = []
    for wav_file in wav_files:
        # Получаем длительность
        y, sr = librosa.load(wav_file, sr=22050)
        duration = len(y) / sr
        
        # Простой текст для каждого файла
        text = "Привет, это тестовый аудиосэмпл для обучения TTS модели."
        
        # Формат: filename|text|normalized_text
        line = f"{wav_file.name}|{text}|{text}"
        metadata_lines.append(line)
    
    # Сохраняем метаданные
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(metadata_lines))
    
    print(f"✅ Созданы метаданные для {len(wav_files)} файлов")
    return True

def create_tts_config():
    """Создает конфигурацию для TTS"""
    print("⚙️ Создание конфигурации TTS...")
    
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
            "batch_size": 32,
            "eval_batch_size": 16,
            "num_loader_workers": 4,
            "num_eval_loader_workers": 4,
            "run_eval": True,
            "test_delay_epochs": -1,
            "epochs": 1000,
            "text_cleaner": "multilingual_cleaners",
            "use_phonemes": False,
            "phoneme_language": "ru",
            "phoneme_cache_path": "models/tts_data/phoneme_cache",
            "print_step": 25,
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
                "warmup_steps": 4000,
                "last_epoch": -1
            }
        }
    }
    
    config_file = Path("models/tts_data/config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Конфигурация создана")
    return True

def train_tts_model():
    """Запускает обучение TTS модели"""
    print("🚀 Запуск обучения TTS модели...")
    
    # Активируем виртуальное окружение
    env = os.environ.copy()
    env['PATH'] = f"{os.getcwd()}/ai_env/bin:{env['PATH']}"
    
    # Команда для обучения
    cmd = [
        "python", "-m", "TTS.bin.train_tts",
        "--config_path", "models/tts_data/config.json",
        "--coqpit.datasets.0.path", "models/tts_data/metadata/metadata.csv",
        "--coqpit.output_path", "models/tts_output",
        "--coqpit.audio.sample_rate", "22050",
        "--coqpit.training.batch_size", "16",  # Уменьшаем для RTX 3060
        "--coqpit.training.epochs", "100",
        "--coqpit.training.mixed_precision", "True"
    ]
    
    try:
        print("⏳ Начинаем обучение...")
        print("💡 Это может занять несколько часов")
        print("💡 Нажмите Ctrl+C для остановки")
        
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Выводим логи в реальном времени
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print("✅ Обучение завершено успешно!")
            return True
        else:
            print("❌ Ошибка при обучении")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️ Обучение прервано пользователем")
        process.terminate()
        return False
    except Exception as e:
        print(f"❌ Ошибка запуска обучения: {e}")
        return False

def test_trained_model():
    """Тестирует обученную модель"""
    print("🧪 Тестирование обученной модели...")
    
    # Ищем обученную модель
    model_dir = Path("models/tts_output")
    if not model_dir.exists():
        print("❌ Директория с моделью не найдена")
        return False
    
    # Ищем checkpoint
    checkpoints = list(model_dir.rglob("*.pth"))
    if not checkpoints:
        print("❌ Checkpoint не найден")
        return False
    
    latest_checkpoint = max(checkpoints, key=lambda x: x.stat().st_mtime)
    print(f"✅ Найден checkpoint: {latest_checkpoint}")
    
    # Тестовый синтез
    test_text = "Привет, это тест обученной TTS модели."
    test_file = "models/tts_output/test_synthesis.wav"
    
    try:
        from TTS.api import TTS
        
        # Загружаем модель
        tts = TTS(model_path=str(latest_checkpoint))
        
        # Синтезируем речь
        tts.tts_to_file(
            text=test_text,
            file_path=test_file,
            speaker_wav="models/tts_data/wavs/audio_001.wav"  # Референсный голос
        )
        
        print(f"✅ Тестовый синтез сохранен в {test_file}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def main():
    """Основная функция"""
    print("🎤 Обучение TTS модели на пользовательских аудиосэмплах")
    print("=" * 60)
    
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
    
    # Настройка окружения
    if not setup_tts_environment():
        return 1
    
    # Конвертация аудио
    if not convert_ogg_to_wav():
        return 1
    
    # Создание метаданных
    if not create_metadata():
        return 1
    
    # Создание конфигурации
    if not create_tts_config():
        return 1
    
    # Обучение модели
    print("\n🎯 Готов к обучению!")
    print("💡 Рекомендуется:")
    print("   - Минимум 10-20 аудиосэмплов")
    print("   - Качество записи 16kHz+")
    print("   - Разная интонация и эмоции")
    print("   - Чистая речь без шумов")
    
    response = input("\n🤔 Начать обучение? (y/n): ").lower().strip()
    if response != 'y':
        print("❌ Обучение отменено")
        return 0
    
    # Запуск обучения
    if train_tts_model():
        # Тестирование модели
        test_trained_model()
        
        print("\n🎉 Обучение завершено!")
        print("📁 Модель сохранена в models/tts_output/")
        print("💡 Используйте для синтеза речи в приложении")
        
        return 0
    else:
        print("\n❌ Обучение не завершено")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 