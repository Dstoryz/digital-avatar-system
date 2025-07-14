#!/usr/bin/env python3
"""
Скрипт для установки и настройки YourTTS
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Выполняет команду с выводом"""
    print(f"🔄 {description}...")
    print(f"   Команда: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} завершено успешно")
            if result.stdout:
                print(f"   Вывод: {result.stdout.strip()}")
        else:
            print(f"❌ Ошибка при {description.lower()}:")
            print(f"   {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение при {description.lower()}: {e}")
        return False
    
    return True

def check_gpu():
    """Проверяет доступность GPU"""
    print("🔍 Проверка GPU...")
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            
            print(f"✅ GPU доступен:")
            print(f"   Количество: {gpu_count}")
            print(f"   Модель: {gpu_name}")
            print(f"   Память: {gpu_memory:.1f} GB")
            
            if gpu_memory < 8:
                print("⚠️  Внимание: Рекомендуется GPU с 8GB+ VRAM")
            
            return True
        else:
            print("❌ GPU недоступен")
            return False
            
    except ImportError:
        print("❌ PyTorch не установлен")
        return False

def setup_environment():
    """Настраивает виртуальное окружение"""
    print("🚀 Настройка окружения для YourTTS...")
    
    # Создание виртуального окружения
    if not run_command([sys.executable, "-m", "venv", "yourtts_env"], 
                      "Создание виртуального окружения"):
        return False
    
    # Активация окружения (для Linux)
    activate_script = "yourtts_env/bin/activate"
    if not os.path.exists(activate_script):
        print("❌ Не удалось найти скрипт активации")
        return False
    
    print("✅ Виртуальное окружение создано")
    return True

