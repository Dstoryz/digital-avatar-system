#!/usr/bin/env python3
"""
Скрипт для тестирования обученной модели YourTTS
"""

import os
import subprocess
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_trained_model():
    """Тестирует обученную модель YourTTS"""
    logger.info("🧪 Тестирование обученной модели YourTTS...")
    
    # Проверяем наличие обученной модели
    model_path = "tts_train_output/best_model.pth"
    if not Path(model_path).exists():
        logger.error(f"❌ Обученная модель не найдена: {model_path}")
        return False
    
    # Тестовые фразы
    test_phrases = [
        "Привет! Как дела?",
        "Сегодня прекрасная погода.",
        "Я очень рада вас видеть.",
        "Спасибо за внимание.",
        "До свидания!"
    ]
    
    # Референсное аудио
    reference_wav = "training_data/wav/audio_94@17-09-2021_09-58-16.wav"
    
    results = []
    
    for i, phrase in enumerate(test_phrases):
        output_path = f"test_output_{i+1}.wav"
        
        logger.info(f"Тестируем фразу {i+1}: {phrase}")
        
        cmd = [
            "tts",
            "--text", phrase,
            "--model_path", model_path,
            "--config_path", "tts_train_output/config.json",
            "--speaker_wav", reference_wav,
            "--language_idx", "en",
            "--out_path", output_path
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"✅ Создан файл: {output_path}")
            results.append((phrase, output_path, True))
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Ошибка при синтезе: {e}")
            results.append((phrase, output_path, False))
    
    # Выводим результаты
    logger.info("\n📊 Результаты тестирования:")
    logger.info("=" * 50)
    
    success_count = 0
    for phrase, output_path, success in results:
        status = "✅ Успешно" if success else "❌ Ошибка"
        logger.info(f"{status}: {phrase}")
        if success:
            success_count += 1
    
    success_rate = (success_count / len(results)) * 100
    logger.info(f"\n🎯 Общий результат: {success_count}/{len(results)} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        logger.info("🎉 Модель работает отлично!")
    elif success_rate >= 60:
        logger.info("👍 Модель работает хорошо!")
    else:
        logger.warning("⚠️ Модель требует доработки!")
    
    return success_rate >= 60

def main():
    """Основная функция"""
    logger.info("🧪 Тестирование обученной модели YourTTS")
    logger.info("=" * 50)
    
    success = test_trained_model()
    
    if success:
        logger.info("🎉 Тестирование завершено успешно!")
        logger.info("🎤 Модель готова к использованию в системе!")
    else:
        logger.error("❌ Тестирование выявило проблемы!")
    
    return success

if __name__ == "__main__":
    main() 