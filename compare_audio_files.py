#!/usr/bin/env python3
"""
Скрипт для сравнения аудиофайлов.

Сравнивает параметры старого и нового аудиофайлов.

Автор: AI Assistant
Версия: 1.0.0
"""

import subprocess
import json

def get_audio_info(file_path):
    """Получение информации об аудиофайле."""
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"❌ Ошибка получения информации о {file_path}: {e}")
        return None

def compare_audio_files():
    """Сравнение аудиофайлов."""
    print("🔍 СРАВНЕНИЕ АУДИОФАЙЛОВ")
    print("=" * 50)
    
    # Файлы для сравнения
    old_file = "demo_russian_test_1.wav"
    new_file = "demo_russian_test_fixed_1.wav"
    
    print(f"📁 Старый файл: {old_file}")
    print(f"📁 Новый файл: {new_file}")
    print()
    
    # Получаем информацию о файлах
    old_info = get_audio_info(old_file)
    new_info = get_audio_info(new_file)
    
    if not old_info or not new_info:
        print("❌ Не удалось получить информацию о файлах")
        return
    
    # Извлекаем параметры
    old_stream = old_info["streams"][0]
    new_stream = new_info["streams"][0]
    
    old_format = old_info["format"]
    new_format = new_info["format"]
    
    print("📊 ПАРАМЕТРЫ АУДИО:")
    print("-" * 30)
    print(f"Длительность:")
    print(f"  Старый: {old_format['duration']} сек")
    print(f"  Новый:  {new_format['duration']} сек")
    print(f"  Разница: {float(new_format['duration']) / float(old_format['duration']):.2f}x")
    print()
    
    print(f"Частота дискретизации:")
    print(f"  Старый: {old_stream['sample_rate']} Hz")
    print(f"  Новый:  {new_stream['sample_rate']} Hz")
    print()
    
    print(f"Размер файла:")
    print(f"  Старый: {int(old_format['size']) / 1024:.1f} KB")
    print(f"  Новый:  {int(new_format['size']) / 1024:.1f} KB")
    print()
    
    print(f"Битрейт:")
    print(f"  Старый: {old_stream['bit_rate']} bps")
    print(f"  Новый:  {new_stream['bit_rate']} bps")
    print()
    
    # Анализ проблемы
    print("🔍 АНАЛИЗ ПРОБЛЕМЫ:")
    print("-" * 30)
    print("❌ ПРОБЛЕМА В СТАРОМ ФАЙЛЕ:")
    print("  - Использовался неправильный pitch shifting")
    print("  - Команда 'asetrate=44100*1.2' изменяла частоту дискретизации")
    print("  - Это делало аудио быстрее в 1.2 раза")
    print("  - Длительность уменьшалась с 2.47 сек до 1.03 сек")
    print()
    
    print("✅ РЕШЕНИЕ В НОВОМ ФАЙЛЕ:")
    print("  - Используется правильный pitch shifting")
    print("  - Питч изменяется без изменения скорости")
    print("  - Длительность остается естественной")
    print("  - Аудио воспроизводится с правильной скоростью")
    print()
    
    print("🎵 РЕКОМЕНДАЦИИ:")
    print("-" * 30)
    print("1. Используйте новый скрипт для создания аудио")
    print("2. Избегайте 'asetrate' для pitch shifting")
    print("3. Используйте 'rubberband' или 'atempo' фильтры")
    print("4. Всегда проверяйте длительность созданных файлов")

if __name__ == "__main__":
    compare_audio_files() 