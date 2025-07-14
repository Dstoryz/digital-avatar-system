#!/usr/bin/env python3
"""
Мониторинг системы цифрового аватара.

Отслеживает статус backend, frontend, обучения YourTTS и HierSpeech_TTS API.

Автор: Авабот
Версия: 1.0.0
"""

import asyncio
import json
import logging
import os
import psutil
import requests
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemMonitor:
    """Монитор системы цифрового аватара."""
    
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:3000"
        self.hier_tts_url = "http://127.0.0.1:8001"
        
    def check_process(self, process_name: str) -> Optional[Dict]:
        """Проверяет статус процесса по имени."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                if process_name.lower() in proc.info['name'].lower():
                    return {
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent'],
                        'status': 'running'
                    }
            return None
        except Exception as e:
            logger.error(f"Ошибка проверки процесса {process_name}: {e}")
            return None
    
    def check_port(self, port: int) -> bool:
        """Проверяет, занят ли порт."""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
            return False
        except Exception as e:
            logger.error(f"Ошибка проверки порта {port}: {e}")
            return False
    
    def check_http_service(self, url: str, timeout: int = 5) -> Dict:
        """Проверяет доступность HTTP сервиса."""
        try:
            response = requests.get(f"{url}/health", timeout=timeout)
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'data': response.json()
                }
            else:
                return {
                    'status': 'error',
                    'status_code': response.status_code,
                    'data': None
                }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'unavailable',
                'error': str(e),
                'data': None
            }
    
    def check_training_progress(self) -> Dict:
        """Проверяет прогресс обучения YourTTS."""
        try:
            # Ищем процесс обучения
            train_process = self.check_process("train_tts")
            if not train_process:
                return {'status': 'not_running'}
            
            # Проверяем использование GPU
            gpu_info = self.get_gpu_info()
            
            # Ищем логи обучения
            log_files = self.find_training_logs()
            
            return {
                'status': 'running',
                'process': train_process,
                'gpu': gpu_info,
                'logs': log_files
            }
        except Exception as e:
            logger.error(f"Ошибка проверки обучения: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_gpu_info(self) -> Dict:
        """Получает информацию о GPU."""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_info = []
                for i in range(gpu_count):
                    props = torch.cuda.get_device_properties(i)
                    gpu_info.append({
                        'id': i,
                        'name': props.name,
                        'memory_total': props.total_memory / 1024**3,  # GB
                        'memory_allocated': torch.cuda.memory_allocated(i) / 1024**3,  # GB
                        'memory_cached': torch.cuda.memory_reserved(i) / 1024**3,  # GB
                    })
                return {'available': True, 'devices': gpu_info}
            else:
                return {'available': False}
        except ImportError:
            return {'available': False, 'error': 'PyTorch not installed'}
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    def find_training_logs(self) -> List[str]:
        """Ищет файлы логов обучения."""
        log_files = []
        try:
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith('.log') and 'train' in file.lower():
                        log_files.append(os.path.join(root, file))
        except Exception as e:
            logger.error(f"Ошибка поиска логов: {e}")
        return log_files
    
    def get_system_info(self) -> Dict:
        """Получает общую информацию о системе."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total / 1024**3,  # GB
                    'available': memory.available / 1024**3,  # GB
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total / 1024**3,  # GB
                    'free': disk.free / 1024**3,  # GB
                    'percent': (disk.used / disk.total) * 100
                }
            }
        except Exception as e:
            logger.error(f"Ошибка получения системной информации: {e}")
            return {}
    
    def generate_report(self) -> Dict:
        """Генерирует полный отчет о состоянии системы."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_info(),
            'services': {
                'backend': {
                    'port_8000': self.check_port(8000),
                    'http_status': self.check_http_service(self.backend_url)
                },
                'frontend': {
                    'port_3000': self.check_port(3000),
                    'http_status': self.check_http_service(self.frontend_url)
                },
                'hier_tts': {
                    'port_8001': self.check_port(8001),
                    'http_status': self.check_http_service(self.hier_tts_url)
                }
            },
            'processes': {
                'uvicorn': self.check_process('uvicorn'),
                'vite': self.check_process('vite'),
                'train_tts': self.check_process('train_tts'),
                'python': self.check_process('python')
            },
            'training': self.check_training_progress(),
            'gpu': self.get_gpu_info()
        }
        
        return report
    
    def print_status(self, report: Dict):
        """Выводит статус системы в консоль."""
        print("\n" + "="*60)
        print(f"СТАТУС СИСТЕМЫ ЦИФРОВОГО АВАТАРА - {report['timestamp']}")
        print("="*60)
        
        # Системная информация
        if report['system']:
            sys = report['system']
            print(f"\n💻 СИСТЕМА:")
            print(f"   CPU: {sys.get('cpu_percent', 0):.1f}%")
            print(f"   RAM: {sys.get('memory', {}).get('percent', 0):.1f}% использовано")
            print(f"   Диск: {sys.get('disk', {}).get('percent', 0):.1f}% использовано")
        
        # Сервисы
        print(f"\n🌐 СЕРВИСЫ:")
        services = report['services']
        
        backend_status = "✅" if services['backend']['port_8000'] else "❌"
        print(f"   Backend (8000): {backend_status}")
        
        frontend_status = "✅" if services['frontend']['port_3000'] else "❌"
        print(f"   Frontend (3000): {frontend_status}")
        
        hier_status = "✅" if services['hier_tts']['port_8001'] else "❌"
        print(f"   HierSpeech_TTS (8001): {hier_status}")
        
        # Процессы
        print(f"\n⚙️  ПРОЦЕССЫ:")
        processes = report['processes']
        
        for name, proc in processes.items():
            if proc:
                status = "✅"
                info = f"PID: {proc['pid']}, CPU: {proc['cpu_percent']:.1f}%"
            else:
                status = "❌"
                info = "не запущен"
            print(f"   {name.capitalize()}: {status} {info}")
        
        # Обучение
        print(f"\n🎓 ОБУЧЕНИЕ YOURTTS:")
        training = report['training']
        if training['status'] == 'running':
            print("   ✅ Обучение активно")
            if 'process' in training:
                proc = training['process']
                print(f"   CPU: {proc['cpu_percent']:.1f}%, RAM: {proc['memory_percent']:.1f}%")
        elif training['status'] == 'not_running':
            print("   ❌ Обучение не запущено")
        else:
            print(f"   ⚠️  Статус: {training['status']}")
        
        # GPU
        print(f"\n🎮 GPU:")
        gpu = report['gpu']
        if gpu.get('available'):
            print("   ✅ GPU доступен")
            for device in gpu.get('devices', []):
                print(f"   {device['name']}: {device['memory_allocated']:.1f}GB / {device['memory_total']:.1f}GB")
        else:
            print("   ❌ GPU недоступен")
        
        print("\n" + "="*60)


async def main():
    """Основная функция мониторинга."""
    monitor = SystemMonitor()
    
    print("🚀 Запуск мониторинга системы цифрового аватара...")
    print("Нажмите Ctrl+C для остановки\n")
    
    try:
        while True:
            report = monitor.generate_report()
            monitor.print_status(report)
            
            # Сохраняем отчет в файл
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"system_status_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"📊 Отчет сохранен: {report_file}")
            
            # Ждем 30 секунд перед следующей проверкой
            await asyncio.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Мониторинг остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка мониторинга: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 