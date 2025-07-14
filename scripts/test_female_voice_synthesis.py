#!/usr/bin/env python3
"""
Тестирование синтеза речи с женскими голосами на русском языке
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_hier_speech_female_voices():
    """Тестирование HierSpeech_TTS с женскими голосами"""
    
    print("🎤 Тестирование синтеза речи с женскими голосами")
    print("=" * 60)
    
    # URL для HierSpeech_TTS API
    hier_url = "http://127.0.0.1:8001"
    
    # Тестовые тексты на русском языке
    test_texts = [
        "Привет! Как дела?",
        "Сегодня прекрасная погода.",
        "Я очень рада вас видеть.",
        "Спасибо за внимание.",
        "До свидания!"
    ]
    
    # Проверяем доступность сервера
    try:
        response = requests.get(f"{hier_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ HierSpeech_TTS сервер доступен")
            print(f"   Доступно женских голосов: {health_data.get('available_female_voices', 0)}")
            print(f"   Всего голосов: {health_data.get('total_female_voices', 0)}")
        else:
            print(f"❌ Ошибка подключения к серверу: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Не удалось подключиться к серверу: {e}")
        return False
    
    # Получаем список доступных голосов
    try:
        response = requests.get(f"{hier_url}/voices", timeout=5)
        if response.status_code == 200:
            voices_data = response.json()
            print(f"📋 Найдено голосов: {voices_data['available_voices']}")
            
            if voices_data['available_voices'] == 0:
                print("❌ Нет доступных женских голосов!")
                return False
        else:
            print(f"❌ Ошибка получения списка голосов: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка получения голосов: {e}")
        return False
    
    # Тестируем синтез речи
    print("\n🎵 Тестирование синтеза речи:")
    print("-" * 40)
    
    results = []
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Текст: '{text}'")
        
        try:
            # Запрос на синтез
            payload = {
                "text": text,
                "language": "ru"
            }
            
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
                
                print(f"   ✅ Синтез успешен")
                print(f"   📁 Файл: {audio_path}")
                print(f"   ⏱️  Длительность: {duration:.2f} сек")
                print(f"   🔊 Частота: {sample_rate} Hz")
                
                # Проверяем существование файла
                # Исправляем путь к файлу (добавляем HierSpeech_TTS/ если нужно)
                actual_path = audio_path
                if not os.path.exists(actual_path) and not actual_path.startswith('HierSpeech_TTS/'):
                    actual_path = f"HierSpeech_TTS/{audio_path}"
                
                if os.path.exists(actual_path):
                    file_size = os.path.getsize(actual_path)
                    print(f"   📊 Размер: {file_size} байт")
                    
                    results.append({
                        "text": text,
                        "success": True,
                        "audio_path": actual_path,
                        "duration": duration,
                        "file_size": file_size
                    })
                else:
                    print(f"   ❌ Файл не найден: {audio_path}")
                    print(f"   🔍 Проверял пути: {audio_path}, {actual_path}")
                    results.append({
                        "text": text,
                        "success": False,
                        "error": "Файл не найден"
                    })
            else:
                print(f"   ❌ Ошибка синтеза: {response.status_code}")
                print(f"   📝 Ответ: {response.text}")
                results.append({
                    "text": text,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Ошибка запроса: {e}")
            results.append({
                "text": text,
                "success": False,
                "error": str(e)
            })
        
        # Небольшая пауза между запросами
        time.sleep(1)
    
    # Статистика
    print("\n📊 Статистика тестирования:")
    print("-" * 40)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"✅ Успешных: {successful}/{total}")
    print(f"❌ Ошибок: {total - successful}/{total}")
    print(f"📈 Успешность: {successful/total*100:.1f}%")
    
    if successful > 0:
        avg_duration = sum(r['duration'] for r in results if r['success']) / successful
        avg_size = sum(r['file_size'] for r in results if r['success']) / successful
        print(f"⏱️  Средняя длительность: {avg_duration:.2f} сек")
        print(f"📊 Средний размер: {avg_size:.0f} байт")
    
    # Сохраняем результаты
    output_file = "test_results_female_voices.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_type": "female_voice_synthesis",
            "results": results,
            "statistics": {
                "successful": successful,
                "total": total,
                "success_rate": successful/total*100 if total > 0 else 0
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: {output_file}")
    
    return successful > 0

def test_backend_integration():
    """Тестирование интеграции с основным backend"""
    
    print("\n🔗 Тестирование интеграции с backend:")
    print("-" * 40)
    
    backend_url = "http://127.0.0.1:8000"
    
    # Проверяем доступность backend
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend доступен")
        else:
            print(f"❌ Backend недоступен: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к backend: {e}")
        return False
    
    # Тестируем русский TTS через backend
    test_text = "Привет! Это тест женского голоса на русском языке."
    
    try:
        payload = {
            "text": test_text,
            "language": "ru",
            "voice_type": "female"
        }
        
        response = requests.post(
            f"{backend_url}/api/tts/synthesize",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Синтез через backend успешен")
            print(f"   📁 Файл: {result.get('audio_path', 'N/A')}")
            print(f"   ⏱️  Длительность: {result.get('duration', 'N/A')}")
        else:
            print(f"❌ Ошибка синтеза через backend: {response.status_code}")
            print(f"   📝 Ответ: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса к backend: {e}")
        return False
    
    return True

def main():
    """Основная функция"""
    
    print("🎤 ТЕСТИРОВАНИЕ ЖЕНСКИХ ГОЛОСОВ НА РУССКОМ ЯЗЫКЕ")
    print("=" * 60)
    
    # Тестируем HierSpeech_TTS
    hier_success = test_hier_speech_female_voices()
    
    # Тестируем интеграцию с backend
    backend_success = test_backend_integration()
    
    # Итоговый результат
    print("\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("-" * 40)
    
    if hier_success:
        print("✅ HierSpeech_TTS с женскими голосами работает")
    else:
        print("❌ HierSpeech_TTS с женскими голосами не работает")
    
    if backend_success:
        print("✅ Интеграция с backend работает")
    else:
        print("❌ Интеграция с backend не работает")
    
    if hier_success and backend_success:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Система готова к использованию с женскими голосами на русском языке")
    else:
        print("\n⚠️  ЕСТЬ ПРОБЛЕМЫ, ТРЕБУЕТСЯ ДОРАБОТКА")
    
    return hier_success and backend_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 