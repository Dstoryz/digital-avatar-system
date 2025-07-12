#!/usr/bin/env python3
"""
Скрипт для проверки размещенных фото и аудио файлов.

Использование:
    python3 scripts/check_data.py
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple

TEST_DATA_DIR = Path("test_data")

def check_directory_structure() -> bool:
    """Проверка структуры папок."""
    print("📁 Проверка структуры папок...")
    
    required_dirs = [
        "test_data",
        "test_data/photos",
        "test_data/audio", 
        "test_data/processed",
        "test_data/processed/avatars",
        "test_data/processed/voice_clips",
        "test_data/processed/animations"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Отсутствуют папки: {', '.join(missing_dirs)}")
        return False
    else:
        print("✅ Все папки созданы")
        return True

def check_photos() -> Tuple[bool, List[str]]:
    """Проверка фотографий."""
    print("\n📸 Проверка фотографий...")
    
    photos_dir = TEST_DATA_DIR / "photos"
    photo_files = list(photos_dir.glob("*"))
    
    if not photo_files:
        print("⚠️  Папка test_data/photos/ пуста")
        print("   Добавьте 3-5 качественных фото девочки")
        return False, []
    
    print(f"📊 Найдено файлов: {len(photo_files)}")
    
    valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    valid_photos = []
    issues = []
    
    for photo_file in photo_files:
        if photo_file.suffix.lower() in valid_extensions:
            file_size = photo_file.stat().st_size
            size_mb = file_size / (1024 * 1024)
            
            if size_mb > 10:
                issues.append(f"Файл {photo_file.name} слишком большой: {size_mb:.1f}MB")
            else:
                valid_photos.append(photo_file.name)
                print(f"   ✅ {photo_file.name} ({size_mb:.1f}MB)")
        else:
            issues.append(f"Неподдерживаемый формат: {photo_file.name}")
    
    if issues:
        print("⚠️  Проблемы:")
        for issue in issues:
            print(f"   - {issue}")
    
    if len(valid_photos) >= 3:
        print(f"✅ Достаточно фото: {len(valid_photos)} файлов")
        return True, valid_photos
    else:
        print(f"⚠️  Недостаточно фото: {len(valid_photos)} из 3-5")
        return False, valid_photos

def check_audio() -> Tuple[bool, List[str]]:
    """Проверка аудиофайлов."""
    print("\n🎤 Проверка аудиофайлов...")
    
    audio_dir = TEST_DATA_DIR / "audio"
    audio_files = list(audio_dir.glob("*"))
    
    if not audio_files:
        print("⚠️  Папка test_data/audio/ пуста")
        print("   Добавьте 5-10 минут аудиозаписей девочки")
        return False, []
    
    print(f"📊 Найдено файлов: {len(audio_files)}")
    
    valid_extensions = {'.wav', '.mp3', '.m4a', '.flac'}
    valid_audio = []
    issues = []
    
    for audio_file in audio_files:
        if audio_file.suffix.lower() in valid_extensions:
            file_size = audio_file.stat().st_size
            size_mb = file_size / (1024 * 1024)
            
            # Примерная оценка длительности (1MB ≈ 1 минута для WAV)
            estimated_duration = size_mb
            
            valid_audio.append(audio_file.name)
            print(f"   ✅ {audio_file.name} ({size_mb:.1f}MB, ~{estimated_duration:.0f}мин)")
        else:
            issues.append(f"Неподдерживаемый формат: {audio_file.name}")
    
    if issues:
        print("⚠️  Проблемы:")
        for issue in issues:
            print(f"   - {issue}")
    
    total_size_mb = sum((TEST_DATA_DIR / "audio" / f).stat().st_size / (1024 * 1024) for f in valid_audio)
    
    if total_size_mb >= 5:  # Примерно 5 минут аудио
        print(f"✅ Достаточно аудио: {len(valid_audio)} файлов (~{total_size_mb:.0f} минут)")
        return True, valid_audio
    else:
        print(f"⚠️  Недостаточно аудио: ~{total_size_mb:.0f} минут из 5-10")
        return False, valid_audio

def check_processed_files() -> bool:
    """Проверка обработанных файлов."""
    print("\n🔄 Проверка обработанных файлов...")
    
    processed_dirs = [
        "test_data/processed/avatars",
        "test_data/processed/voice_clips", 
        "test_data/processed/animations"
    ]
    
    all_empty = True
    for dir_path in processed_dirs:
        files = list(Path(dir_path).glob("*"))
        if files:
            print(f"   📁 {dir_path}: {len(files)} файлов")
            all_empty = False
        else:
            print(f"   📁 {dir_path}: пусто (нормально)")
    
    if all_empty:
        print("✅ Обработанные файлы будут созданы автоматически")
    else:
        print("⚠️  Обнаружены обработанные файлы")
    
    return True

def generate_summary(photos_ok: bool, audio_ok: bool, photos: List[str], audio: List[str]) -> None:
    """Генерация итогового отчета."""
    print("\n" + "="*50)
    print("📋 ИТОГОВЫЙ ОТЧЕТ")
    print("="*50)
    
    if photos_ok and audio_ok:
        print("🎉 ДАННЫЕ ГОТОВЫ К ИСПОЛЬЗОВАНИЮ!")
        print("\n📸 Фотографии:")
        for photo in photos:
            print(f"   - {photo}")
        
        print("\n🎤 Аудиофайлы:")
        for audio_file in audio:
            print(f"   - {audio_file}")
        
        print("\n🚀 Следующие шаги:")
        print("   1. Запустить систему загрузки")
        print("   2. Загрузить данные через веб-интерфейс")
        print("   3. Начать интеграцию AI моделей")
        
    else:
        print("⚠️  ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ ПОДГОТОВКА")
        
        if not photos_ok:
            print("\n📸 Для фотографий нужно:")
            print("   - Добавить 3-5 качественных фото в test_data/photos/")
            print("   - Разрешение: минимум 512x512")
            print("   - Форматы: JPG, PNG, WEBP")
            print("   - Размер: максимум 10MB каждое")
        
        if not audio_ok:
            print("\n🎤 Для аудио нужно:")
            print("   - Добавить 5-10 минут аудиозаписей в test_data/audio/")
            print("   - Форматы: WAV, MP3, M4A")
            print("   - Частота: 16kHz или выше")
            print("   - Разные эмоции и интонации")
    
    print("\n📁 Структура папок:")
    print("   test_data/photos/     - исходные фото")
    print("   test_data/audio/      - исходные аудио")
    print("   test_data/processed/  - обработанные файлы")

def main():
    """Основная функция."""
    print("🔍 Проверка размещенных данных для цифрового аватара")
    print("="*60)
    
    # Проверка структуры
    if not check_directory_structure():
        print("\n❌ Создайте недостающие папки:")
        print("   mkdir -p test_data/{photos,audio,processed/{avatars,voice_clips,animations}}")
        return
    
    # Проверка фото
    photos_ok, photos = check_photos()
    
    # Проверка аудио
    audio_ok, audio = check_audio()
    
    # Проверка обработанных файлов
    check_processed_files()
    
    # Итоговый отчет
    generate_summary(photos_ok, audio_ok, photos, audio)

if __name__ == "__main__":
    main() 