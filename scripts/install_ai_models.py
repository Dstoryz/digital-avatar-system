#!/usr/bin/env python3
"""
Скрипт для установки и настройки AI моделей для цифрового аватара
Устанавливает SadTalker, Coqui TTS, Whisper, Real-ESRGAN и другие модели
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import urllib.request
import zipfile
import tarfile

class AIModelInstaller:
    """Класс для установки AI моделей"""
    
    def __init__(self):
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.models_config = {
            "sadtalker": {
                "name": "SadTalker",
                "repo": "https://github.com/OpenTalker/SadTalker",
                "branch": "main",
                "requirements": [
                    "torch",
                    "torchvision",
                    "torchaudio",
                    "opencv-python",
                    "scipy",
                    "librosa",
                    "soundfile",
                    "yacs",
                    "gfpgan",
                    "facexlib",
                    "basicsr",
                    "face-alignment",
                    "dlib",
                    "gdown",
                    "imageio",
                    "imageio-ffmpeg",
                    "resampy",
                    "sklearn",
                    "scikit-image",
                    "tqdm",
                    "yaml",
                    "tb-nightly",
                    "tensorboardX",
                    "ffmpeg-python"
                ],
                "weights": {
                    "checkpoints": "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2/checkpoints.zip",
                    "gfpgan": "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2/GFPGANv1.4.pth",
                    "facexlib": "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2/detection_Resnet50_Final.pth"
                }
            },
            "coqui_tts": {
                "name": "Coqui TTS",
                "repo": "https://github.com/coqui-ai/TTS",
                "branch": "main",
                "requirements": [
                    "TTS",
                    "torch",
                    "torchaudio",
                    "numpy",
                    "scipy",
                    "librosa",
                    "soundfile",
                    "phonemizer",
                    "espeak-ng",
                    "tensorboard",
                    "matplotlib",
                    "seaborn"
                ]
            },
            "whisper": {
                "name": "OpenAI Whisper",
                "repo": "https://github.com/openai/whisper",
                "branch": "main",
                "requirements": [
                    "openai-whisper",
                    "torch",
                    "torchaudio",
                    "numpy",
                    "ffmpeg-python"
                ]
            },
            "real_esrgan": {
                "name": "Real-ESRGAN",
                "repo": "https://github.com/xinntao/Real-ESRGAN",
                "branch": "master",
                "requirements": [
                    "torch",
                    "torchvision",
                    "opencv-python",
                    "numpy",
                    "Pillow",
                    "scipy",
                    "basicsr",
                    "facexlib",
                    "gfpgan"
                ],
                "weights": {
                    "realesrgan": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
                    "realesrgan_anime": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"
                }
            },
            "wav2lip": {
                "name": "Wav2Lip",
                "repo": "https://github.com/Rudrabha/Wav2Lip",
                "branch": "master",
                "requirements": [
                    "torch",
                    "torchvision",
                    "opencv-python",
                    "numpy",
                    "scipy",
                    "librosa",
                    "soundfile",
                    "resampy",
                    "tqdm",
                    "gdown"
                ],
                "weights": {
                    "wav2lip": "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip.pth",
                    "wav2lip_gan": "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth",
                    "face_detection": "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/s3fd.pth"
                }
            }
        }
    
    def print_header(self, title: str):
        """Вывод заголовка"""
        print(f"\n{'='*60}")
        print(f"🤖 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str):
        """Вывод шага"""
        print(f"\n📋 {step}")
        print("-" * 40)
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> Tuple[bool, str]:
        """Выполнение команды"""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    
    def download_file(self, url: str, dest_path: Path) -> bool:
        """Скачивание файла"""
        try:
            print(f"Скачиваем {url}...")
            urllib.request.urlretrieve(url, dest_path)
            print(f"✅ Скачан: {dest_path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка скачивания: {e}")
            return False
    
    def extract_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """Распаковка архива"""
        try:
            print(f"Распаковываем {archive_path}...")
            
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.suffix in ['.tar', '.tar.gz', '.tgz']:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_to)
            
            print(f"✅ Распакован в {extract_to}")
            return True
        except Exception as e:
            print(f"❌ Ошибка распаковки: {e}")
            return False
    
    def clone_repository(self, repo_url: str, branch: str, dest_path: Path) -> bool:
        """Клонирование репозитория"""
        try:
            if dest_path.exists():
                print(f"📁 Репозиторий уже существует: {dest_path}")
                return True
            
            print(f"Клонируем {repo_url}...")
            success, output = self.run_command([
                "git", "clone", "-b", branch, repo_url, str(dest_path)
            ])
            
            if success:
                print(f"✅ Клонирован: {dest_path}")
                return True
            else:
                print(f"❌ Ошибка клонирования: {output}")
                return False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def install_requirements(self, requirements: List[str], model_name: str) -> bool:
        """Установка зависимостей"""
        self.print_step(f"Установка зависимостей для {model_name}")
        
        for package in requirements:
            print(f"Устанавливаем {package}...")
            success, output = self.run_command([
                sys.executable, "-m", "pip", "install", package
            ])
            
            if success:
                print(f"✅ {package} установлен")
            else:
                print(f"⚠️  Ошибка установки {package}: {output}")
                # Продолжаем установку других пакетов
    
    def install_sadtalker(self) -> bool:
        """Установка SadTalker"""
        self.print_step("Установка SadTalker")
        
        sadtalker_dir = self.models_dir / "sadtalker"
        
        # Клонируем репозиторий
        if not self.clone_repository(
            self.models_config["sadtalker"]["repo"],
            self.models_config["sadtalker"]["branch"],
            sadtalker_dir
        ):
            return False
        
        # Устанавливаем зависимости
        self.install_requirements(
            self.models_config["sadtalker"]["requirements"],
            "SadTalker"
        )
        
        # Создаем папку для весов
        weights_dir = sadtalker_dir / "checkpoints"
        weights_dir.mkdir(exist_ok=True)
        
        # Скачиваем веса
        for weight_name, weight_url in self.models_config["sadtalker"]["weights"].items():
            if weight_name == "checkpoints":
                weight_path = weights_dir / "checkpoints.zip"
                if self.download_file(weight_url, weight_path):
                    self.extract_archive(weight_path, weights_dir)
                    weight_path.unlink()  # Удаляем архив
            else:
                weight_path = weights_dir / f"{weight_name}.pth"
                self.download_file(weight_url, weight_path)
        
        print("✅ SadTalker установлен")
        return True
    
    def install_coqui_tts(self) -> bool:
        """Установка Coqui TTS"""
        self.print_step("Установка Coqui TTS")
        
        coqui_dir = self.models_dir / "coqui_tts"
        
        # Клонируем репозиторий
        if not self.clone_repository(
            self.models_config["coqui_tts"]["repo"],
            self.models_config["coqui_tts"]["branch"],
            coqui_dir
        ):
            return False
        
        # Устанавливаем зависимости
        self.install_requirements(
            self.models_config["coqui_tts"]["requirements"],
            "Coqui TTS"
        )
        
        # Устанавливаем TTS в режиме разработки
        success, output = self.run_command([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], cwd=coqui_dir)
        
        if success:
            print("✅ Coqui TTS установлен")
            return True
        else:
            print(f"❌ Ошибка установки: {output}")
            return False
    
    def install_whisper(self) -> bool:
        """Установка Whisper"""
        self.print_step("Установка OpenAI Whisper")
        
        # Устанавливаем зависимости
        self.install_requirements(
            self.models_config["whisper"]["requirements"],
            "Whisper"
        )
        
        # Скачиваем модели (базовая модель)
        print("Скачиваем базовую модель Whisper...")
        success, output = self.run_command([
            sys.executable, "-c", "import whisper; whisper.load_model('base')"
        ])
        
        if success:
            print("✅ Whisper установлен")
            return True
        else:
            print(f"❌ Ошибка установки: {output}")
            return False
    
    def install_real_esrgan(self) -> bool:
        """Установка Real-ESRGAN"""
        self.print_step("Установка Real-ESRGAN")
        
        esrgan_dir = self.models_dir / "real_esrgan"
        
        # Клонируем репозиторий
        if not self.clone_repository(
            self.models_config["real_esrgan"]["repo"],
            self.models_config["real_esrgan"]["branch"],
            esrgan_dir
        ):
            return False
        
        # Устанавливаем зависимости
        self.install_requirements(
            self.models_config["real_esrgan"]["requirements"],
            "Real-ESRGAN"
        )
        
        # Создаем папку для весов
        weights_dir = esrgan_dir / "experiments/pretrained_models"
        weights_dir.mkdir(parents=True, exist_ok=True)
        
        # Скачиваем веса
        for weight_name, weight_url in self.models_config["real_esrgan"]["weights"].items():
            weight_path = weights_dir / f"{weight_name}.pth"
            self.download_file(weight_url, weight_path)
        
        print("✅ Real-ESRGAN установлен")
        return True
    
    def install_wav2lip(self) -> bool:
        """Установка Wav2Lip"""
        self.print_step("Установка Wav2Lip")
        
        wav2lip_dir = self.models_dir / "wav2lip"
        
        # Клонируем репозиторий
        if not self.clone_repository(
            self.models_config["wav2lip"]["repo"],
            self.models_config["wav2lip"]["branch"],
            wav2lip_dir
        ):
            return False
        
        # Устанавливаем зависимости
        self.install_requirements(
            self.models_config["wav2lip"]["requirements"],
            "Wav2Lip"
        )
        
        # Создаем папку для весов
        weights_dir = wav2lip_dir / "checkpoints"
        weights_dir.mkdir(exist_ok=True)
        
        # Скачиваем веса
        for weight_name, weight_url in self.models_config["wav2lip"]["weights"].items():
            weight_path = weights_dir / f"{weight_name}.pth"
            self.download_file(weight_url, weight_path)
        
        print("✅ Wav2Lip установлен")
        return True
    
    def create_model_config(self) -> bool:
        """Создание конфигурации моделей"""
        self.print_step("Создание конфигурации моделей")
        
        config = {
            "models": {
                "sadtalker": {
                    "path": str(self.models_dir / "sadtalker"),
                    "checkpoints": str(self.models_dir / "sadtalker" / "checkpoints"),
                    "enabled": True
                },
                "coqui_tts": {
                    "path": str(self.models_dir / "coqui_tts"),
                    "enabled": True
                },
                "whisper": {
                    "model": "base",
                    "enabled": True
                },
                "real_esrgan": {
                    "path": str(self.models_dir / "real_esrgan"),
                    "enabled": True
                },
                "wav2lip": {
                    "path": str(self.models_dir / "wav2lip"),
                    "checkpoints": str(self.models_dir / "wav2lip" / "checkpoints"),
                    "enabled": True
                }
            },
            "gpu": {
                "enabled": True,
                "device": "cuda:0",
                "memory_fraction": 0.8
            },
            "processing": {
                "max_batch_size": 1,
                "timeout": 300,
                "temp_dir": "./temp"
            }
        }
        
        config_path = Path("models_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Конфигурация сохранена в {config_path}")
        return True
    
    def run_installation(self) -> None:
        """Запуск полной установки"""
        self.print_header("УСТАНОВКА AI МОДЕЛЕЙ")
        
        results = {}
        
        # Устанавливаем модели
        results["SadTalker"] = self.install_sadtalker()
        results["Coqui TTS"] = self.install_coqui_tts()
        results["Whisper"] = self.install_whisper()
        results["Real-ESRGAN"] = self.install_real_esrgan()
        results["Wav2Lip"] = self.install_wav2lip()
        
        # Создаем конфигурацию
        results["Configuration"] = self.create_model_config()
        
        # Отчет
        self.print_step("Отчет об установке")
        
        print("\n📊 Результаты установки:")
        for model, status in results.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {model}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"\n🎯 Общий результат: {success_count}/{total_count} моделей установлено")
        
        if success_count == total_count:
            print("🎉 Все AI модели успешно установлены!")
        else:
            print("⚠️  Некоторые модели не установлены")
            print("\n📋 Следующие шаги:")
            print("   1. Проверьте ошибки установки")
            print("   2. Установите недостающие зависимости")
            print("   3. Запустите тесты моделей")
        
        # Сохраняем отчет
        with open("ai_models_report.json", "w") as f:
            json.dump({
                "installation_results": results,
                "models_dir": str(self.models_dir),
                "total_models": total_count,
                "successful_installations": success_count
            }, f, indent=2)
        
        print(f"\n💾 Отчет сохранен в ai_models_report.json")

def main():
    """Основная функция"""
    installer = AIModelInstaller()
    installer.run_installation()

if __name__ == "__main__":
    main() 