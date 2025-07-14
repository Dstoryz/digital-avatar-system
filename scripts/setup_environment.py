#!/usr/bin/env python3
"""
Скрипт для настройки окружения разработки цифрового аватара
Проверяет и устанавливает все необходимые зависимости
"""

import os
import sys
import subprocess
import platform
import json
from typing import Dict, List, Tuple, Any
from pathlib import Path

class EnvironmentSetup:
    """Класс для настройки окружения разработки"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_linux = self.system == "linux"
        self.is_windows = self.system == "windows"
        self.is_macos = self.system == "darwin"
        
        self.requirements = {
            "python": "3.10",
            "node": "18.0.0",
            "ffmpeg": "4.0",
            "cuda": "11.8",
            "redis": "6.0"
        }
        
        self.python_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "python-multipart",
            "pillow",
            "opencv-python",
            "numpy",
            "torch",
            "torchvision",
            "torchaudio",
            "transformers",
            "diffusers",
            "accelerate",
            "safetensors",
            "scipy",
            "librosa",
            "soundfile",
            "pydub",
            "redis",
            "websockets",
            "aiofiles",
            "python-jose[cryptography]",
            "passlib[bcrypt]",
            "python-dotenv",
            "requests",
            "httpx",
            "tqdm",
            "matplotlib",
            "seaborn",
            "jupyter"
        ]
        
        self.node_packages = [
            "react",
            "react-dom",
            "react-router-dom",
            "axios",
            "tailwindcss",
            "@tailwindcss/forms",
            "@headlessui/react",
            "@heroicons/react",
            "framer-motion",
            "react-dropzone",
            "react-hot-toast",
            "zustand",
            "typescript",
            "@types/react",
            "@types/react-dom",
            "@types/node",
            "vite",
            "@vitejs/plugin-react",
            "autoprefixer",
            "postcss"
        ]
        
        self.ai_models = {
            "sadtalker": "https://github.com/OpenTalker/SadTalker",
            "coqui_tts": "https://github.com/coqui-ai/TTS",
            "whisper": "openai-whisper",
            "real_esrgan": "https://github.com/xinntao/Real-ESRGAN",
            "wav2lip": "https://github.com/Rudrabha/Wav2Lip"
        }
    
    def print_header(self, title: str):
        """Вывод заголовка"""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str):
        """Вывод шага"""
        print(f"\n📋 {step}")
        print("-" * 40)
    
    def run_command(self, command: List[str], check: bool = True) -> Tuple[bool, str]:
        """Выполнение команды"""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=check
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    
    def check_python(self) -> bool:
        """Проверка Python"""
        self.print_step("Проверка Python")
        
        version = sys.version_info
        print(f"Текущая версия Python: {version.major}.{version.minor}.{version.micro}")
        
        if version.major >= 3 and version.minor >= 10:
            print("✅ Python версия подходит")
            return True
        else:
            print("❌ Требуется Python 3.10 или выше")
            return False
    
    def check_cuda(self) -> bool:
        """Проверка CUDA"""
        self.print_step("Проверка CUDA")
        
        # Проверяем nvidia-smi
        success, output = self.run_command(["nvidia-smi"], check=False)
        if success:
            print("✅ CUDA доступен")
            print(output.split('\n')[0])  # Первая строка с версией
            return True
        else:
            print("⚠️  CUDA не найден или не установлен")
            print("   Это нормально, если у вас нет GPU или вы используете CPU")
            return False
    
    def check_ffmpeg(self) -> bool:
        """Проверка FFmpeg"""
        self.print_step("Проверка FFmpeg")
        
        success, output = self.run_command(["ffmpeg", "-version"], check=False)
        if success:
            print("✅ FFmpeg установлен")
            version_line = output.split('\n')[0]
            print(f"   {version_line}")
            return True
        else:
            print("❌ FFmpeg не найден")
            if self.is_linux:
                print("   Установите: sudo apt install ffmpeg")
            elif self.is_macos:
                print("   Установите: brew install ffmpeg")
            elif self.is_windows:
                print("   Скачайте с: https://ffmpeg.org/download.html")
            return False
    
    def check_node(self) -> bool:
        """Проверка Node.js"""
        self.print_step("Проверка Node.js")
        
        success, output = self.run_command(["node", "--version"], check=False)
        if success:
            version = output.strip()
            print(f"✅ Node.js установлен: {version}")
            return True
        else:
            print("❌ Node.js не найден")
            print("   Установите с: https://nodejs.org/")
            return False
    
    def check_npm(self) -> bool:
        """Проверка npm"""
        self.print_step("Проверка npm")
        
        success, output = self.run_command(["npm", "--version"], check=False)
        if success:
            version = output.strip()
            print(f"✅ npm установлен: {version}")
            return True
        else:
            print("❌ npm не найден")
            return False
    
    def check_redis(self) -> bool:
        """Проверка Redis"""
        self.print_step("Проверка Redis")
        
        try:
            success, output = self.run_command(["redis-server", "--version"], check=False)
            if success:
                print("✅ Redis установлен")
                print(f"   {output.strip()}")
                return True
            else:
                print("⚠️  Redis не найден")
                if self.is_linux:
                    print("   Установите: sudo apt install redis-server")
                elif self.is_macos:
                    print("   Установите: brew install redis")
                elif self.is_windows:
                    print("   Скачайте с: https://redis.io/download")
                return False
        except FileNotFoundError:
            print("⚠️  Redis не найден")
            if self.is_linux:
                print("   Установите: sudo apt install redis-server")
            elif self.is_macos:
                print("   Установите: brew install redis")
            elif self.is_windows:
                print("   Скачайте с: https://redis.io/download")
            return False
    
    def install_python_packages(self) -> bool:
        """Установка Python пакетов"""
        self.print_step("Установка Python пакетов")
        
        print("Устанавливаем основные пакеты...")
        
        # Создаем requirements.txt
        requirements_file = "requirements.txt"
        with open(requirements_file, 'w') as f:
            for package in self.python_packages:
                f.write(f"{package}\n")
        
        print(f"Создан файл {requirements_file}")
        
        # Устанавливаем пакеты
        success, output = self.run_command([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        
        if success:
            print("✅ Python пакеты установлены")
            return True
        else:
            print("❌ Ошибка установки Python пакетов")
            print(output)
            return False
    
    def setup_frontend(self) -> bool:
        """Настройка Frontend"""
        self.print_step("Настройка Frontend")
        
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print("Создаем React приложение...")
            
            # Создаем React приложение с Vite
            success, output = self.run_command([
                "npm", "create", "vite@latest", "frontend", "--", "--template", "react-ts"
            ])
            
            if not success:
                print("❌ Ошибка создания React приложения")
                print(output)
                return False
        
        # Переходим в папку frontend
        os.chdir(frontend_dir)
        
        # Устанавливаем зависимости
        print("Устанавливаем npm зависимости...")
        success, output = self.run_command(["npm", "install"])
        
        if success:
            print("✅ Frontend зависимости установлены")
            os.chdir("..")  # Возвращаемся в корневую папку
            return True
        else:
            print("❌ Ошибка установки npm зависимостей")
            print(output)
            os.chdir("..")
            return False
    
    def create_env_files(self) -> bool:
        """Создание файлов окружения"""
        self.print_step("Создание файлов окружения")
        
        # Backend .env
        backend_env = """# Backend Environment Variables
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./digital_avatar.db

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=./uploads
PROCESSED_DIR=./processed

