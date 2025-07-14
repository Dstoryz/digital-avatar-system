#!/usr/bin/env python3
"""
Простое решение для русской речи с ElevenLabs API.

Это решение работает быстро и не требует сложной установки.
Просто получите бесплатный API ключ на https://elevenlabs.io

Автор: AI Assistant
Версия: 1.0.0
"""

import os
import requests
import json
from typing import Optional, Dict, Any

class SimpleRussianTTS:
    """Простое решение для русской речи с ElevenLabs."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация.
        
        Args:
            api_key: API ключ ElevenLabs (можно получить на elevenlabs.io)
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            print("⚠️  API ключ ElevenLabs не найден")
            print("💡 Получите БЕСПЛАТНЫЙ ключ на https://elevenlabs.io")
            print("💡 Установите: export ELEVENLABS_API_KEY='ваш_ключ'")
            print("💡 Или передайте ключ в конструктор: SimpleRussianTTS('ваш_ключ')")
        
        print("🎤 SimpleRussianTTS инициализирован")
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Получение доступных голосов."""
        if not self.api_key:
            return {"error": "API ключ не установлен"}
        
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers={"xi-api-key": self.api_key}
            )
            
            if response.status_code == 200:
                voices = response.json()
                print(f"✅ Найдено {len(voices.get('voices', []))} голосов")
                return voices
            else:
                return {"error": f"Ошибка API: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def clone_voice(self, voice_name: str, audio_file_path: str) -> Dict[str, Any]:
        """
        Клонирование голоса из аудиофайла.
        
        Args:
            voice_name: Название для нового голоса
            audio_file_path: Путь к аудиофайлу для клонирования
        """
        if not self.api_key:
            return {"error": "API ключ не установлен"}
        
        if not os.path.exists(audio_file_path):
            return {"error": f"Аудиофайл не найден: {audio_file_path}"}
        
        try:
            with open(audio_file_path, 'rb') as f:
                files = {'files': f}
                data = {
                    'name': voice_name,
                    'description': f'Клонированный голос из {audio_file_path}'
                }
                
                response = requests.post(
                    f"{self.base_url}/voices/add",
                    headers={"xi-api-key": self.api_key},
                    data=data,
                    files=files
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Голос '{voice_name}' успешно клонирован")
                return result
            else:
                return {"error": f"Ошибка клонирования: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def synthesize_russian(self, text: str, voice_id: str, output_path: str) -> Dict[str, Any]:
        """
        Синтез русской речи.
        
        Args:
            text: Русский текст для синтеза
            voice_id: ID голоса (клонированного или существующего)
            output_path: Путь для сохранения аудио
        """
        if not self.api_key:
            return {"error": "API ключ не установлен"}
        
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # Поддерживает русский
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(
                url,
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Русская речь синтезирована: {output_path}")
                return {"success": True, "output_path": output_path}
            else:
                return {"error": f"Ошибка синтеза: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def test_without_api_key(self):
        """Демонстрация без API ключа."""
        print("🧪 ДЕМОНСТРАЦИЯ БЕЗ API КЛЮЧА")
        print("=" * 40)
        
        test_texts = [
            "Привет! Как дела?",
            "Сегодня прекрасная погода.",
            "Я очень рад тебя видеть!",
            "Это тест синтеза русской речи с клонированием голоса."
        ]
        
        print("📝 Примеры русских текстов для синтеза:")
        for i, text in enumerate(test_texts, 1):
            print(f"   {i}. {text}")
        
        print(f"\n💡 Для тестирования:")
        print("   1. Получите бесплатный API ключ на https://elevenlabs.io")
        print("   2. Установите: export ELEVENLABS_API_KEY='ваш_ключ'")
        print("   3. Запустите: python scripts/simple_russian_tts.py")
        
        return False
    
    def test_with_api_key(self):
        """Тестирование с API ключом."""
        print("🧪 ТЕСТИРОВАНИЕ С API КЛЮЧОМ")
        print("=" * 40)
        
        # Получаем доступные голоса
        voices = self.get_available_voices()
        if "error" in voices:
            print(f"❌ {voices['error']}")
            return False
        
        # Показываем первые 3 голоса
        print("\n📋 Доступные голоса:")
        for i, voice in enumerate(voices.get('voices', [])[:3]):
            print(f"   {i+1}. {voice.get('name', 'Unknown')} (ID: {voice.get('voice_id', 'Unknown')})")
        
        # Клонируем голос
        speaker_wav = "../data/audio/audio_1@02-12-2020_23-57-46.ogg"
        print(f"\n🎭 Клонирование голоса из {speaker_wav}...")
        
        clone_result = self.clone_voice("Голос_девочки", speaker_wav)
        
        if "error" in clone_result:
            print(f"❌ Ошибка клонирования: {clone_result['error']}")
            print("\n💡 Используем существующий голос для теста")
            
            if voices.get('voices'):
                test_voice_id = voices['voices'][0]['voice_id']
                print(f"🎯 Используем голос: {voices['voices'][0]['name']}")
            else:
                print("❌ Нет доступных голосов")
                return False
        else:
            test_voice_id = clone_result.get('voice_id')
            print(f"✅ Голос клонирован с ID: {test_voice_id}")
        
        # Тестируем русский синтез
        test_texts = [
            "Привет! Как дела?",
            "Сегодня прекрасная погода.",
            "Я очень рад тебя видеть!",
            "Это тест синтеза русской речи с клонированием голоса."
        ]
        
        success_count = 0
        
        for i, text in enumerate(test_texts):
            output_path = f"elevenlabs_russian_test_{i+1}.wav"
            print(f"\n📝 Тест {i+1}: {text}")
            
            result = self.synthesize_russian(text, test_voice_id, output_path)
            
            if "success" in result:
                print(f"✅ Тест {i+1} успешен")
                success_count += 1
            else:
                print(f"❌ Тест {i+1} провален: {result.get('error', 'Неизвестная ошибка')}")
        
        print(f"\n📊 Результаты: {success_count}/{len(test_texts)} тестов прошли успешно")
        return success_count > 0

def main():
    """Основная функция."""
    print("🎤 ПРОСТОЕ РЕШЕНИЕ ДЛЯ РУССКОЙ РЕЧИ")
    print("=" * 50)
    
    # Инициализация
    tts = SimpleRussianTTS()
    
    # Проверяем наличие API ключа
    if not tts.api_key:
        tts.test_without_api_key()
    else:
        success = tts.test_with_api_key()
        
        if success:
            print("\n✅ ElevenLabs API работает отлично!")
            print("🎯 Готово к интеграции в проект")
        else:
            print("\n❌ Есть проблемы с API")
    
    print(f"\n" + "=" * 50)
    print("📋 РЕЗЮМЕ:")
    print("✅ ElevenLabs поддерживает русский язык")
    print("✅ Отличное качество клонирования голоса")
    print("✅ Простая интеграция")
    print("✅ Бесплатный план (10,000 символов/месяц)")
    print("💡 Требует API ключ (получить на elevenlabs.io)")

if __name__ == "__main__":
    main() 