#!/usr/bin/env python3
"""
Скрипт для мониторинга процесса обучения YourTTS
"""

import os
import time
import psutil
import subprocess
from pathlib import Path

def monitor_training():
    """Мониторит процесс обучения YourTTS"""
    print("🔍 Мониторинг обучения YourTTS")
    print("=" * 50)
    
    while True:
        # Проверяем процесс обучения
        training_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                if 'train_tts' in ' '.join(proc.info['cmdline'] or []):
                    training_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if training_processes:
            print(f"✅ Процесс обучения активен: PID {training_processes[0]['pid']}")
            print(f"   CPU: {training_processes[0]['cpu_percent']:.1f}%")
            print(f"   Memory: {training_processes[0]['memory_percent']:.1f}%")
        else:
            print("❌ Процесс обучения не найден")
            break
        
        # Проверяем папку с результатами
        if Path("tts_train_output").exists():
            files = list(Path("tts_train_output").glob("*"))
            if files:
                print(f"📁 Найдено файлов в tts_train_output: {len(files)}")
                for file in files[-3:]:  # Показываем последние 3 файла
                    print(f"   {file.name}")
        
        # Проверяем использование GPU
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                gpu_info = result.stdout.strip().split(', ')
                print(f"🎮 GPU: {gpu_info[0]}% | Memory: {gpu_info[1]}/{gpu_info[2]} MB")
        except:
            print("🎮 GPU: недоступен")
        
        print("-" * 50)
        time.sleep(30)  # Проверяем каждые 30 секунд

if __name__ == "__main__":
    try:
        monitor_training()
    except KeyboardInterrupt:
        print("\n👋 Мониторинг остановлен") 