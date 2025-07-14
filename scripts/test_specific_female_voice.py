#!/usr/bin/env python3
"""
Тестирование конкретного женского голоса
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_specific_female_voice(voice_path: str, test_text: str = "Привет! Это тест женского голоса."):
    """Тестирование конкретного женского голоса"""
    
    print(f"🎤 Тестирование женского голоса: {os.path.basename(voice_path)}")
    print("=" * 60)
    
    # URL для HierSpeech_TTS API
    hier_url = "http://127.0.0.1:8001"
    
    # Исправляем путь к файлу голоса
    actual_voice_path = voice_path
    if voice_path.startswith('../'):
        actual_voice_path = voice_path[3:]  # Убираем ../
    
    # Проверяем существование файла голоса
    if not os.path.exists(actual_voice_path):
        print(f"❌ Файл голоса не найден: {actual_voice_path}")
        return False
    
    print(f"✅ Файл голоса найден: {actual_voice_path}")
    print(f"📊 Размер: {os.path.getsize(actual_voice_path)} байт")
    
    try:
        # Запрос на синтез с конкретным голосом
        payload = {
            "text": test_text,
            "language": "ru",
            "reference_audio_path": actual_voice_path
        }
        
        print(f"📝 Текст: '{test_text}'")
        print("🔄 Отправка запроса...")
        
        response = requests.post(
            f"{hier_url}/synthesize",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            audio_path = result['audio_path']
            duration = result['duration']
            sample_rate = result['sample_rate']
            
            print(f"✅ Синтез успешен")
            print(f"📁 Файл: {audio_path}")
            print(f"⏱️  Длительность: {duration:.2f} сек")
            print(f"🔊 Частота: {sample_rate} Hz")
            
            # Проверяем существование файла
            actual_path = audio_path
            if not os.path.exists(actual_path) and not actual_path.startswith('HierSpeech_TTS/'):
                actual_path = f"HierSpeech_TTS/{audio_path}"
            
            if os.path.exists(actual_path):
                file_size = os.path.getsize(actual_path)
                print(f"📊 Размер: {file_size} байт")
                
                # Воспроизводим звук
                print("🔊 Воспроизведение звука...")
                os.system(f"aplay {actual_path}")
                
                return True
            else:
                print(f"❌ Файл не найден: {audio_path}")
                return False
        else:
            print(f"❌ Ошибка синтеза: {response.status_code}")
            print(f"📝 Ответ: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def list_available_voices():
    """Список доступных женских голосов"""
    
    print("📋 Доступные женские голоса:")
    print("-" * 40)
    
    hier_url = "http://127.0.0.1:8001"
    
    try:
        response = requests.get(f"{hier_url}/voices", timeout=5)
        if response.status_code == 200:
            voices_data = response.json()
            
            for i, voice in enumerate(voices_data['voices'][:10], 1):  # Показываем первые 10
                print(f"{i:2d}. {voice['name']} ({voice['size']} байт)")
            
            if len(voices_data['voices']) > 10:
                print(f"... и ещё {len(voices_data['voices']) - 10} голосов")
            
            return voices_data['voices']
        else:
            print(f"❌ Ошибка получения голосов: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return []

def main():
    """Основная функция"""
    
    print("🎤 ТЕСТИРОВАНИЕ КОНКРЕТНОГО ЖЕНСКОГО ГОЛОСА")
    print("=" * 60)
    
    # Показываем доступные голоса
    voices = list_available_voices()
    
    if not voices:
        print("❌ Нет доступных голосов")
        return False
    
    # Выбираем первый голос для тестирования
    test_voice = voices[0]['path']
    
    # Тестируем разные тексты
    test_texts = [
        "Привет! Как дела?",
        "Сегодня прекрасная погода.",
        "Я очень рада вас видеть.",
        "Спасибо за внимание.",
        "До свидания!"
    ]
    
    print(f"\n🎵 Тестирование голоса: {os.path.basename(test_voice)}")
    print("-" * 40)
    
    success_count = 0
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Тестирование текста: '{text}'")
        if test_specific_female_voice(test_voice, text):
            success_count += 1
        else:
            print("❌ Тест не прошёл")
        
        time.sleep(2)  # Пауза между тестами
    
    print(f"\n📊 Результаты: {success_count}/{len(test_texts)} успешных тестов")
    
    if success_count == len(test_texts):
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Женский голос работает корректно")
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ С ГОЛОСОМ")
    
    return success_count == len(test_texts)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 