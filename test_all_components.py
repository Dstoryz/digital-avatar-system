#!/usr/bin/env python3
"""
Комплексное тестирование всех компонентов системы цифрового аватара.

Проверяет работу backend, frontend, TTS, распознавания речи и ИИ-чата.

Автор: Авабот
Версия: 1.0.0
"""

import asyncio
import json
import logging
import requests
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemTester:
    """Тестер системы цифрового аватара."""
    
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:3000"
        self.hier_tts_url = "http://127.0.0.1:8001"
        self.test_results = {}
    
    def test_backend_health(self) -> Dict[str, Any]:
        """Тестирование здоровья backend."""
        try:
            logger.info("🔍 Тестирование backend...")
            
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Backend работает")
                return {
                    "status": "success",
                    "data": data,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                logger.error(f"❌ Backend вернул статус {response.status_code}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к backend: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_frontend_health(self) -> Dict[str, Any]:
        """Тестирование здоровья frontend."""
        try:
            logger.info("🔍 Тестирование frontend...")
            
            response = requests.get(self.frontend_url, timeout=5)
            
            if response.status_code == 200:
                logger.info("✅ Frontend работает")
                return {
                    "status": "success",
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                logger.error(f"❌ Frontend вернул статус {response.status_code}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к frontend: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_hier_tts(self) -> Dict[str, Any]:
        """Тестирование HierSpeech_TTS."""
        try:
            logger.info("🔍 Тестирование HierSpeech_TTS...")
            
            response = requests.get(f"{self.hier_tts_url}/health", timeout=5)
            
            if response.status_code == 200:
                logger.info("✅ HierSpeech_TTS работает")
                return {
                    "status": "success",
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                logger.error(f"❌ HierSpeech_TTS вернул статус {response.status_code}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к HierSpeech_TTS: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_whisper_service(self) -> Dict[str, Any]:
        """Тестирование сервиса Whisper."""
        try:
            logger.info("🔍 Тестирование Whisper...")
            
            # Проверяем доступность endpoint
            response = requests.get(f"{self.backend_url}/api/v1/speech/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Whisper API работает")
                return {
                    "status": "success",
                    "data": data
                }
            else:
                logger.error(f"❌ Whisper API вернул статус {response.status_code}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования Whisper: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def test_ollama_service(self) -> Dict[str, Any]:
        """Тестирование сервиса Ollama."""
        try:
            logger.info("🔍 Тестирование Ollama...")
            
            # Проверяем доступность endpoint
            response = requests.get(f"{self.backend_url}/api/v1/chat/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Ollama API работает")
                return {
                    "status": "success",
                    "data": data
                }
            else:
                logger.error(f"❌ Ollama API вернул статус {response.status_code}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования Ollama: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_ports(self) -> Dict[str, Any]:
        """Тестирование занятости портов."""
        try:
            logger.info("🔍 Проверка портов...")
            
            import psutil
            
            ports_to_check = [8000, 3000, 8001]
            port_status = {}
            
            for port in ports_to_check:
                is_used = False
                for conn in psutil.net_connections():
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        is_used = True
                        break
                
                port_status[f"port_{port}"] = "used" if is_used else "free"
            
            logger.info("✅ Проверка портов завершена")
            return {
                "status": "success",
                "ports": port_status
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки портов: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_gpu(self) -> Dict[str, Any]:
        """Тестирование GPU."""
        try:
            logger.info("🔍 Проверка GPU...")
            
            import torch
            
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_info = []
                
                for i in range(gpu_count):
                    props = torch.cuda.get_device_properties(i)
                    gpu_info.append({
                        "id": i,
                        "name": props.name,
                        "memory_total": props.total_memory / 1024**3,  # GB
                        "memory_allocated": torch.cuda.memory_allocated(i) / 1024**3,  # GB
                    })
                
                logger.info(f"✅ GPU доступен: {gpu_count} устройств")
                return {
                    "status": "success",
                    "cuda_available": True,
                    "gpu_count": gpu_count,
                    "gpus": gpu_info
                }
            else:
                logger.warning("⚠️ GPU недоступен")
                return {
                    "status": "warning",
                    "cuda_available": False,
                    "message": "GPU недоступен, будет использоваться CPU"
                }
                
        except ImportError:
            logger.warning("⚠️ PyTorch не установлен")
            return {
                "status": "warning",
                "error": "PyTorch не установлен"
            }
        except Exception as e:
            logger.error(f"❌ Ошибка проверки GPU: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов."""
        logger.info("🚀 Запуск комплексного тестирования системы...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Тестируем компоненты
        results["tests"]["backend"] = self.test_backend_health()
        results["tests"]["frontend"] = self.test_frontend_health()
        results["tests"]["hier_tts"] = self.test_hier_tts()
        results["tests"]["whisper"] = self.test_whisper_service()
        results["tests"]["ollama"] = await self.test_ollama_service()
        results["tests"]["ports"] = self.test_ports()
        results["tests"]["gpu"] = self.test_gpu()
        
        # Подсчитываем статистику
        total_tests = len(results["tests"])
        successful_tests = sum(1 for test in results["tests"].values() if test["status"] == "success")
        warning_tests = sum(1 for test in results["tests"].values() if test["status"] == "warning")
        failed_tests = sum(1 for test in results["tests"].values() if test["status"] == "error")
        
        results["summary"] = {
            "total": total_tests,
            "successful": successful_tests,
            "warnings": warning_tests,
            "failed": failed_tests,
            "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        }
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Вывод результатов тестирования."""
        print("\n" + "="*60)
        print("📊 РЕЗУЛЬТАТЫ КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ")
        print("="*60)
        print(f"Время тестирования: {results['timestamp']}")
        
        # Выводим результаты по компонентам
        for component, result in results["tests"].items():
            status_icon = "✅" if result["status"] == "success" else "⚠️" if result["status"] == "warning" else "❌"
            print(f"\n{status_icon} {component.upper()}: {result['status']}")
            
            if result["status"] == "error":
                print(f"   Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            elif result["status"] == "success":
                if "response_time" in result:
                    print(f"   Время ответа: {result['response_time']:.3f} сек")
        
        # Выводим сводку
        summary = results["summary"]
        print(f"\n📈 СВОДКА:")
        print(f"   Всего тестов: {summary['total']}")
        print(f"   Успешно: {summary['successful']} ✅")
        print(f"   Предупреждения: {summary['warnings']} ⚠️")
        print(f"   Ошибки: {summary['failed']} ❌")
        print(f"   Процент успеха: {summary['success_rate']:.1f}%")
        
        # Общая оценка
        if summary["success_rate"] >= 80:
            print(f"\n🎉 ОТЛИЧНО! Система работает стабильно")
        elif summary["success_rate"] >= 60:
            print(f"\n🔶 ХОРОШО! Есть небольшие проблемы")
        else:
            print(f"\n🔴 ТРЕБУЕТ ВНИМАНИЯ! Много проблем")
        
        print("="*60)


async def main():
    """Основная функция."""
    tester = SystemTester()
    
    try:
        results = await tester.run_all_tests()
        tester.print_results(results)
        
        # Сохраняем результаты
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Результаты сохранены в: {results_file}")
        
        # Возвращаем код выхода
        if results["summary"]["success_rate"] >= 80:
            sys.exit(0)  # Успех
        elif results["summary"]["success_rate"] >= 60:
            sys.exit(1)  # Предупреждение
        else:
            sys.exit(2)  # Ошибка
            
    except Exception as e:
        logger.error(f"Ошибка тестирования: {e}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main()) 