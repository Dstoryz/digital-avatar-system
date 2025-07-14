#!/usr/bin/env python3
"""
Скрипт для проверки статуса системы цифрового аватара.

Проверяет:
- Backend API
- Frontend
- TTS сервисы
- Доступность портов

Автор: AI Assistant
Версия: 1.0.0
"""

import requests
import subprocess
import json
import time
from datetime import datetime

def check_backend():
    """Проверка backend API."""
    print("🔍 Проверка Backend API...")
    
    try:
        # Проверка health endpoint
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend работает: {data['status']} (версия {data['version']})")
            return True
        else:
            print(f"❌ Backend недоступен: статус {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к backend: {e}")
        return False

def check_tts_service():
    """Проверка TTS сервиса."""
    print("\n🔍 Проверка TTS сервиса...")
    
    try:
        response = requests.get("http://127.0.0.1:8001/api/v1/tts/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ TTS сервис: {data['service']}")
            print(f"   - Доступен: {'✅' if data['available'] else '❌'}")
            print(f"   - Поддерживает русский: {'✅' if data['supports_russian'] else '❌'}")
            print(f"   - Клонирование голоса: {'✅' if data['voice_cloning'] else '❌'}")
            return data['available']
        else:
            print(f"❌ TTS сервис недоступен: статус {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к TTS: {e}")
        return False

def check_frontend():
    """Проверка frontend."""
    print("\n🔍 Проверка Frontend...")
    
    # Проверяем разные порты
    ports = [3000, 3001, 3002, 3003]
    
    for port in ports:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=3)
            if response.status_code == 200:
                print(f"✅ Frontend работает на порту {port}")
                return True
        except:
            continue
    
    print("❌ Frontend недоступен на всех портах")
    return False

def check_ports():
    """Проверка занятых портов."""
    print("\n🔍 Проверка портов...")
    
    try:
        result = subprocess.run(
            ["netstat", "-tlnp"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            
            # Ищем наши сервисы
            backend_found = False
            frontend_found = False
            
            for line in lines:
                if ':8001' in line and 'python' in line:
                    print("✅ Backend порт 8001 активен")
                    backend_found = True
                elif any(f':{port}' in line and 'node' in line for port in ['3000', '3001', '3002', '3003']):
                    if not frontend_found:
                        print("✅ Frontend порт активен")
                        frontend_found = True
            
            if not backend_found:
                print("❌ Backend порт 8001 не найден")
            if not frontend_found:
                print("❌ Frontend порты не найдены")
                
            return backend_found and frontend_found
        else:
            print("❌ Не удалось проверить порты")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки портов: {e}")
        return False

def main():
    """Основная функция проверки."""
    print("🚀 Проверка системы цифрового аватара")
    print("=" * 50)
    print(f"Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Проверки
    backend_ok = check_backend()
    tts_ok = check_tts_service()
    frontend_ok = check_frontend()
    ports_ok = check_ports()
    
    # Итоговый результат
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ СТАТУС:")
    print(f"Backend API: {'✅ Работает' if backend_ok else '❌ Не работает'}")
    print(f"TTS сервис: {'✅ Доступен' if tts_ok else '❌ Недоступен'}")
    print(f"Frontend: {'✅ Работает' if frontend_ok else '❌ Не работает'}")
    print(f"Порты: {'✅ Активны' if ports_ok else '❌ Проблемы'}")
    
    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")
    
    if not backend_ok:
        print("- Запустите backend: source ai_env/bin/activate && python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001")
    
    if not frontend_ok:
        print("- Запустите frontend: cd frontend && npm run dev")
    
    if not tts_ok:
        print("- Установите API ключ ElevenLabs для полной функциональности TTS")
    
    if backend_ok and frontend_ok:
        print("🎉 Система готова к работе!")
        print("📱 Откройте браузер: http://localhost:3003")
        print("📚 API документация: http://127.0.0.1:8001/docs")

if __name__ == "__main__":
    main() 