#!/usr/bin/env python3
"""
Тестовый скрипт для проверки реального синтеза речи
"""

import requests
import json
import time
import os

def test_tts_synthesis():
    """Тестирует синтез речи через API"""
    
    base_url = "http://127.0.0.1:8001"
    
    # Тестовые фразы
    test_phrases = [
        "Привет!",
        "Как дела?",
        "Сегодня прекрасная погода.",
        "Я очень рада вас видеть.",
        "Спасибо за внимание.",
        "До свидания!"
    ]
    
    print("🎤 Тестирование реального синтеза речи")
    print("=" * 50)
    
    results = []
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n{i}. Синтезируем: '{phrase}'")
        
        try:
            # Отправляем запрос на синтез
            response = requests.post(
                f"{base_url}/synthesize",
                json={
                    "text": phrase,
                    "language": "ru"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Успешно!")
                print(f"   📁 Файл: {result['audio_path']}")
                print(f"   ⏱️  Длительность: {result['duration']:.2f} сек")
                print(f"   🔊 Частота: {result['sample_rate']} Hz")
                
                # Проверяем существование файла (исправляем путь)
                file_path = f"HierSpeech_TTS/{result['audio_path']}"
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"   📊 Размер: {file_size} байт")
                    
                    # Воспроизводим аудио
                    print(f"   🎵 Воспроизводим...")
                    os.system(f"aplay {file_path}")
                    
                    results.append({
                        "phrase": phrase,
                        "success": True,
                        "file": file_path,
                        "duration": result['duration'],
                        "size": file_size
                    })
                else:
                    print(f"   ❌ Файл не найден: {file_path}")
                    results.append({
                        "phrase": phrase,
                        "success": False,
                        "error": "Файл не создан"
                    })
            else:
                print(f"   ❌ Ошибка HTTP: {response.status_code}")
                print(f"   📄 Ответ: {response.text}")
                results.append({
                    "phrase": phrase,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            results.append({
                "phrase": phrase,
                "success": False,
                "error": str(e)
            })
        
        time.sleep(1)  # Пауза между запросами
    
    # Итоговая статистика
    print("\n" + "=" * 50)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 50)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"✅ Успешно: {successful}/{total}")
    print(f"❌ Ошибок: {total - successful}/{total}")
    print(f"📈 Успешность: {successful/total*100:.1f}%")
    
    if successful > 0:
        avg_duration = sum(r['duration'] for r in results if r['success']) / successful
        avg_size = sum(r['size'] for r in results if r['success']) / successful
        print(f"⏱️  Средняя длительность: {avg_duration:.2f} сек")
        print(f"📊 Средний размер: {avg_size:.0f} байт")
    
    # Список ошибок
    errors = [r for r in results if not r['success']]
    if errors:
        print(f"\n❌ ОШИБКИ:")
        for error in errors:
            print(f"   - '{error['phrase']}': {error['error']}")
    
    return results

def test_health_check():
    """Проверяет состояние сервера"""
    
    print("\n🏥 Проверка состояния сервера")
    print("-" * 30)
    
    try:
        response = requests.get("http://127.0.0.1:8001/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Статус: {health['status']}")
            print(f"🤖 Модели загружены: {health['models_loaded']}")
            print(f"🔊 Доступно голосов: {health['available_female_voices']}")
            print(f"🎯 Всего голосов: {health['total_female_voices']}")
            print(f"🚀 CUDA доступен: {health['cuda_available']}")
        else:
            print(f"❌ Ошибка проверки состояния: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестирования синтеза речи")
    print("=" * 50)
    
    # Проверяем состояние сервера
    test_health_check()
    
    # Тестируем синтез речи
    results = test_tts_synthesis()
    
    print("\n🎉 Тестирование завершено!") 