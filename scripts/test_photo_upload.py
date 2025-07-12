#!/usr/bin/env python3
"""
Скрипт для тестирования API загрузки фотографий.

Использование:
    python scripts/test_photo_upload.py [путь_к_фото]

Пример:
    python scripts/test_photo_upload.py test_photos/avatar.jpg
"""

import sys
import os
import requests
import json
from pathlib import Path
from typing import List, Optional

# Настройки API
API_BASE_URL = "http://localhost:8000/api/v1"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload/photos"
STATUS_ENDPOINT = f"{API_BASE_URL}/upload/status"

def check_server_status() -> bool:
    """Проверка доступности сервера."""
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Сервер доступен")
            return True
        else:
            print(f"❌ Сервер недоступен: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к серверу: {e}")
        return False

def get_upload_status() -> Optional[dict]:
    """Получение статуса системы загрузки."""
    try:
        response = requests.get(STATUS_ENDPOINT, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Ошибка получения статуса: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса статуса: {e}")
        return None

def validate_image_file(file_path: Path) -> bool:
    """Валидация файла изображения."""
    if not file_path.exists():
        print(f"❌ Файл не найден: {file_path}")
        return False
    
    if not file_path.is_file():
        print(f"❌ Не является файлом: {file_path}")
        return False
    
    # Проверка размера (максимум 10MB)
    file_size = file_path.stat().st_size
    max_size = 10 * 1024 * 1024  # 10MB
    
    if file_size > max_size:
        print(f"❌ Файл слишком большой: {file_size / 1024 / 1024:.1f}MB (максимум 10MB)")
        return False
    
    # Проверка расширения
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    if file_path.suffix.lower() not in allowed_extensions:
        print(f"❌ Неподдерживаемый формат: {file_path.suffix}")
        print(f"   Поддерживаются: {', '.join(allowed_extensions)}")
        return False
    
    print(f"✅ Файл валиден: {file_path.name} ({file_size / 1024:.1f}KB)")
    return True

def upload_photos(file_paths: List[Path]) -> Optional[dict]:
    """Загрузка фотографий через API."""
    if not file_paths:
        print("❌ Нет файлов для загрузки")
        return None
    
    # Подготовка файлов для загрузки
    files = []
    for file_path in file_paths:
        if validate_image_file(file_path):
            files.append(('files', (file_path.name, open(file_path, 'rb'), 'image/jpeg')))
        else:
            return None
    
    try:
        print(f"📤 Загрузка {len(files)} файлов...")
        response = requests.post(
            UPLOAD_ENDPOINT,
            files=files,
            data={'description': 'Тестовая загрузка фото'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Загрузка успешна!")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Загружено файлов: {result.get('total_files')}")
            return result
        else:
            print(f"❌ Ошибка загрузки: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return None
    finally:
        # Закрываем файлы
        for _, file_tuple in files:
            file_tuple[1].close()

def get_uploaded_photos(session_id: str) -> Optional[dict]:
    """Получение информации о загруженных фотографиях."""
    try:
        response = requests.get(f"{UPLOAD_ENDPOINT}/{session_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Ошибка получения информации: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return None

def main():
    """Основная функция."""
    print("🧪 Тестирование API загрузки фотографий")
    print("=" * 50)
    
    # Проверка сервера
    if not check_server_status():
        print("\n💡 Убедитесь, что сервер запущен:")
        print("   cd backend && uvicorn app.main:app --reload")
        return
    
    # Получение статуса
    status = get_upload_status()
    if status:
        print(f"📊 Статус системы:")
        print(f"   Фотографий: {status.get('photos_count', 0)}")
        print(f"   Аватаров: {status.get('avatars_count', 0)}")
        print(f"   Свободное место: {status.get('disk_space', {}).get('free_gb', 0)}GB")
    
    # Обработка аргументов командной строки
    if len(sys.argv) < 2:
        print("\n📝 Использование:")
        print(f"   {sys.argv[0]} [путь_к_фото1] [путь_к_фото2] ...")
        print("\n💡 Примеры:")
        print(f"   {sys.argv[0]} test_photos/avatar.jpg")
        print(f"   {sys.argv[0]} photo1.jpg photo2.png photo3.webp")
        return
    
    # Получение путей к файлам
    file_paths = []
    for arg in sys.argv[1:]:
        file_path = Path(arg)
        if file_path.exists():
            file_paths.append(file_path)
        else:
            print(f"⚠️  Файл не найден: {arg}")
    
    if not file_paths:
        print("❌ Нет валидных файлов для загрузки")
        return
    
    print(f"\n📁 Найдено файлов: {len(file_paths)}")
    
    # Загрузка файлов
    result = upload_photos(file_paths)
    if result:
        session_id = result.get('session_id')
        
        # Получение информации о загруженных файлах
        print(f"\n📋 Информация о загруженных файлах:")
        files_info = get_uploaded_photos(session_id)
        if files_info:
            for i, file_info in enumerate(files_info.get('files', []), 1):
                print(f"   {i}. {file_info.get('original_name', 'Unknown')}")
                print(f"      Размер: {file_info.get('size', 0) / 1024:.1f}KB")
                print(f"      Размеры: {file_info.get('dimensions', 'Unknown')}")
        
        print(f"\n🎉 Тест завершен успешно!")
        print(f"   Session ID: {session_id}")
        print(f"   API endpoint: {UPLOAD_ENDPOINT}")
    else:
        print("\n❌ Тест завершен с ошибками")

if __name__ == "__main__":
    main() 