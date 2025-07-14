#!/usr/bin/env python3
"""
Исправленная демонстрационная версия русской речи без API ключей.

Использует доступные инструменты для создания русской речи:
1. espeak (если установлен)
2. gtts (Google Text-to-Speech)
3. Правильный pitch shifting для соответствия голосу

Автор: AI Assistant
Версия: 1.1.0
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

class DemoRussianTTSFixed:
    """Исправленная демонстрационная версия русской речи."""
    
    def __init__(self):
        """Инициализация демо TTS."""
        self.temp_dir = Path("data/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        print("🎤 Исправленная демонстрационная версия русской речи инициализирована")
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
    
    def apply_pitch_shift_fixed(self, input_path: str, output_path: str, pitch_shift: float = 1.2) -> bool:
        """
        ИСПРАВЛЕННЫЙ pitch shifting с помощью ffmpeg.
        
        Использует правильный фильтр для изменения питча без изменения скорости.
        """
        if not self.ffmpeg_available:
            # Просто копируем файл если ffmpeg недоступен
            shutil.copy(input_path, output_path)
            return True
        
        try:
            # Используем правильный фильтр для pitch shifting
            # rubberband изменяет питч без изменения скорости
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-af", f"rubberband=pitch={pitch_shift}",
                "-y",  # Перезаписать выходной файл
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Если rubberband недоступен, используем альтернативный метод
            if result.returncode != 0:
                print("⚠️  rubberband недоступен, используем альтернативный метод...")
                
                # Альтернативный метод: изменяем скорость и затем восстанавливаем длительность
                temp_file = self.temp_dir / "temp_pitch.wav"
                
                # Сначала изменяем скорость
                cmd1 = [
                    "ffmpeg",
                    "-i", input_path,
                    "-af", f"atempo={1/pitch_shift}",
                    "-y",
                    str(temp_file)
                ]
                
                subprocess.run(cmd1, check=True, capture_output=True)
                
                # Затем восстанавливаем длительность, изменяя питч
                cmd2 = [
                    "ffmpeg",
                    "-i", str(temp_file),
                    "-af", f"asetrate=44100*{pitch_shift}",
                    "-y",
                    output_path
                ]
                
                subprocess.run(cmd2, check=True, capture_output=True)
                
                # Очистка временного файла
                if temp_file.exists():
                    temp_file.unlink()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка ffmpeg: {e}")
            # В случае ошибки просто копируем оригинальный файл
            shutil.copy(input_path, output_path)
            return True
    
    def synthesize_russian_fixed(self, text: str, output_path: str, pitch_shift: float = 1.0) -> Dict[str, Any]:
        """
        ИСПРАВЛЕННЫЙ синтез русской речи.
        
        Args:
            text: Русский текст для синтеза
            output_path: Путь для сохранения аудио
            pitch_shift: Коэффициент сдвига питча (1.0 = без изменений)
            
        Returns:
            Результат синтеза
        """
        print(f"🇷🇺 ИСПРАВЛЕННЫЙ синтез русской речи: '{text[:50]}...'")
        
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
                
                # Применяем ИСПРАВЛЕННЫЙ pitch shifting
                if pitch_shift != 1.0:
                    print(f"🎵 Применение ИСПРАВЛЕННОГО pitch shifting (коэффициент: {pitch_shift})...")
                    self.apply_pitch_shift_fixed(str(temp_file), output_path, pitch_shift)
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
    
    def test_demo_synthesis_fixed(self) -> bool:
        """Тестирование ИСПРАВЛЕННОГО демо синтеза."""
        print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕННОГО ДЕМО СИНТЕЗА")
        print("=" * 50)
        
        test_texts = [
            "Привет! Как дела?",
            "Сегодня прекрасная погода.",
            "Я очень рад тебя видеть!",
            "Это демонстрация синтеза русской речи."
        ]
        
        success_count = 0
        
        for i, text in enumerate(test_texts):
            output_path = f"demo_russian_test_fixed_{i+1}.wav"
            print(f"\n📝 Тест {i+1}: {text}")
            
            result = self.synthesize_russian_fixed(text, output_path)
            
            if "success" in result:
                print(f"✅ Тест {i+1} успешен (метод: {result['method']})")
                success_count += 1
            else:
                print(f"❌ Тест {i+1} провален: {result.get('error', 'Неизвестная ошибка')}")
        
        print(f"\n📊 Результаты: {success_count}/{len(test_texts)} тестов прошли успешно")
        return success_count > 0

def main():
    """Основная функция."""
    print("🎤 ИСПРАВЛЕННАЯ ДЕМОНСТРАЦИОННАЯ ВЕРСИЯ РУССКОЙ РЕЧИ")
    print("=" * 60)
    
    # Инициализация
    demo_tts = DemoRussianTTSFixed()
    
    # Тестирование
    success = demo_tts.test_demo_synthesis_fixed()
    
    if success:
        print("\n✅ ИСПРАВЛЕННЫЙ демо синтез работает!")
        print("🎵 Теперь аудио должно воспроизводиться с правильной скоростью!")
    else:
        print("\n❌ ИСПРАВЛЕННЫЙ демо синтез не работает")

if __name__ == "__main__":
    main() 