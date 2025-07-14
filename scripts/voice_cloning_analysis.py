#!/usr/bin/env python3
"""
Анализ проблемы с клонированием голоса в Coqui TTS.

Проблема: Клонированный голос звучит как мужской, хотя исходные сэмплы - голос девочки.
Возможные причины:
1. Неправильное извлечение характеристик голоса
2. Проблемы с качеством аудиосэмплов
3. Ограничения модели YourTTS
4. Несовместимость языков (русский vs английский)

Автор: AI Assistant
Версия: 1.0.0
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import librosa
import numpy as np

def analyze_audio_file(file_path):
    """Анализ аудиофайла для определения характеристик голоса."""
    try:
        # Загрузка аудио
        y, sr = librosa.load(file_path, sr=None)
        
        # Базовые характеристики
        duration = len(y) / sr
        rms = np.sqrt(np.mean(y**2))
        
        # Спектральные характеристики
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        
        # Питч (высота голоса)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        if pitch_values:
            avg_pitch = np.mean(pitch_values)
            pitch_std = np.std(pitch_values)
        else:
            avg_pitch = 0
            pitch_std = 0
        
        # Определение пола по питчу (приблизительно)
        if avg_pitch > 165:  # Hz
            gender = "женский/детский"
        elif avg_pitch > 85:
            gender = "мужской"
        else:
            gender = "неопределен"
        
        return {
            "file": file_path,
            "duration": duration,
            "sample_rate": sr,
            "rms_energy": rms,
            "avg_spectral_centroid": np.mean(spectral_centroids),
            "avg_spectral_rolloff": np.mean(spectral_rolloff),
            "avg_pitch": avg_pitch,
            "pitch_std": pitch_std,
            "estimated_gender": gender,
            "pitch_range": f"{min(pitch_values) if pitch_values else 0:.1f} - {max(pitch_values) if pitch_values else 0:.1f} Hz"
        }
    except Exception as e:
        return {"file": file_path, "error": str(e)}

def test_different_speakers():
    """Тест с разными аудиосэмплами для сравнения."""
    audio_files = list(Path("data/audio").glob("*.ogg"))[:5]
    
    print("=== АНАЛИЗ ИСХОДНЫХ АУДИОСЭМПЛОВ ===")
    for i, audio_file in enumerate(audio_files):
        print(f"\n{i+1}. {audio_file.name}")
        analysis = analyze_audio_file(str(audio_file))
        if "error" not in analysis:
            print(f"   Длительность: {analysis['duration']:.2f} сек")
            print(f"   Частота дискретизации: {analysis['sample_rate']} Hz")
            print(f"   Средний питч: {analysis['avg_pitch']:.1f} Hz")
            print(f"   Предполагаемый пол: {analysis['estimated_gender']}")
            print(f"   Диапазон питча: {analysis['pitch_range']}")
        else:
            print(f"   Ошибка: {analysis['error']}")

def create_test_samples():
    """Создание тестовых сэмплов с разными настройками."""
    print("\n=== СОЗДАНИЕ ТЕСТОВЫХ СЭМПЛОВ ===")
    
    # Тест 1: Короткий сэмпл
    cmd1 = [
        "source coqui_tts_env/bin/activate && tts",
        "--text", "Hello!",
        "--model_name", "tts_models/multilingual/multi-dataset/your_tts",
        "--speaker_wav", "data/audio/audio_1@02-12-2020_23-57-46.ogg",
        "--language_idx", "en",
        "--out_path", "test_short.wav"
    ]
    
    # Тест 2: С разными аудиосэмплами
    audio_files = list(Path("data/audio").glob("*.ogg"))[:3]
    
    for i, audio_file in enumerate(audio_files):
        cmd = [
            "source coqui_tts_env/bin/activate && tts",
            "--text", "Hello! This is a test.",
            "--model_name", "tts_models/multilingual/multi-dataset/your_tts",
            "--speaker_wav", str(audio_file),
            "--language_idx", "en",
            "--out_path", f"test_speaker_{i+1}.wav"
        ]
        
        print(f"Создание теста с {audio_file.name}...")
        try:
            subprocess.run(" ".join(cmd), shell=True, check=True)
            print(f"✅ Тест {i+1} создан")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка в тесте {i+1}: {e}")

def analyze_generated_samples():
    """Анализ сгенерированных сэмплов."""
    print("\n=== АНАЛИЗ СГЕНЕРИРОВАННЫХ СЭМПЛОВ ===")
    
    generated_files = list(Path(".").glob("test_*.wav"))
    
    for file in generated_files:
        print(f"\n{file.name}:")
        analysis = analyze_audio_file(str(file))
        if "error" not in analysis:
            print(f"   Длительность: {analysis['duration']:.2f} сек")
            print(f"   Средний питч: {analysis['avg_pitch']:.1f} Hz")
            print(f"   Предполагаемый пол: {analysis['estimated_gender']}")
            print(f"   Диапазон питча: {analysis['pitch_range']}")
        else:
            print(f"   Ошибка: {analysis['error']}")

def suggest_solutions():
    """Предложения по решению проблемы."""
    print("\n=== ПРЕДЛОЖЕНИЯ ПО РЕШЕНИЮ ===")
    
    solutions = [
        "1. **Попробовать XTTS v2** (поддерживает русский язык):",
        "   - Установить более старую версию PyTorch (2.5.x)",
        "   - Или использовать Docker с совместимой версией",
        "",
        "2. **Улучшить качество аудиосэмплов**:",
        "   - Записать новые сэмплы в тихом помещении",
        "   - Использовать качественный микрофон",
        "   - Нормализовать громкость",
        "",
        "3. **Попробовать другие модели**:",
        "   - Coqui TTS с fine-tuning",
        "   - Tortoise TTS",
        "   - Tacotron 2 с клонированием",
        "",
        "4. **Обучение кастомной модели**:",
        "   - Собрать больше аудиосэмплов (30+ минут)",
        "   - Обучить модель с нуля на русском языке",
        "",
        "5. **Временное решение**:",
        "   - Использовать YourTTS для английского",
        "   - Добавить русский TTS без клонирования",
        "   - Объединить результаты"
    ]
    
    for solution in solutions:
        print(solution)

def main():
    """Основная функция анализа."""
    print("🔍 АНАЛИЗ ПРОБЛЕМЫ КЛОНИРОВАНИЯ ГОЛОСА")
    print("=" * 50)
    
    # Анализ исходных сэмплов
    test_different_speakers()
    
    # Создание тестовых сэмплов
    create_test_samples()
    
    # Анализ сгенерированных сэмплов
    analyze_generated_samples()
    
    # Предложения по решению
    suggest_solutions()
    
    print("\n" + "=" * 50)
    print("📋 РЕЗЮМЕ:")
    print("- Проблема: YourTTS не поддерживает русский язык")
    print("- Решение: Использовать XTTS v2 или обучить кастомную модель")
    print("- Альтернатива: Комбинировать английский TTS + русский TTS")

if __name__ == "__main__":
    main() 