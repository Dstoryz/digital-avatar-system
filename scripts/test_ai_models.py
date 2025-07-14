#!/usr/bin/env python3
"""
Скрипт для тестирования установленных AI моделей
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def test_pytorch_cuda():
    """Тестирует PyTorch с CUDA поддержкой"""
    try:
        import torch
        print(f"✅ PyTorch версия: {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA доступен: {torch.cuda.get_device_name(0)}")
            print(f"✅ CUDA версия: {torch.version.cuda}")
            print(f"✅ GPU память: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            return True
        else:
            print("❌ CUDA недоступен")
            return False
    except ImportError:
        print("❌ PyTorch не установлен")
        return False

def test_whisper():
    """Тестирует Whisper"""
    try:
        import whisper
        print(f"✅ Whisper установлен: {whisper.__version__}")
        
        # Тестируем загрузку модели
        model = whisper.load_model("tiny")
        print("✅ Whisper модель загружена успешно")
        return True
    except ImportError:
        print("❌ Whisper не установлен")
        return False
    except Exception as e:
        print(f"❌ Ошибка Whisper: {e}")
        return False

def test_transformers():
    """Тестирует Transformers"""
    try:
        import transformers
        print(f"✅ Transformers установлен: {transformers.__version__}")
        
        # Тестируем загрузку токенизатора
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        print("✅ Transformers токенизатор загружен")
        return True
    except ImportError:
        print("❌ Transformers не установлен")
        return False
    except Exception as e:
        print(f"❌ Ошибка Transformers: {e}")
        return False

def test_librosa():
    """Тестирует Librosa"""
    try:
        import librosa
        print(f"✅ Librosa установлен: {librosa.__version__}")
        
        # Тестируем базовые функции
        import numpy as np
        y = np.random.random(22050)  # 1 секунда аудио
        sr = librosa.get_samplerate("test.wav") if os.path.exists("test.wav") else 22050
        print("✅ Librosa функции работают")
        return True
    except ImportError:
        print("❌ Librosa не установлен")
        return False
    except Exception as e:
        print(f"❌ Ошибка Librosa: {e}")
        return False

def test_soundfile():
    """Тестирует SoundFile"""
    try:
        import soundfile as sf
        print(f"✅ SoundFile установлен: {sf.__version__}")
        
        # Тестируем запись/чтение
        import numpy as np
        data = np.random.random(22050)
        sf.write("test.wav", data, 22050)
        data_read, sr = sf.read("test.wav")
        print("✅ SoundFile работает")
        
        # Удаляем тестовый файл
        if os.path.exists("test.wav"):
            os.remove("test.wav")
        return True
    except ImportError:
        print("❌ SoundFile не установлен")
        return False
    except Exception as e:
        print(f"❌ Ошибка SoundFile: {e}")
        return False

def test_espeak():
    """Тестирует eSpeak"""
    try:
        result = subprocess.run(["espeak-ng", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ eSpeak установлен: {result.stdout.strip()}")
            return True
        else:
            print("❌ eSpeak не работает")
            return False
    except FileNotFoundError:
        print("❌ eSpeak не установлен")
        return False

def test_ffmpeg():
    """Тестирует FFmpeg"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg установлен: {version_line}")
            return True
        else:
            print("❌ FFmpeg не работает")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg не установлен")
        return False

def test_redis():
    """Тестирует Redis"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis работает")
        return True
    except ImportError:
        print("❌ Redis Python клиент не установлен")
        return False
    except Exception as e:
        print(f"❌ Ошибка Redis: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование AI моделей и зависимостей")
    print("=" * 50)
    
    results = {}
    
    # Тестируем основные компоненты
    print("\n📋 Тестирование PyTorch и CUDA")
    print("-" * 30)
    results['pytorch_cuda'] = test_pytorch_cuda()
    
    print("\n📋 Тестирование Whisper")
    print("-" * 30)
    results['whisper'] = test_whisper()
    
    print("\n📋 Тестирование Transformers")
    print("-" * 30)
    results['transformers'] = test_transformers()
    
    print("\n📋 Тестирование Librosa")
    print("-" * 30)
    results['librosa'] = test_librosa()
    
    print("\n📋 Тестирование SoundFile")
    print("-" * 30)
    results['soundfile'] = test_soundfile()
    
    print("\n📋 Тестирование eSpeak")
    print("-" * 30)
    results['espeak'] = test_espeak()
    
    print("\n📋 Тестирование FFmpeg")
    print("-" * 30)
    results['ffmpeg'] = test_ffmpeg()
    
    print("\n📋 Тестирование Redis")
    print("-" * 30)
    results['redis'] = test_redis()
    
    # Подсчитываем результаты
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print("\n📊 Результаты тестирования")
    print("=" * 50)
    print(f"✅ Пройдено: {passed_tests}/{total_tests}")
    print(f"❌ Провалено: {total_tests - passed_tests}/{total_tests}")
    print(f"📈 Успешность: {passed_tests/total_tests*100:.1f}%")
    
    # Сохраняем отчет
    report = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'summary': {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': passed_tests/total_tests*100
        }
    }
    
    with open('ai_models_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Отчет сохранен в ai_models_test_report.json")
    
    if passed_tests == total_tests:
        print("\n🎉 Все тесты пройдены! AI модели готовы к работе.")
        return 0
    else:
        print("\n⚠️  Некоторые тесты провалены. Проверьте установку.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 