def install_dependencies():
    """Устанавливает зависимости"""
    print("📦 Установка зависимостей...")
    
    # Обновление pip
    if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      "Обновление pip"):
        return False
    
    # Установка PyTorch с CUDA
    if not run_command([sys.executable, "-m", "pip", "install", 
                       "torch", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu118"], 
                      "Установка PyTorch"):
        return False
    
    # Установка TTS
    if not run_command([sys.executable, "-m", "pip", "install", "TTS"], 
                      "Установка Coqui TTS"):
        return False
    
    # Установка дополнительных зависимостей
    additional_packages = [
        "transformers",
        "datasets",
        "accelerate",
        "wandb",
        "tensorboard",
        "librosa",
        "soundfile"
    ]
    
    for package in additional_packages:
        if not run_command([sys.executable, "-m", "pip", "install", package], 
                          f"Установка {package}"):
            return False
    
    return True

def download_pretrained_model():
    """Скачивает предобученную модель YourTTS"""
    print("📥 Скачивание предобученной модели YourTTS...")
    
    try:
        from TTS.api import TTS
        
        # Инициализация TTS для скачивания модели
        tts = TTS("tts_models/multilingual/multi-dataset/your_tts")
        
        print("✅ Модель YourTTS готова к использованию")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при скачивании модели: {e}")
        return False

def create_training_script():
    """Создаёт скрипт для запуска обучения"""
    print("📝 Создание скрипта обучения...")
    
    training_script = """#!/usr/bin/env python3
\"\"\"
Скрипт для запуска обучения YourTTS
\"\"\"

import os
import sys
from pathlib import Path

def main():
    # Активация виртуального окружения
    activate_script = "yourtts_env/bin/activate"
    if os.path.exists(activate_script):
        print("✅ Виртуальное окружение активировано")
    else:
        print("❌ Виртуальное окружение не найдено")
        return 1
    
    # Проверка наличия данных
    config_file = "training_data/training_config.json"
    if not os.path.exists(config_file):
        print(f"❌ Конфигурационный файл не найден: {config_file}")
        return 1
    
    print("🚀 Запуск обучения YourTTS...")
    print("⏱️  Ожидаемое время: 4-8 часов")
    print("💾 Результаты будут сохранены в tts_train_output/")
    
    # Команда для обучения
    cmd = [
        sys.executable, "-m", "TTS.bin.train_tts",
        "--config_path", config_file,
        "--coqpit.datasets.0.path", "training_data/wav",
        "--coqpit.datasets.0.meta_file_train", "training_data/metadata/train_metadata.csv",
        "--coqpit.datasets.0.meta_file_val", "training_data/metadata/val_metadata.csv"
    ]
    
    print(f"Команда: {' '.join(cmd)}")
    
    try:
        import subprocess
        result = subprocess.run(cmd)
        return result.returncode
    except Exception as e:
        print(f"❌ Ошибка при запуске обучения: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
"""
    
    with open("scripts/start_training.py", "w", encoding="utf-8") as f:
        f.write(training_script)
    
    # Делаем скрипт исполняемым
    os.chmod("scripts/start_training.py", 0o755)
    
    print("✅ Скрипт обучения создан: scripts/start_training.py")
    return True

def create_test_script():
    """Создаёт скрипт для тестирования обученной модели"""
    print("📝 Создание скрипа тестирования...")
    
    test_script = """#!/usr/bin/env python3
\"\"\"
Скрипт для тестирования обученной модели YourTTS
\"\"\"

import os
import sys
from pathlib import Path

def main():
    # Проверка наличия обученной модели
    model_path = "tts_train_output/best_model.pth"
    if not os.path.exists(model_path):
        print(f"❌ Обученная модель не найдена: {model_path}")
        return 1
    
    print("🎤 Тестирование обученной модели...")
    
    # Тестовые фразы
    test_phrases = [
        "Привет! Как дела?",
        "Сегодня прекрасная погода.",
        "Я очень рада вас видеть.",
        "Спасибо за внимание.",
        "До свидания!"
    ]
    
    try:
        from TTS.api import TTS
        
        # Загрузка обученной модели
        tts = TTS(model_path=model_path)
        
        # Создание директории для результатов
        output_dir = Path("test_results")
        output_dir.mkdir(exist_ok=True)
        
        for i, phrase in enumerate(test_phrases, 1):
            output_file = output_dir / f"test_{i:02d}.wav"
            
            print(f"Синтезируем {i}/{len(test_phrases)}: '{phrase}'")
            
            # Синтез речи
            tts.tts_to_file(
                text=phrase,
                file_path=str(output_file),
                speaker_wav="training_data/wav/audio_104@04-11-2021_22-32-49.wav",
                language="ru"
            )
            
            print(f"✅ Сохранено: {output_file}")
        
        print("🎉 Тестирование завершено!")
        print(f"📁 Результаты: {output_dir}")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
"""
    
    with open("scripts/test_trained_model.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    # Делаем скрипт исполняемым
    os.chmod("scripts/test_trained_model.py", 0o755)
    
    print("✅ Скрипт тестирования создан: scripts/test_trained_model.py")
    return True

def main():
    """Основная функция"""
    print("🎤 Настройка YourTTS для дообучения")
    print("=" * 50)
    
    # Проверка GPU
    if not check_gpu():
        print("⚠️  Продолжение без GPU (будет медленнее)")
    
    # Настройка окружения
    if not setup_environment():
        print("❌ Не удалось настроить окружение")
        return 1
    
    # Установка зависимостей
    if not install_dependencies():
        print("❌ Не удалось установить зависимости")
        return 1
    
    # Скачивание модели
    if not download_pretrained_model():
        print("❌ Не удалось скачать модель")
        return 1
    
    # Создание скриптов
    if not create_training_script():
        print("❌ Не удалось создать скрипт обучения")
        return 1
    
    if not create_test_script():
        print("❌ Не удалось создать скрипт тестирования")
        return 1
    
    print("\n🎉 Настройка YourTTS завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Активировать окружение:")
    print("   source yourtts_env/bin/activate")
    print("2. Запустить обучение:")
    print("   python scripts/start_training.py")
    print("3. Дождаться завершения (4-8 часов)")
    print("4. Протестировать модель:")
    print("   python scripts/test_trained_model.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 