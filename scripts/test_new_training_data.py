#!/usr/bin/env python3
"""
Тестирование с новыми данными обучения
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_new_training_data():
    """Тестирование с новыми данными обучения"""
    
    print("🎤 ТЕСТИРОВАНИЕ С НОВЫМИ ДАННЫМИ ОБУЧЕНИЯ")
    print("=" * 60)
    
    # URL для HierSpeech_TTS API
    hier_url = "http://127.0.0.1:8001"
    
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
    
    # Тестовые тексты на русском языке
    test_texts = [
        "Привет! Как дела?",
        "Сегодня прекрасная погода.",
        "Я очень рада вас видеть.",
        "Спасибо за внимание.",
        "До свидания!"
    ]
    
    # Тестируем синтез речи с разными голосами
    print("\n🎵 Тестирование синтеза речи с новыми данными:")
    print("-" * 50)
    
    results = []
    
    # Тестируем первые 5 голосов из новых данных
    test_voices = voices_data['voices'][:5]
    
    for voice_idx, voice in enumerate(test_voices, 1):
        print(f"\n🎤 Тест голоса {voice_idx}: {voice['name']}")
        print(f"   📊 Размер: {voice['size']} байт")
        
        voice_results = []
        
        for text_idx, text in enumerate(test_texts, 1):
            print(f"   {text_idx}. Текст: '{text}'")
            
            try:
                # Запрос на синтез с конкретным голосом
                payload = {
                    "text": text,
                    "language": "ru",
                    "reference_audio_path": voice['path'].replace('../', '')
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
                    
                    # Проверяем существование файла
                    actual_path = audio_path
                    if not os.path.exists(actual_path) and not actual_path.startswith('HierSpeech_TTS/'):
                        actual_path = f"HierSpeech_TTS/{audio_path}"
                    
                    if os.path.exists(actual_path):
                        file_size = os.path.getsize(actual_path)
                        print(f"      ✅ Синтез успешен")
                        print(f"      📁 Файл: {os.path.basename(audio_path)}")
                        print(f"      ⏱️  Длительность: {duration:.2f} сек")
                        print(f"      📊 Размер: {file_size} байт")
                        
                        voice_results.append({
                            "text": text,
                            "success": True,
                            "audio_path": actual_path,
                            "duration": duration,
                            "file_size": file_size
                        })
                    else:
                        print(f"      ❌ Файл не найден: {audio_path}")
                        voice_results.append({
                            "text": text,
                            "success": False,
                            "error": "Файл не найден"
                        })
                else:
                    print(f"      ❌ Ошибка синтеза: {response.status_code}")
                    voice_results.append({
                        "text": text,
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except requests.exceptions.RequestException as e:
                print(f"      ❌ Ошибка запроса: {e}")
                voice_results.append({
                    "text": text,
                    "success": False,
                    "error": str(e)
                })
            
            time.sleep(1)  # Пауза между запросами
        
        # Статистика для этого голоса
        successful = sum(1 for r in voice_results if r['success'])
        total = len(voice_results)
        
        print(f"   📊 Результаты голоса {voice_idx}: {successful}/{total} успешных")
        
        results.append({
            "voice": voice['name'],
            "voice_size": voice['size'],
            "results": voice_results,
            "successful": successful,
            "total": total
        })
    
    # Общая статистика
    print("\n📊 ОБЩАЯ СТАТИСТИКА:")
    print("-" * 50)
    
    total_tests = sum(r['total'] for r in results)
    total_successful = sum(r['successful'] for r in results)
    
    print(f"🎤 Протестировано голосов: {len(results)}")
    print(f"📝 Всего тестов: {total_tests}")
    print(f"✅ Успешных: {total_successful}")
    print(f"❌ Ошибок: {total_tests - total_successful}")
    print(f"📈 Общая успешность: {total_successful/total_tests*100:.1f}%")
    
    # Детальная статистика по голосам
    print("\n🎤 ДЕТАЛЬНАЯ СТАТИСТИКА ПО ГОЛОСАМ:")
    print("-" * 50)
    
    for i, result in enumerate(results, 1):
        success_rate = result['successful'] / result['total'] * 100
        print(f"{i}. {result['voice']}: {result['successful']}/{result['total']} ({success_rate:.1f}%)")
    
    # Сохраняем результаты
    output_file = "test_results_new_training_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_type": "new_training_data",
            "total_voices_tested": len(results),
            "total_tests": total_tests,
            "total_successful": total_successful,
            "overall_success_rate": total_successful/total_tests*100 if total_tests > 0 else 0,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: {output_file}")
    
    # Итоговый результат
    print("\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("-" * 50)
    
    if total_successful == total_tests:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Новые данные обучения работают отлично!")
    elif total_successful > total_tests * 0.8:
        print("✅ БОЛЬШИНСТВО ТЕСТОВ ПРОЙДЕНО УСПЕШНО!")
        print("Новые данные обучения работают хорошо!")
    elif total_successful > total_tests * 0.5:
        print("⚠️  ЧАСТИЧНО УСПЕШНО!")
        print("Есть проблемы с некоторыми голосами.")
    else:
        print("❌ МНОГО ПРОБЛЕМ!")
        print("Требуется доработка системы.")
    
    return total_successful > total_tests * 0.5

def main():
    """Основная функция"""
    
    success = test_new_training_data()
    
    if success:
        print("\n✅ Тестирование завершено успешно!")
        return True
    else:
        print("\n❌ Тестирование выявило проблемы!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 