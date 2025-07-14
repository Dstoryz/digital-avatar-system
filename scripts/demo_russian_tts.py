#!/usr/bin/env python3
"""
Демонстрационная версия русской речи без API ключей.

Использует доступные инструменты для создания русской речи:
1. espeak (если установлен)
2. gtts (Google Text-to-Speech)
3. pitch shifting для соответствия голосу

Автор: AI Assistant
Версия: 1.0.0
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

class DemoRussianTTS:
    """Демонстрационная версия русской речи."""
    
    def __init__(self):
        """Инициализация демо TTS."""
        self.temp_dir = Path("data/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        print("🎤 Демонстрационная версия русской речи инициализирована")
        self._check_available_tools()
    
    def _check_available_tools(self):
        """Проверка доступных инструментов."""
        print("\n🔍 Проверка доступных инструментов:")
        
        # Проверка espeak
        try:
            subprocess.run(["espeak", "--version"], capture_output=True, check=True)
            print("✅ espeak доступен")
            self.espeak_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ espeak не найден")
            self.espeak_available = False
        
        # Проверка gtts
        try:
            import gtts
            print("✅ gtts доступен")
            self.gtts_available = True
        except ImportError:
            print("❌ gtts не найден")
            self.gtts_available = False
        
        # Проверка ffmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            print("✅ ffmpeg доступен")
            self.ffmpeg_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ ffmpeg не найден")
            self.ffmpeg_available = False
    
    def synthesize_with_espeak(self, text: str, output_path: str) -> bool:
        """Синтез с помощью espeak."""
        if not self.espeak_available:
            return False
        
        try:
            cmd = [
                "espeak", 
                "-v", "ru",  # Русский голос
                "-s", "150",  # Скорость
                "-p", "50",   # Питч
                "-a", "100",  # Громкость
                f'"{text}"',
                "-w", output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка espeak: {e}")
            return False
    
    def synthesize_with_gtts(self, text: str, output_path: str) -> bool:
        """Синтез с помощью Google TTS."""
        if not self.gtts_available:
            return False
        
        try:
            from gtts import gTTS
            
            tts = gTTS(text=text, lang='ru', slow=False)
            tts.save(output_path)
            return True
            
        except Exception as e:
            print(f"❌ Ошибка gtts: {e}")
            return False
    
    def apply_pitch_shift(self, input_path: str, output_path: str, pitch_shift: float = 1.2) -> bool:
        """Применение pitch shifting с помощью ffmpeg."""
        if not self.ffmpeg_available:
            # Просто копируем файл если ffmpeg недоступен
            shutil.copy(input_path, output_path)
            return True
        
        try:
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-af", f"asetrate=44100*{pitch_shift},aresample=44100",
                "-y",  # Перезаписать выходной файл
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка ffmpeg: {e}")
            return False
    
    def synthesize_russian(self, text: str, output_path: str, pitch_shift: float = 1.2) -> Dict[str, Any]:
        """
        Синтез русской речи.
        
        Args:
            text: Русский текст для синтеза
            output_path: Путь для сохранения аудио
            pitch_shift: Коэффициент сдвига питча (1.0 = без изменений)
            
        Returns:
            Результат синтеза
        """
        print(f"🇷🇺 Синтез русской речи: '{text[:50]}...'")
        
        # Создаем временный файл
        temp_file = self.temp_dir / "temp_synthesis.wav"
        
        # Пробуем разные методы синтеза
        synthesis_methods = [
            ("espeak", self.synthesize_with_espeak),
            ("gtts", self.synthesize_with_gtts)
        ]
        
        for method_name, method_func in synthesis_methods:
            print(f"🔧 Попытка синтеза с {method_name}...")
            
            if method_func(text, str(temp_file)):
                print(f"✅ Синтез с {method_name} успешен")
                
                # Применяем pitch shifting
                if pitch_shift != 1.0:
                    print(f"🎵 Применение pitch shifting (коэффициент: {pitch_shift})...")
                    self.apply_pitch_shift(str(temp_file), output_path, pitch_shift)
                else:
                    shutil.copy(str(temp_file), output_path)
                
                # Очистка временного файла
                if temp_file.exists():
                    temp_file.unlink()
                
                print(f"✅ Русская речь синтезирована: {output_path}")
                return {
                    "success": True,
                    "method": method_name,
                    "output_path": output_path,
                    "pitch_shift": pitch_shift
                }
        
        # Если ни один метод не сработал
        print("❌ Не удалось синтезировать речь ни одним методом")
        return {"error": "Не удалось синтезировать речь"}
    
    def test_demo_synthesis(self) -> bool:
        """Тестирование демо синтеза."""
        print("🧪 ТЕСТИРОВАНИЕ ДЕМО СИНТЕЗА")
        print("=" * 40)
        
        test_texts = [
            "Привет! Как дела?",
            "Сегодня прекрасная погода.",
            "Я очень рад тебя видеть!",
            "Это демонстрация синтеза русской речи."
        ]
        
        success_count = 0
        
        for i, text in enumerate(test_texts):
            output_path = f"demo_russian_test_{i+1}.wav"
            print(f"\n📝 Тест {i+1}: {text}")
            
            result = self.synthesize_russian(text, output_path)
            
            if "success" in result:
                print(f"✅ Тест {i+1} успешен (метод: {result['method']})")
                success_count += 1
            else:
                print(f"❌ Тест {i+1} провален: {result.get('error', 'Неизвестная ошибка')}")
        
        print(f"\n📊 Результаты: {success_count}/{len(test_texts)} тестов прошли успешно")
        return success_count > 0
    
    def create_voice_clone_demo(self, original_audio_path: str) -> Dict[str, Any]:
        """
        Демонстрация клонирования голоса.
        
        Args:
            original_audio_path: Путь к оригинальному аудиофайлу
            
        Returns:
            Результат демонстрации
        """
        print(f"🎭 ДЕМОНСТРАЦИЯ КЛОНИРОВАНИЯ ГОЛОСА")
        print("=" * 40)
        
        if not os.path.exists(original_audio_path):
            return {"error": f"Аудиофайл не найден: {original_audio_path}"}
        
        print(f"📁 Анализ оригинального голоса: {original_audio_path}")
        
        # Анализируем характеристики голоса (упрощенно)
        try:
            if self.ffmpeg_available:
                # Получаем информацию об аудио
                cmd = [
                    "ffprobe",
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    original_audio_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                audio_info = result.stdout
                
                print("✅ Анализ аудиофайла выполнен")
                print(f"📊 Информация об аудио: {len(audio_info)} символов")
            else:
                print("⚠️  ffmpeg недоступен, пропускаем анализ аудио")
        
        except Exception as e:
            print(f"⚠️  Ошибка анализа аудио: {e}")
        
        # Создаем демо синтез с похожими характеристиками
        demo_text = "Это демонстрация клонирования голоса с помощью доступных инструментов."
        output_path = "demo_voice_clone.wav"
        
        # Используем повышенный питч для имитации детского голоса
        result = self.synthesize_russian(demo_text, output_path, pitch_shift=1.3)
        
        if "success" in result:
            print(f"✅ Демо клонирование создано: {output_path}")
            return {
                "success": True,
                "original_audio": original_audio_path,
                "demo_output": output_path,
                "method": result["method"]
            }
        else:
            return {"error": "Не удалось создать демо клонирование"}

def main():
    """Основная функция."""
    print("🎤 ДЕМОНСТРАЦИОННАЯ ВЕРСИЯ РУССКОЙ РЕЧИ")
    print("=" * 50)
    
    # Инициализация
    demo_tts = DemoRussianTTS()
    
    # Тестирование
    success = demo_tts.test_demo_synthesis()
    
    if success:
        print("\n✅ Демо синтез работает!")
        
        # Демонстрация клонирования голоса
        speaker_wav = "data/audio/audio_1@02-12-2020_23-57-46.ogg"
        clone_result = demo_tts.create_voice_clone_demo(speaker_wav)
        
        if "success" in clone_result:
            print("🎭 Демо клонирование голоса создано!")
        else:
            print(f"❌ Ошибка демо клонирования: {clone_result.get('error')}")
    else:
        print("\n❌ Демо синтез не работает")
        print("💡 Установите espeak или gtts:")
        print("   sudo apt install espeak")
        print("   pip install gtts")
    
    print(f"\n" + "=" * 50)
    print("📋 РЕЗЮМЕ:")
    print("✅ Работает без API ключей")
    print("✅ Поддерживает русский язык")
    print("⚠️  Качество ниже, чем у ElevenLabs")
    print("💡 Для лучшего качества используйте ElevenLabs API")

if __name__ == "__main__":
    main() 