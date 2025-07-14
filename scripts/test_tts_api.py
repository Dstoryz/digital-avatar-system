#!/usr/bin/env python3
"""
Тестовый скрипт для проверки TTS API endpoints.

Проверяет работу ElevenLabs TTS интеграции в backend.

Автор: AI Assistant
Версия: 1.0.0
"""

import requests
import json
import os
from typing import Dict, Any

class TTSAPITester:
    """Тестер для TTS API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """
        Инициализация тестера.
        
        Args:
            base_url: Базовый URL API
        """
        self.base_url = base_url
        self.api_prefix = "/api/v1/tts"
        print(f"🎤 TTS API Тестер инициализирован")
        print(f"🌐 Базовый URL: {base_url}")
    
    def test_health(self) -> bool:
        """Тест health check."""
        print("\n🏥 Тест health check...")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check успешен: {data}")
                return True
            else:
                print(f"❌ Health check провален: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка health check: {e}")
            return False
    
    def test_tts_status(self) -> bool:
        """Тест статуса TTS сервиса."""
        print("\n📊 Тест статуса TTS...")
        
        try:
            response = requests.get(f"{self.base_url}{self.api_prefix}/status")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ TTS статус: {data}")
                return data.get("available", False)
            else:
                print(f"❌ TTS статус провален: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка TTS статуса: {e}")
            return False
    
    def test_voices_endpoint(self) -> bool:
        """Тест endpoint для получения голосов."""
        print("\n🎭 Тест получения голосов...")
        
        try:
            response = requests.get(f"{self.base_url}{self.api_prefix}/voices")
            
            if response.status_code == 200:
                data = response.json()
                voices_count = len(data.get("voices", []))
                print(f"✅ Найдено голосов: {voices_count}")
                return True
            elif response.status_code == 503:
                print("⚠️  ElevenLabs API ключ не установлен")
                print("💡 Установите: export ELEVENLABS_API_KEY='ваш_ключ'")
                return False
            else:
                print(f"❌ Ошибка получения голосов: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка получения голосов: {e}")
            return False
    
    def test_russian_synthesis(self) -> bool:
        """Тест синтеза русской речи."""
        print("\n🇷🇺 Тест синтеза русской речи...")
        
        try:
            response = requests.post(f"{self.base_url}{self.api_prefix}/test-russian")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Тест русской речи успешен: {data}")
                return True
            elif response.status_code == 503:
                print("⚠️  ElevenLabs API ключ не установлен")
                return False
            else:
                print(f"❌ Ошибка теста русской речи: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка теста русской речи: {e}")
            return False
    
    def test_synthesis_with_params(self, text: str, voice_id: str) -> bool:
        """Тест синтеза с параметрами."""
        print(f"\n🎤 Тест синтеза: '{text[:30]}...'")
        
        try:
            data = {
                "text": text,
                "voice_id": voice_id,
                "output_filename": "test_synthesis.wav"
            }
            
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/synthesize",
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Синтез успешен: {result}")
                return True
            else:
                print(f"❌ Ошибка синтеза: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка синтеза: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Запуск всех тестов."""
        print("🧪 ЗАПУСК ВСЕХ ТЕСТОВ TTS API")
        print("=" * 50)
        
        results = {}
        
        # Тест 1: Health check
        results["health"] = self.test_health()
        
        # Тест 2: TTS статус
        results["tts_status"] = self.test_tts_status()
        
        # Тест 3: Получение голосов
        results["voices"] = self.test_voices_endpoint()
        
        # Тест 4: Тест русской речи
        results["russian_test"] = self.test_russian_synthesis()
        
        # Вывод результатов
        print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТОВ:")
        print("=" * 30)
        
        for test_name, success in results.items():
            status = "✅ УСПЕШЕН" if success else "❌ ПРОВАЛЕН"
            print(f"   {test_name}: {status}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"\n📈 ИТОГО: {success_count}/{total_count} тестов прошли успешно")
        
        if success_count == total_count:
            print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        elif success_count > 0:
            print("⚠️  Часть тестов провалилась")
        else:
            print("❌ ВСЕ ТЕСТЫ ПРОВАЛИЛИСЬ")
        
        return results

def main():
    """Основная функция."""
    print("🎤 ТЕСТИРОВАНИЕ TTS API")
    print("=" * 50)
    
    # Проверяем, запущен ли backend
    print("🔍 Проверка доступности backend...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend доступен")
        else:
            print("❌ Backend недоступен")
            print("💡 Запустите backend: python -m uvicorn backend.app.main:app --reload")
            return
    except Exception as e:
        print("❌ Backend недоступен")
        print("💡 Запустите backend: python -m uvicorn backend.app.main:app --reload")
        return
    
    # Запускаем тесты
    tester = TTSAPITester()
    results = tester.run_all_tests()
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    
    if not results.get("voices", False):
        print("   1. Получите бесплатный API ключ на https://elevenlabs.io")
        print("   2. Установите: export ELEVENLABS_API_KEY='ваш_ключ'")
        print("   3. Перезапустите backend")
    
    if results.get("health", False) and results.get("tts_status", False):
        print("   ✅ Backend и TTS API работают корректно")
        print("   🎯 Готово к интеграции в frontend")

if __name__ == "__main__":
    main() 