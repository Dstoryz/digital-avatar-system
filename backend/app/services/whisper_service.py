"""
Сервис для распознавания речи с помощью Whisper.

Обеспечивает real-time и batch распознавание речи на русском языке.

Автор: Авабот
Версия: 1.0.0
"""

import logging
import os
import tempfile
from typing import Optional, Dict, Any
import whisper
import torch
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class WhisperService:
    """Сервис для распознавания речи с помощью Whisper."""
    
    def __init__(self, model_name: str = "base"):
        """
        Инициализация Whisper сервиса.
        
        Args:
            model_name: Название модели Whisper (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Загрузка модели Whisper."""
        try:
            logger.info(f"Загрузка модели Whisper: {self.model_name}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info(f"Модель Whisper {self.model_name} загружена на {self.device}")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели Whisper: {e}")
            raise
    
    def transcribe_audio_file(self, audio_path: str, language: str = "ru") -> Dict[str, Any]:
        """
        Транскрипция аудиофайла.
        
        Args:
            audio_path: Путь к аудиофайлу
            language: Язык аудио (ru, en, etc.)
            
        Returns:
            Результат транскрипции
        """
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Аудиофайл не найден: {audio_path}")
            
            logger.info(f"Транскрипция файла: {audio_path}")
            
            # Транскрипция с указанием языка
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                verbose=False
            )
            
            logger.info(f"Транскрипция завершена: {len(result['text'])} символов")
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "segments": result.get("segments", []),
                "confidence": self._calculate_confidence(result),
                "duration": result.get("duration", 0)
            }
            
        except Exception as e:
            logger.error(f"Ошибка транскрипции: {e}")
            raise
    
    def transcribe_audio_data(self, audio_data: bytes, language: str = "ru") -> Dict[str, Any]:
        """
        Транскрипция аудиоданных из памяти.
        
        Args:
            audio_data: Аудиоданные в байтах
            language: Язык аудио
            
        Returns:
            Результат транскрипции
        """
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                result = self.transcribe_audio_file(temp_path, language)
                return result
            finally:
                # Удаляем временный файл
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Ошибка транскрипции аудиоданных: {e}")
            raise
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """
        Вычисление средней уверенности транскрипции.
        
        Args:
            result: Результат транскрипции
            
        Returns:
            Средняя уверенность (0-1)
        """
        try:
            segments = result.get("segments", [])
            if not segments:
                return 0.0
            
            confidences = []
            for segment in segments:
                if "avg_logprob" in segment:
                    # Преобразуем log probability в вероятность
                    prob = np.exp(segment["avg_logprob"])
                    confidences.append(prob)
            
            if confidences:
                return float(np.mean(confidences))
            else:
                return 0.0
                
        except Exception as e:
            logger.warning(f"Ошибка вычисления уверенности: {e}")
            return 0.0
    
    def get_supported_languages(self) -> list:
        """Получение списка поддерживаемых языков."""
        return [
            "ru", "en", "es", "fr", "de", "it", "pt", "nl", "pl", "tr",
            "ja", "ko", "zh", "ar", "hi", "th", "vi", "id", "ms", "fa"
        ]
    
    def is_language_supported(self, language: str) -> bool:
        """
        Проверка поддержки языка.
        
        Args:
            language: Код языка
            
        Returns:
            True если язык поддерживается
        """
        return language in self.get_supported_languages()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Получение информации о модели."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "supported_languages": self.get_supported_languages(),
            "cuda_available": torch.cuda.is_available()
        }


# Глобальный экземпляр сервиса
whisper_service = None


def get_whisper_service(model_name: str = "base") -> WhisperService:
    """
    Получение глобального экземпляра Whisper сервиса.
    
    Args:
        model_name: Название модели
        
    Returns:
        Экземпляр WhisperService
    """
    global whisper_service
    
    if whisper_service is None or whisper_service.model_name != model_name:
        whisper_service = WhisperService(model_name)
    
    return whisper_service


def transcribe_audio(audio_path: str, language: str = "ru", model_name: str = "base") -> Dict[str, Any]:
    """
    Удобная функция для транскрипции аудио.
    
    Args:
        audio_path: Путь к аудиофайлу
        language: Язык аудио
        model_name: Название модели
        
    Returns:
        Результат транскрипции
    """
    service = get_whisper_service(model_name)
    return service.transcribe_audio_file(audio_path, language)


if __name__ == "__main__":
    # Тестирование сервиса
    import sys
    
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        service = WhisperService("base")
        result = service.transcribe_audio_file(audio_file)
        print(f"Текст: {result['text']}")
        print(f"Уверенность: {result['confidence']:.2f}")
        print(f"Длительность: {result['duration']:.2f} сек")
    else:
        print("Использование: python whisper_service.py <audio_file>") 