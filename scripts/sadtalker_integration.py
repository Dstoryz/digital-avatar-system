#!/usr/bin/env python3
"""
Интеграционный скрипт для SadTalker в проекте цифрового аватара.

Функции:
- Генерация анимированного видео из фото и аудио
- Оптимизация под RTX 3060 12GB VRAM
- Интеграция с FastAPI backend
- Управление памятью GPU

Автор: AI Assistant
Версия: 1.0.0
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
import subprocess
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SadTalkerIntegration:
    """Интеграция SadTalker для проекта цифрового аватара."""
    
    def __init__(self, sadtalker_path: str = "SadTalker"):
        """
        Инициализация интеграции SadTalker.
        
        Args:
            sadtalker_path: Путь к папке SadTalker
        """
        self.sadtalker_path = Path(sadtalker_path).resolve()
        self.device = "cuda"  # Предполагаем CUDA доступность
        
        logger.info(f"SadTalker инициализирован: {self.sadtalker_path}")
    
    def check_gpu_memory(self) -> bool:
        """
        Проверка доступности GPU памяти для SadTalker.
        
        Returns:
            True если достаточно памяти, False иначе
        """
        try:
            # Проверяем через nvidia-smi
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                memory_mb = int(result.stdout.strip())
                memory_gb = memory_mb / 1024
                logger.info(f"GPU память: {memory_gb:.1f} GB")
                return memory_gb >= 6  # Требуется минимум 6GB
            else:
                logger.warning("Не удалось получить информацию о GPU памяти")
                return True  # Предполагаем, что памяти достаточно
        except Exception as e:
            logger.warning(f"Ошибка проверки GPU памяти: {e}")
            return True
    
    def clear_gpu_memory(self):
        """Очистка GPU памяти после использования."""
        try:
            # Очистка через nvidia-smi
            subprocess.run(["nvidia-smi", "--gpu-reset"], capture_output=True)
            logger.info("GPU память очищена")
        except Exception as e:
            logger.warning(f"Не удалось очистить GPU память: {e}")
    
    def generate_animation(
        self,
        source_image: str,
        driven_audio: str,
        result_dir: str = "results",
        enhancer: str = "gfpgan",
        still_mode: bool = False,
        use_enhancer: bool = True,
        size: int = 256
    ) -> Dict[str, Any]:
        """
        Генерация анимированного видео с помощью SadTalker.
        
        Args:
            source_image: Путь к исходному изображению
            driven_audio: Путь к аудиофайлу
            result_dir: Папка для результатов
            enhancer: Тип улучшения лица (gfpgan, gfpgan_plus)
            still_mode: Режим статичного лица
            use_enhancer: Использовать улучшение лица
            size: Размер видео (256 или 512)
            
        Returns:
            Словарь с результатами генерации
        """
        try:
            # Проверка входных файлов
            if not os.path.exists(source_image):
                raise FileNotFoundError(f"Исходное изображение не найдено: {source_image}")
            if not os.path.exists(driven_audio):
                raise FileNotFoundError(f"Аудиофайл не найден: {driven_audio}")
            
            # Создание папки результатов
            os.makedirs(result_dir, exist_ok=True)
            
            # Формирование команды SadTalker
            cmd = [
                "python",
                str(self.sadtalker_path / "inference.py"),
                "--driven_audio", driven_audio,
                "--source_image", source_image,
                "--result_dir", result_dir,
                "--size", str(size)
            ]
            
            if use_enhancer:
                cmd.extend(["--enhancer", enhancer])
            
            if still_mode:
                cmd.append("--still_mode")
            
            logger.info(f"Запуск SadTalker: {' '.join(cmd)}")
            
            # Запуск процесса
            start_time = datetime.now()
            process = subprocess.run(
                cmd,
                cwd=self.sadtalker_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 минут таймаут
            )
            end_time = datetime.now()
            
            if process.returncode != 0:
                logger.error(f"Ошибка SadTalker: {process.stderr}")
                return {
                    "success": False,
                    "error": process.stderr,
                    "duration": (end_time - start_time).total_seconds()
                }
            
            # Поиск сгенерированного файла
            result_files = list(Path(result_dir).glob("*.mp4"))
            if not result_files:
                logger.error("Сгенерированный файл не найден")
                return {
                    "success": False,
                    "error": "Сгенерированный файл не найден",
                    "duration": (end_time - start_time).total_seconds()
                }
            
            result_file = result_files[-1]  # Последний созданный файл
            
            logger.info(f"Анимация сгенерирована: {result_file}")
            
            return {
                "success": True,
                "result_file": str(result_file),
                "file_size": result_file.stat().st_size,
                "duration": (end_time - start_time).total_seconds()
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Таймаут выполнения SadTalker")
            return {
                "success": False,
                "error": "Таймаут выполнения",
                "duration": 300
            }
        except Exception as e:
            logger.error(f"Ошибка генерации анимации: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": 0
            }
        finally:
            self.clear_gpu_memory()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Получение информации о моделях SadTalker."""
        try:
            checkpoints_dir = self.sadtalker_path / "checkpoints"
            models = {}
            
            if checkpoints_dir.exists():
                for model_file in checkpoints_dir.glob("*.pth"):
                    models[model_file.name] = {
                        "size": model_file.stat().st_size,
                        "path": str(model_file)
                    }
                
                for model_file in checkpoints_dir.glob("*.safetensors"):
                    models[model_file.name] = {
                        "size": model_file.stat().st_size,
                        "path": str(model_file)
                    }
            
            return {
                "sadtalker_path": str(self.sadtalker_path),
                "models": models,
                "device": self.device
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о моделях: {e}")
            return {"error": str(e)}

def main():
    """Тестовая функция для проверки интеграции."""
    integration = SadTalkerIntegration()
    
    # Проверка GPU
    print("=== Информация о системе ===")
    info = integration.get_model_info()
    print(json.dumps(info, indent=2, ensure_ascii=False))
    
    # Проверка GPU памяти
    print(f"\n=== Проверка GPU памяти ===")
    if integration.check_gpu_memory():
        print("✅ GPU память достаточна для SadTalker")
    else:
        print("⚠️ GPU память может быть недостаточна")
    
    # Тест генерации (если есть примеры)
    examples_dir = integration.sadtalker_path / "examples"
    if examples_dir.exists():
        source_image = examples_dir / "source_image" / "full_body_1.png"
        driven_audio = examples_dir / "driven_audio" / "bus_chinese.wav"
        
        if source_image.exists() and driven_audio.exists():
            print(f"\n=== Тест генерации ===")
            result = integration.generate_animation(
                str(source_image),
                str(driven_audio),
                result_dir="test_results"
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 