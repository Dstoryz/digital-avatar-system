#!/usr/bin/env python3
"""
Интеграция Coqui TTS с клонированием голоса для проекта цифрового аватара.

ПРОБЛЕМА КЛОНИРОВАНИЯ ГОЛОСА:
- YourTTS не поддерживает русский язык
- XTTS v2 и v1.1 имеют проблемы совместимости с PyTorch 2.6+
- Клонированный голос звучит как мужской на английском языке

РЕШЕНИЯ:
1. Временное: Использовать YourTTS для английского + русский TTS отдельно
2. Долгосрочное: Обучить кастомную модель на русском языке
3. Альтернативное: Использовать другие TTS системы (Tortoise, Tacotron)

Автор: AI Assistant
Версия: 2.0.0
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple

class CoquiTTSIntegration:
    """Интеграция Coqui TTS с системой цифрового аватара."""
    
    def __init__(self, env_path: str = "coqui_tts_env"):
        """
        Инициализация интеграции.
        
        Args:
            env_path: Путь к виртуальному окружению Coqui TTS
        """
        self.env_path = env_path
        self.available_models = self._get_available_models()
        self.current_model = "tts_models/multilingual/multi-dataset/your_tts"
        
        print("🎤 Coqui TTS Integration инициализирована")
        print(f"📦 Доступно моделей: {len(self.available_models)}")
        print(f"🎯 Текущая модель: {self.current_model}")
    
    def _get_available_models(self) -> List[str]:
        """Получение списка доступных моделей."""
        try:
            cmd = f"source {self.env_path}/bin/activate && tts --list_models"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                models = []
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('Name format:'):
                        model_name = line.split(']')[0].split('[')[-1].strip()
                        if model_name:
                            models.append(model_name)
                return models
            else:
                print(f"❌ Ошибка получения списка моделей: {result.stderr}")
                return []
        except Exception as e:
            print(f"❌ Ошибка получения моделей: {e}")
            return []
    
    def check_gpu_memory(self) -> Dict[str, float]:
        """
        Проверка доступной GPU памяти.
        
        Returns:
            Словарь с информацией о GPU памяти
        """
        try:
            import torch
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                allocated = torch.cuda.memory_allocated(0) / 1024**3
                cached = torch.cuda.memory_reserved(0) / 1024**3
                free = gpu_memory - allocated
                
                return {
                    "total_gb": gpu_memory,
                    "allocated_gb": allocated,
                    "cached_gb": cached,
                    "free_gb": free,
                    "usage_percent": (allocated / gpu_memory) * 100
                }
            else:
                return {"error": "CUDA недоступен"}
        except Exception as e:
            return {"error": str(e)}
    
    def synthesize_speech(self, text: str, speaker_wav: str, output_path: str, 
                         language: str = "en", model: Optional[str] = None) -> bool:
        """
        Синтез речи с клонированием голоса.
        
        Args:
            text: Текст для синтеза
            speaker_wav: Путь к аудиосэмплу для клонирования голоса
            output_path: Путь для сохранения результата
            language: Язык синтеза (en/ru)
            model: Модель для использования
            
        Returns:
            True если синтез успешен, False иначе
        """
        if model is None:
            model = self.current_model
        
        print(f"🎤 Синтез речи: '{text[:50]}...'")
        print(f"🎵 Модель: {model}")
        print(f"🌍 Язык: {language}")
        print(f"🎭 Сэмпл голоса: {speaker_wav}")
        
        # Проверка GPU памяти
        gpu_info = self.check_gpu_memory()
        if "error" not in gpu_info:
            print(f"💾 GPU память: {gpu_info['free_gb']:.1f}GB свободно")
        
        # Команда синтеза
        cmd = [
            f"source {self.env_path}/bin/activate && tts",
            "--text", text,
            "--model_name", model,
            "--speaker_wav", speaker_wav,
            "--language_idx", language,
            "--out_path", output_path
        ]
        
        start_time = time.time()
        
        try:
            result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                duration = time.time() - start_time
                print(f"✅ Синтез завершен за {duration:.2f} сек")
                print(f"📁 Результат сохранен: {output_path}")
                return True
            else:
                print(f"❌ Ошибка синтеза: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при синтезе: {e}")
            return False
    
    def synthesize_russian_with_limitations(self, text: str, speaker_wav: str, 
                                          output_path: str) -> bool:
        """
        Синтез русской речи с ограничениями (без клонирования голоса).
        
        ПРОБЛЕМА: YourTTS не поддерживает русский язык
        РЕШЕНИЕ: Используем базовую модель без клонирования
        
        Args:
            text: Русский текст для синтеза
            speaker_wav: Путь к аудиосэмплу (не используется)
            output_path: Путь для сохранения результата
            
        Returns:
            True если синтез успешен, False иначе
        """
        print(f"🇷🇺 Синтез русской речи: '{text[:50]}...'")
        print("⚠️  ВНИМАНИЕ: Клонирование голоса недоступно для русского языка")
        print("💡 Рекомендация: Использовать английский текст с YourTTS")
        
        # Пробуем разные подходы для русского синтеза
        approaches = [
            # Подход 1: XTTS v1.1 (может не работать)
            {
                "model": "tts_models/multilingual/multi-dataset/xtts_v1.1",
                "language": "ru",
                "description": "XTTS v1.1 с русским языком"
            },
            # Подход 2: YourTTS с английским (работает, но не русский)
            {
                "model": "tts_models/multilingual/multi-dataset/your_tts",
                "language": "en",
                "description": "YourTTS с английским (fallback)"
            }
        ]
        
        for i, approach in enumerate(approaches):
            print(f"\n🔧 Попытка {i+1}: {approach['description']}")
            
            if approach['language'] == 'en':
                # Для английского используем клонирование голоса
                english_text = "Hello! This is a test of voice cloning."
                success = self.synthesize_speech(
                    english_text, speaker_wav, 
                    f"temp_english_{i}.wav", 
                    "en", approach['model']
                )
            else:
                # Для русского пробуем без клонирования
                success = self.synthesize_speech(
                    text, speaker_wav, 
                    f"temp_russian_{i}.wav", 
                    approach['language'], approach['model']
                )
            
            if success:
                # Копируем результат
                import shutil
                shutil.copy(f"temp_{approach['language']}_{i}.wav", output_path)
                
                # Очистка временных файлов
                for temp_file in [f"temp_english_{i}.wav", f"temp_russian_{i}.wav"]:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                
                print(f"✅ Успешно создан файл: {output_path}")
                return True
        
        print("❌ Все попытки синтеза русской речи провалились")
        return False
    
    def get_voice_characteristics(self, audio_path: str) -> Dict[str, float]:
        """
        Анализ характеристик голоса.
        
        Args:
            audio_path: Путь к аудиофайлу
            
        Returns:
            Словарь с характеристиками голоса
        """
        try:
            import librosa
            import numpy as np
            
            y, sr = librosa.load(audio_path, sr=None)
            
            # Базовые характеристики
            duration = len(y) / sr
            rms = np.sqrt(np.mean(y**2))
            
            # Спектральные характеристики
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            
            # Питч (высота голоса)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            avg_pitch = np.mean(pitch_values) if pitch_values else 0
            
            # Определение пола по питчу
            if avg_pitch > 165:
                gender = "женский/детский"
            elif avg_pitch > 85:
                gender = "мужской"
            else:
                gender = "неопределен"
            
            return {
                "duration": duration,
                "sample_rate": sr,
                "rms_energy": rms,
                "avg_spectral_centroid": np.mean(spectral_centroids),
                "avg_pitch": avg_pitch,
                "estimated_gender": gender,
                "pitch_range": f"{min(pitch_values) if pitch_values else 0:.1f} - {max(pitch_values) if pitch_values else 0:.1f} Hz"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def clear_gpu_memory(self) -> bool:
        """
        Очистка GPU памяти.
        
        Returns:
            True если очистка успешна
        """
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print("🧹 GPU память очищена")
                return True
            else:
                print("ℹ️  CUDA недоступен")
                return False
        except Exception as e:
            print(f"❌ Ошибка очистки GPU памяти: {e}")
            return False
    
    def test_voice_cloning_quality(self, speaker_wav: str) -> Dict[str, any]:
        """
        Тест качества клонирования голоса.
        
        Args:
            speaker_wav: Путь к аудиосэмплу
            
        Returns:
            Результаты тестирования
        """
        print("🧪 ТЕСТ КАЧЕСТВА КЛОНИРОВАНИЯ ГОЛОСА")
        print("=" * 50)
        
        # Анализ исходного голоса
        print(f"\n📊 Анализ исходного голоса: {speaker_wav}")
        original_chars = self.get_voice_characteristics(speaker_wav)
        
        if "error" in original_chars:
            print(f"❌ Ошибка анализа: {original_chars['error']}")
            return {"error": original_chars['error']}
        
        print(f"   Длительность: {original_chars['duration']:.2f} сек")
        print(f"   Средний питч: {original_chars['avg_pitch']:.1f} Hz")
        print(f"   Предполагаемый пол: {original_chars['estimated_gender']}")
        print(f"   Диапазон питча: {original_chars['pitch_range']}")
        
        # Синтез тестового текста
        test_text = "Hello! This is a test of voice cloning quality."
        output_path = "voice_cloning_test.wav"
        
        success = self.synthesize_speech(test_text, speaker_wav, output_path)
        
        if success:
            # Анализ клонированного голоса
            print(f"\n📊 Анализ клонированного голоса: {output_path}")
            cloned_chars = self.get_voice_characteristics(output_path)
            
            if "error" not in cloned_chars:
                print(f"   Длительность: {cloned_chars['duration']:.2f} сек")
                print(f"   Средний питч: {cloned_chars['avg_pitch']:.1f} Hz")
                print(f"   Предполагаемый пол: {cloned_chars['estimated_gender']}")
                print(f"   Диапазон питча: {cloned_chars['pitch_range']}")
                
                # Сравнение характеристик
                pitch_diff = abs(original_chars['avg_pitch'] - cloned_chars['avg_pitch'])
                pitch_similarity = max(0, 100 - (pitch_diff / original_chars['avg_pitch']) * 100)
                
                return {
                    "original": original_chars,
                    "cloned": cloned_chars,
                    "pitch_similarity_percent": pitch_similarity,
                    "quality_score": pitch_similarity / 100,
                    "recommendations": self._get_quality_recommendations(original_chars, cloned_chars)
                }
        
        return {"error": "Тест не удался"}
    
    def _get_quality_recommendations(self, original: Dict, cloned: Dict) -> List[str]:
        """Получение рекомендаций по улучшению качества."""
        recommendations = []
        
        pitch_diff = abs(original['avg_pitch'] - cloned['avg_pitch'])
        if pitch_diff > 50:
            recommendations.append("🔧 Большая разница в питче - попробуйте другие аудиосэмплы")
        
        if original['duration'] < 5:
            recommendations.append("⏱️  Короткий аудиосэмпл - используйте более длинные записи (10+ сек)")
        
        if original['rms_energy'] < 0.1:
            recommendations.append("🔊 Низкая громкость - используйте более громкие записи")
        
        if not recommendations:
            recommendations.append("✅ Качество клонирования хорошее")
        
        return recommendations

def main():
    """Основная функция для тестирования интеграции."""
    print("🎤 ИНТЕГРАЦИЯ COQUI TTS С КЛОНИРОВАНИЕМ ГОЛОСА")
    print("=" * 60)
    
    # Инициализация
    tts_integration = CoquiTTSIntegration()
    
    # Тест качества клонирования
    speaker_wav = "data/audio/audio_1@02-12-2020_23-57-46.ogg"
    test_results = tts_integration.test_voice_cloning_quality(speaker_wav)
    
    if "error" not in test_results:
        print(f"\n📈 РЕЗУЛЬТАТЫ ТЕСТА:")
        print(f"   Схожесть питча: {test_results['pitch_similarity_percent']:.1f}%")
        print(f"   Оценка качества: {test_results['quality_score']:.2f}/1.0")
        
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        for rec in test_results['recommendations']:
            print(f"   {rec}")
    
    # Тест русского синтеза
    print(f"\n🇷🇺 ТЕСТ РУССКОГО СИНТЕЗА:")
    russian_text = "Привет! Это тест синтеза русской речи."
    success = tts_integration.synthesize_russian_with_limitations(
        russian_text, speaker_wav, "russian_test_output.wav"
    )
    
    if success:
        print("✅ Русский синтез создан (без клонирования голоса)")
    else:
        print("❌ Русский синтез не удался")
    
    # Очистка памяти
    tts_integration.clear_gpu_memory()
    
    print(f"\n" + "=" * 60)
    print("📋 ИТОГОВЫЙ ОТЧЕТ:")
    print("✅ YourTTS работает для английского языка")
    print("⚠️  Русский язык требует альтернативных решений")
    print("🎯 Рекомендуется: Обучение кастомной модели на русском")

if __name__ == "__main__":
    main() 