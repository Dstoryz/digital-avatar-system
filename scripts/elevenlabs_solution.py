#!/usr/bin/env python3
"""
Решение для русской речи с клонированием голоса через ElevenLabs API.

ElevenLabs предоставляет:
- Поддержку русского языка
- Качественное клонирование голоса
- Простой API
- Бесплатный план (10,000 символов/месяц)

Автор: AI Assistant
Версия: 1.0.0
"""

import os
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any

class ElevenLabsTTS:
    """Интеграция с ElevenLabs API для русской речи."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация ElevenLabs TTS.
        
        Args:
            api_key: API ключ ElevenLabs (можно получить на elevenlabs.io)
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            print("⚠️  API ключ ElevenLabs не найден")
            print("💡 Получите бесплатный ключ на https://elevenlabs.io")
            print("💡 Установите переменную окружения: export ELEVENLABS_API_KEY='ваш_ключ'")
        
        print("🎤 ElevenLabs TTS инициализирован")
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Получение списка доступных голосов."""
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
            
        Returns:
            Результат клонирования
        """
        if not self.api_key:
            return {"error": "API ключ не установлен"}
        
        if not os.path.exists(audio_file_path):
            return {"error": f"Аудиофайл не найден: {audio_file_path}"}
        
        try:
            # Подготовка файла
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
    
    def synthesize_speech(self, text: str, voice_id: str, output_path: str) -> Dict[str, Any]:
        """
        Синтез речи с клонированным голосом.
        
        Args:
            text: Текст для синтеза (поддерживает русский)
            voice_id: ID клонированного голоса
            output_path: Путь для сохранения аудио
            
        Returns:
            Результат синтеза
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
                # Сохранение аудио
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Речь синтезирована и сохранена: {output_path}")
                return {"success": True, "output_path": output_path}
            else:
                return {"error": f"Ошибка синтеза: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def test_russian_synthesis(self, voice_id: str) -> bool:
        """Тест синтеза русской речи."""
        test_texts = [
            "Привет! Как дела?",
            "Сегодня прекрасная погода.",
            "Я очень рад тебя видеть!",
            "Это тест синтеза русской речи с клонированием голоса."
        ]
        
        print("🧪 ТЕСТ СИНТЕЗА РУССКОЙ РЕЧИ")
        print("=" * 40)
        
        for i, text in enumerate(test_texts):
            output_path = f"elevenlabs_russian_test_{i+1}.wav"
            print(f"\n📝 Тест {i+1}: {text}")
            
            result = self.synthesize_speech(text, voice_id, output_path)
            
            if "success" in result:
                print(f"✅ Тест {i+1} успешен")
            else:
                print(f"❌ Тест {i+1} провален: {result.get('error', 'Неизвестная ошибка')}")
                return False
        
        return True

def main():
    """Основная функция для тестирования ElevenLabs."""
    print("🎤 ELEVENLABS TTS ДЛЯ РУССКОЙ РЕЧИ")
    print("=" * 50)
    
    # Инициализация
    tts = ElevenLabsTTS()
    
    # Проверка доступных голосов
    print("\n📋 Доступные голоса:")
    voices = tts.get_available_voices()
    
    if "error" in voices:
        print(f"❌ {voices['error']}")
        return
    
    # Показываем первые 5 голосов
    for i, voice in enumerate(voices.get('voices', [])[:5]):
        print(f"   {i+1}. {voice.get('name', 'Unknown')} (ID: {voice.get('voice_id', 'Unknown')})")
    
    # Клонирование голоса
    print(f"\n🎭 Клонирование голоса:")
    speaker_wav = "data/audio/audio_1@02-12-2020_23-57-46.ogg"
    
    clone_result = tts.clone_voice("Голос_девочки", speaker_wav)
    
    if "error" in clone_result:
        print(f"❌ Ошибка клонирования: {clone_result['error']}")
        print("\n💡 Для тестирования используйте существующий голос")
        
        # Используем первый доступный голос для теста
        if voices.get('voices'):
            test_voice_id = voices['voices'][0]['voice_id']
            print(f"🎯 Используем голос: {voices['voices'][0]['name']}")
            
            # Тест синтеза
            success = tts.test_russian_synthesis(test_voice_id)
            
            if success:
                print("\n✅ Все тесты русской речи прошли успешно!")
            else:
                print("\n❌ Тесты русской речи провалились")
    else:
        voice_id = clone_result.get('voice_id')
        print(f"✅ Голос клонирован с ID: {voice_id}")
        
        # Тест синтеза с клонированным голосом
        success = tts.test_russian_synthesis(voice_id)
        
        if success:
            print("\n✅ Все тесты русской речи с клонированным голосом прошли успешно!")
        else:
            print("\n❌ Тесты русской речи провалились")
    
    print(f"\n" + "=" * 50)
    print("📋 РЕЗЮМЕ:")
    print("✅ ElevenLabs поддерживает русский язык")
    print("✅ Качественное клонирование голоса")
    print("✅ Простой API интеграция")
    print("💡 Требует API ключ (бесплатный план доступен)")

if __name__ == "__main__":
    main() 