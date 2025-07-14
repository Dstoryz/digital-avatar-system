#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работоспособности системы цифрового аватара.

Проверяет:
- Backend API (FastAPI)
- Frontend (React/Vite)
- WebSocket соединения
- Загрузка файлов
- AI модели (базовая проверка)

Автор: Авабот
Версия: 1.0.0
"""

import asyncio
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any


class SystemTester:
    """Класс для тестирования системы цифрового аватара."""
    
    def __init__(self):
        """Инициализация тестера."""
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_urls = [
            "http://localhost:3000", 
            "http://localhost:3001", 
            "http://localhost:3002",
            "http://192.168.0.102:3000",
            "http://192.168.0.102:3001", 
            "http://192.168.0.102:3002"
        ]
        self.results = {}
        
    def test_backend_health(self) -> Dict[str, Any]:
        """Тест health endpoint backend."""
        print("🔍 Тестирование backend health endpoint...")
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend health: {data}")
                return {"status": "success", "data": data}
            else:
                print(f"❌ Backend health failed: {response.status_code}")
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            print(f"❌ Backend health error: {e}")
            return {"status": "error", "message": str(e)}
    
    def test_backend_docs(self) -> Dict[str, Any]:
        """Тест Swagger документации."""
        print("🔍 Тестирование Swagger документации...")
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            if response.status_code == 200 and "swagger-ui" in response.text:
                print("✅ Swagger документация доступна")
                return {"status": "success"}
            else:
                print(f"❌ Swagger документация недоступна: {response.status_code}")
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            print(f"❌ Swagger документация error: {e}")
            return {"status": "error", "message": str(e)}
    
    def test_backend_openapi(self) -> Dict[str, Any]:
        """Тест OpenAPI схемы."""
        print("🔍 Тестирование OpenAPI схемы...")
        try:
            response = requests.get(f"{self.backend_url}/openapi.json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                endpoints = list(data.get("paths", {}).keys())
                print(f"✅ OpenAPI схема доступна, endpoints: {len(endpoints)}")
                return {"status": "success", "endpoints": endpoints}
            else:
                print(f"❌ OpenAPI схема недоступна: {response.status_code}")
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            print(f"❌ OpenAPI схема error: {e}")
            return {"status": "error", "message": str(e)}
    
    def test_frontend(self) -> Dict[str, Any]:
        """Тест frontend."""
        print("🔍 Тестирование frontend...")
        for url in self.frontend_urls:
            try:
                response = requests.get(url, timeout=5)
                response.encoding = 'utf-8'
                if response.status_code == 200 and ("Цифровой" in response.text or "digital" in response.text.lower()):
                    print(f"✅ Frontend доступен: {url}")
                    return {"status": "success", "url": url}
            except Exception as e:
                print(f"❌ Frontend {url} недоступен: {e}")
                continue
        
        print("❌ Все frontend URL недоступны")
        return {"status": "error", "message": "Все frontend URL недоступны"}
    
    def test_upload_endpoint(self) -> Dict[str, Any]:
        """Тест endpoint загрузки файлов."""
        print("🔍 Тестирование upload endpoint...")
        try:
            response = requests.get(f"{self.backend_url}/api/v1/upload/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Upload endpoint доступен: {data.get('status')}")
                return {"status": "success", "data": data}
            else:
                print(f"❌ Upload endpoint недоступен: {response.status_code}")
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            print(f"❌ Upload endpoint error: {e}")
            return {"status": "error", "message": str(e)}
    
    def test_websocket_endpoint(self) -> Dict[str, Any]:
        """Тест WebSocket endpoint (базовая проверка)."""
        print("🔍 Тестирование WebSocket endpoint...")
        try:
            # Проверяем наличие WebSocket endpoint в коде
            import os
            main_py_path = "./backend/app/main.py"
            
            if os.path.exists(main_py_path):
                with open(main_py_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "@app.websocket" in content and "/ws/" in content:
                    print("✅ WebSocket endpoint найден в коде")
                    return {"status": "success", "message": "WebSocket endpoint реализован"}
                else:
                    print("❌ WebSocket endpoint не найден в коде")
                    return {"status": "error", "message": "WebSocket endpoint не реализован"}
            else:
                print("❌ Файл main.py не найден")
                return {"status": "error", "message": "Файл main.py не найден"}
                
        except Exception as e:
            print(f"❌ WebSocket endpoint error: {e}")
            return {"status": "error", "message": str(e)}
    
    def test_ai_models_availability(self) -> Dict[str, Any]:
        """Тест доступности AI моделей."""
        print("🔍 Тестирование доступности AI моделей...")
        try:
            # Проверяем наличие папок с моделями
            import os
            models_path = "./models"
            cache_path = "./cache"
            
            results = {}
            
            if os.path.exists(models_path):
                models_count = len([f for f in os.listdir(models_path) if os.path.isdir(os.path.join(models_path, f))])
                print(f"✅ Папка models существует, подпапок: {models_count}")
                results["models"] = {"status": "success", "count": models_count}
            else:
                print("❌ Папка models не существует")
                results["models"] = {"status": "error", "message": "Папка не существует"}
            
            if os.path.exists(cache_path):
                cache_size = len(os.listdir(cache_path))
                print(f"✅ Папка cache существует, файлов: {cache_size}")
                results["cache"] = {"status": "success", "size": cache_size}
            else:
                print("❌ Папка cache не существует")
                results["cache"] = {"status": "error", "message": "Папка не существует"}
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            print(f"❌ AI models availability error: {e}")
            return {"status": "error", "message": str(e)}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов."""
        print("🚀 Запуск тестирования системы цифрового аватара")
        print("=" * 60)
        
        start_time = time.time()
        
        # Запуск тестов
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "backend_health": self.test_backend_health(),
            "backend_docs": self.test_backend_docs(),
            "backend_openapi": self.test_backend_openapi(),
            "frontend": self.test_frontend(),
            "upload_endpoint": self.test_upload_endpoint(),
            "websocket_endpoint": self.test_websocket_endpoint(),
            "ai_models": self.test_ai_models_availability()
        }
        
        end_time = time.time()
        self.results["execution_time"] = end_time - start_time
        
        # Подсчет результатов
        success_count = sum(1 for result in self.results.values() 
                           if isinstance(result, dict) and result.get("status") == "success")
        total_count = len([k for k in self.results.keys() if k != "timestamp" and k != "execution_time"])
        
        self.results["summary"] = {
            "total_tests": total_count,
            "successful_tests": success_count,
            "failed_tests": total_count - success_count,
            "success_rate": (success_count / total_count * 100) if total_count > 0 else 0
        }
        
        return self.results
    
    def print_summary(self):
        """Вывод сводки результатов."""
        print("\n" + "=" * 60)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        summary = self.results.get("summary", {})
        print(f"Всего тестов: {summary.get('total_tests', 0)}")
        print(f"Успешных: {summary.get('successful_tests', 0)}")
        print(f"Неудачных: {summary.get('failed_tests', 0)}")
        print(f"Процент успеха: {summary.get('success_rate', 0):.1f}%")
        print(f"Время выполнения: {self.results.get('execution_time', 0):.2f} сек")
        
        print("\n🔍 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        for test_name, result in self.results.items():
            if test_name not in ["timestamp", "execution_time", "summary"]:
                status = "✅" if result.get("status") == "success" else "❌"
                print(f"{status} {test_name}: {result.get('status', 'unknown')}")
        
        # Сохранение результатов
        with open("system_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в system_test_results.json")


def main():
    """Основная функция."""
    tester = SystemTester()
    results = tester.run_all_tests()
    tester.print_summary()
    
    # Возвращаем код выхода
    summary = results.get("summary", {})
    if summary.get("success_rate", 0) >= 80:
        print("\n🎉 Система готова к работе!")
        return 0
    else:
        print("\n⚠️  Система требует доработки!")
        return 1


if __name__ == "__main__":
    exit(main()) 