# AI Models
SADTALKER_PATH=./models/sadtalker
COQUI_TTS_PATH=./models/coqui_tts
WHISPER_MODEL=base
OLLAMA_URL=http://localhost:11434

# GPU Settings
USE_GPU=True
CUDA_VISIBLE_DEVICES=0
"""
        
        with open("backend/.env", "w") as f:
            f.write(backend_env)
        
        # Frontend .env
        frontend_env = """# Frontend Environment Variables
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=Digital Avatar
VITE_APP_VERSION=1.0.0
"""
        
        with open("frontend/.env", "w") as f:
            f.write(frontend_env)
        
        print("✅ Файлы окружения созданы")
        return True
    
    def create_directories(self) -> bool:
        """Создание необходимых директорий"""
        self.print_step("Создание директорий")
        
        directories = [
            "uploads",
            "processed",
            "models",
            "logs",
            "cache",
            "temp"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            print(f"   📁 {directory}/")
        
        print("✅ Директории созданы")
        return True
    
    def generate_setup_report(self, results: Dict[str, bool]) -> None:
        """Генерация отчета о настройке"""
        self.print_step("Отчет о настройке окружения")
        
        print("\n📊 Результаты проверки:")
        for component, status in results.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {component}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"\n🎯 Общий результат: {success_count}/{total_count} компонентов готово")
        
        if success_count == total_count:
            print("🎉 Окружение полностью настроено!")
        else:
            print("⚠️  Некоторые компоненты требуют ручной настройки")
            print("\n📋 Следующие шаги:")
            print("   1. Установите недостающие компоненты")
            print("   2. Настройте AI модели")
            print("   3. Запустите тесты")
    
    def run_setup(self) -> None:
        """Запуск полной настройки"""
        self.print_header("НАСТРОЙКА ОКРУЖЕНИЯ ЦИФРОВОГО АВАТАРА")
        
        results = {}
        
        # Проверки
        results["Python"] = self.check_python()
        results["CUDA"] = self.check_cuda()
        results["FFmpeg"] = self.check_ffmpeg()
        results["Node.js"] = self.check_node()
        results["npm"] = self.check_npm()
        results["Redis"] = self.check_redis()
        
        # Установки
        if results["Python"]:
            results["Python Packages"] = self.install_python_packages()
        
        if results["Node.js"] and results["npm"]:
            results["Frontend"] = self.setup_frontend()
        
        # Создание файлов и директорий
        results["Environment Files"] = self.create_env_files()
        results["Directories"] = self.create_directories()
        
        # Отчет
        self.generate_setup_report(results)
        
        # Сохраняем результаты
        with open("setup_report.json", "w") as f:
            json.dump({
                "timestamp": str(Path().cwd()),
                "system": self.system,
                "results": results
            }, f, indent=2)
        
        print(f"\n💾 Отчет сохранен в setup_report.json")

def main():
    """Основная функция"""
    setup = EnvironmentSetup()
    setup.run_setup()

if __name__ == "__main__":
    main() 