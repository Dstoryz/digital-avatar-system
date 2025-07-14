#!/usr/bin/env python3
"""
Простой тест TTS на русском языке
"""

import os
import sys
from pathlib import Path

def test_tts_import():
    """Тестирует импорт TTS"""
    try:
        from TTS.api import TTS
        print("✅ TTS импортирован успешно")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта TTS: {e}")
        return False

def test_tts_synthesis():
    """Тестирует синтез речи на русском языке"""
    try:
        from TTS.api import TTS
        
        # Используем другую русскоязычную модель
        model_name = "tts_models/ru/ru_v3"
        print(f"🔄 Загружаем модель: {model_name}")
        tts = TTS(model_name)
        
        # Получаем список спикеров (если есть)
        speakers = getattr(tts, 'speakers', None)
        if speakers:
            print(f"✅ Доступные спикеры: {speakers}")
            speaker = speakers[0]
        else:
            speaker = None
        
        # Тестовый текст
        text = "Привет, это тест синтеза речи на русском языке."
        print(f"🔄 Синтезируем текст: '{text}'")
        output_path = "test_output_ru.wav"
        
        # Синтез речи
        if speaker:
            tts.tts_to_file(text=text, speaker=speaker, file_path=output_path)
        else:
            tts.tts_to_file(text=text, file_path=output_path)
        
        if os.path.exists(output_path):
            print(f"✅ Аудиофайл создан: {output_path}")
            print(f"📊 Размер файла: {os.path.getsize(output_path)} байт")
            return True
        else:
            print("❌ Аудиофайл не создан")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка синтеза речи: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование TTS (русский язык)...")
    print("=" * 50)
    
    # Тест 1: Импорт
    if not test_tts_import():
        return False
    print()
    # Тест 2: Синтез
    if not test_tts_synthesis():
        return False
    print()
    print("🎉 Все тесты TTS пройдены успешно!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 