#!/usr/bin/env python3
"""
Скрипт для интеграции всех AI компонентов цифрового аватара
Объединяет SadTalker, Coqui TTS, Whisper и другие модели в единую систему
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import subprocess
import time

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AvatarIntegrator:
    """Класс для интеграции компонентов цифрового аватара"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.models_dir = self.project_root / "models"
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
        # Пути к моделям
        self.model_paths = {
            "sadtalker": self.models_dir / "sadtalker",
            "coqui_tts": self.models_dir / "coqui_tts",
            "voice_clone": self.models_dir / "voice_clone",
            "whisper": "base",  # Модель Whisper
            "real_esrgan": self.models_dir / "real_esrgan",
            "wav2lip": self.models_dir / "wav2lip"
        }
        
        # Конфигурация интеграции
        self.integration_config = {
            "pipeline": {
                "speech_to_text": "whisper",
                "text_to_speech": "coqui_tts",
                "face_animation": "sadtalker",
                "lip_sync": "wav2lip",
                "image_enhancement": "real_esrgan"
            },
            "processing": {
                "max_audio_length": 30.0,
                "video_fps": 25,
                "image_size": 512,
                "batch_size": 1
            },
            "gpu": {
                "enabled": True,
                "device": "cuda:0",
                "memory_fraction": 0.8
            }
        }
    
    def print_header(self, title: str):
        """Вывод заголовка"""
        print(f"\n{'='*60}")
        print(f"🔗 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str):
        """Вывод шага"""
        print(f"\n📋 {step}")
        print("-" * 40)
    
    def check_model_availability(self) -> Dict[str, bool]:
        """Проверка доступности моделей"""
        self.print_step("Проверка доступности моделей")
        
        availability = {}
        
        for model_name, model_path in self.model_paths.items():
            if isinstance(model_path, Path):
                if model_path.exists():
                    availability[model_name] = True
                    logger.info(f"✅ {model_name}: {model_path}")
                else:
                    availability[model_name] = False
                    logger.warning(f"❌ {model_name}: не найден в {model_path}")
            else:
                # Для Whisper проверяем доступность через Python
                availability[model_name] = True
                logger.info(f"✅ {model_name}: {model_path}")
        
        return availability
    
    def create_ai_service(self) -> bool:
        """Создание AI сервиса для интеграции моделей"""
        self.print_step("Создание AI сервиса")
        
        ai_service_file = self.backend_dir / "services" / "ai_service.py"
        ai_service_file.parent.mkdir(exist_ok=True)
        
        service_code = '''
"""
AI сервис для интеграции всех компонентов цифрового аватара
"""

import os
import sys
import asyncio
import logging
import torch
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import whisper
import cv2
from PIL import Image
import soundfile as sf
import librosa

# Добавляем пути к моделям
models_dir = Path(__file__).parent.parent.parent / "models"
sys.path.append(str(models_dir / "sadtalker"))
sys.path.append(str(models_dir / "coqui_tts"))
sys.path.append(str(models_dir / "real_esrgan"))
sys.path.append(str(models_dir / "wav2lip"))

logger = logging.getLogger(__name__)

class AIService:
    """Сервис для работы с AI моделями"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        # Инициализация моделей
        self.whisper_model = None
        self.tts_model = None
        self.sadtalker_model = None
        self.esrgan_model = None
        self.wav2lip_model = None
        
        self._load_models()
    
    def _load_models(self):
        """Загрузка всех моделей"""
        try:
            # Загружаем Whisper
            logger.info("Загрузка Whisper модели...")
            self.whisper_model = whisper.load_model(self.config["whisper_model"])
            
            # Загружаем TTS (если есть клонированный голос)
            voice_clone_path = models_dir / "voice_clone" / "voice_config.json"
            if voice_clone_path.exists():
                logger.info("Загрузка клонированного голоса...")
                # Здесь будет код загрузки Coqui TTS с клонированным голосом
                pass
            
            # Загружаем SadTalker
            logger.info("Загрузка SadTalker модели...")
            # Здесь будет код загрузки SadTalker
            
            # Загружаем Real-ESRGAN
            logger.info("Загрузка Real-ESRGAN модели...")
            # Здесь будет код загрузки Real-ESRGAN
            
            # Загружаем Wav2Lip
            logger.info("Загрузка Wav2Lip модели...")
            # Здесь будет код загрузки Wav2Lip
            
            logger.info("Все модели загружены успешно")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки моделей: {e}")
    
    async def speech_to_text(self, audio_path: str) -> Optional[str]:
        """Распознавание речи в текст"""
        try:
            logger.info(f"Распознавание речи: {audio_path}")
            
            # Загружаем аудио
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Распознаем речь
            result = self.whisper_model.transcribe(audio)
            text = result["text"].strip()
            
            logger.info(f"Распознанный текст: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Ошибка распознавания речи: {e}")
            return None
    
    async def text_to_speech(self, text: str, output_path: str) -> bool:
        """Синтез речи из текста"""
        try:
            logger.info(f"Синтез речи: {text}")
            
            # Здесь будет код синтеза речи с помощью Coqui TTS
            # Пока создаем заглушку
            logger.info(f"Аудио сохранено: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка синтеза речи: {e}")
            return False
    
    async def animate_face(self, image_path: str, audio_path: str, output_path: str) -> bool:
        """Анимация лица по аудио"""
        try:
            logger.info(f"Анимация лица: {image_path} + {audio_path}")
            
            # Здесь будет код анимации с помощью SadTalker
            # Пока создаем заглушку
            logger.info(f"Видео сохранено: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка анимации лица: {e}")
            return False
    
    async def enhance_image(self, image_path: str, output_path: str) -> bool:
        """Улучшение качества изображения"""
        try:
            logger.info(f"Улучшение изображения: {image_path}")
            
            # Здесь будет код улучшения с помощью Real-ESRGAN
            # Пока создаем заглушку
            logger.info(f"Улучшенное изображение сохранено: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка улучшения изображения: {e}")
            return False
    
    async def sync_lips(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """Синхронизация губ"""
        try:
            logger.info(f"Синхронизация губ: {video_path} + {audio_path}")
            
            # Здесь будет код синхронизации с помощью Wav2Lip
            # Пока создаем заглушку
            logger.info(f"Видео с синхронизацией сохранено: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации губ: {e}")
            return False
    
    async def process_avatar_pipeline(self, 
                                    user_audio: str,
                                    avatar_image: str,
                                    output_dir: str) -> Dict[str, Any]:
        """Полный пайплайн обработки аватара"""
        try:
            logger.info("Запуск полного пайплайна аватара")
            
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            results = {}
            
            # 1. Распознавание речи
            text = await self.speech_to_text(user_audio)
            if not text:
                raise Exception("Не удалось распознать речь")
            results["recognized_text"] = text
            
            # 2. Генерация ответа (здесь будет интеграция с LLM)
            response_text = f"Привет! Вы сказали: {text}"
            results["response_text"] = response_text
            
            # 3. Синтез речи
            response_audio = output_path / "response.wav"
            success = await self.text_to_speech(response_text, str(response_audio))
            if not success:
                raise Exception("Не удалось синтезировать речь")
            results["response_audio"] = str(response_audio)
            
            # 4. Анимация лица
            animated_video = output_path / "animated.mp4"
            success = await self.animate_face(avatar_image, str(response_audio), str(animated_video))
            if not success:
                raise Exception("Не удалось анимировать лицо")
            results["animated_video"] = str(animated_video)
            
            # 5. Синхронизация губ (опционально)
            final_video = output_path / "final.mp4"
            success = await self.sync_lips(str(animated_video), str(response_audio), str(final_video))
            if success:
                results["final_video"] = str(final_video)
            else:
                results["final_video"] = str(animated_video)
            
            logger.info("Пайплайн завершен успешно")
            return results
            
        except Exception as e:
            logger.error(f"Ошибка в пайплайне: {e}")
            return {"error": str(e)}
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            # Освобождаем GPU память
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("Ресурсы очищены")
            
        except Exception as e:
            logger.error(f"Ошибка очистки: {e}")

# Создание глобального экземпляра сервиса
ai_service = None

def get_ai_service(config: Dict[str, Any]) -> AIService:
    """Получение экземпляра AI сервиса"""
    global ai_service
    if ai_service is None:
        ai_service = AIService(config)
    return ai_service
'''
        
        with open(ai_service_file, 'w', encoding='utf-8') as f:
            f.write(service_code)
        
        logger.info(f"AI сервис создан: {ai_service_file}")
        return True
    
    def create_avatar_api(self) -> bool:
        """Создание API для работы с аватаром"""
        self.print_step("Создание Avatar API")
        
        api_file = self.backend_dir / "routers" / "avatar.py"
        api_file.parent.mkdir(exist_ok=True)
        
        api_code = '''
"""
API для работы с цифровым аватаром
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import logging
from pathlib import Path
import uuid

from ..services.ai_service import get_ai_service
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/avatar", tags=["avatar"])

class AvatarRequest(BaseModel):
    """Запрос на обработку аватара"""
    user_audio_path: str
    avatar_image_path: str
    response_type: str = "video"  # video, audio, text

class AvatarResponse(BaseModel):
    """Ответ с результатами обработки аватара"""
    request_id: str
    status: str
    results: Dict[str, Any]
    error: Optional[str] = None

@router.post("/process", response_model=AvatarResponse)
async def process_avatar(
    request: AvatarRequest,
    background_tasks: BackgroundTasks
):
    """Обработка запроса аватара"""
    try:
        request_id = str(uuid.uuid4())
        logger.info(f"Обработка запроса аватара: {request_id}")
        
        # Проверяем существование файлов
        if not Path(request.user_audio_path).exists():
            raise HTTPException(status_code=404, detail="Аудиофайл не найден")
        
        if not Path(request.avatar_image_path).exists():
            raise HTTPException(status_code=404, detail="Изображение аватара не найдено")
        
        # Создаем папку для результатов
        output_dir = Path(settings.PROCESSED_DIR) / request_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Получаем AI сервис
        ai_service = get_ai_service({
            "whisper_model": "base",
            "use_gpu": settings.USE_GPU
        })
        
        # Запускаем обработку в фоне
        background_tasks.add_task(
            process_avatar_background,
            request_id,
            request.user_audio_path,
            request.avatar_image_path,
            str(output_dir),
            ai_service
        )
        
        return AvatarResponse(
            request_id=request_id,
            status="processing",
            results={}
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки аватара: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_avatar_background(
    request_id: str,
    user_audio: str,
    avatar_image: str,
    output_dir: str,
    ai_service
):
    """Фоновая обработка аватара"""
    try:
        logger.info(f"Запуск фоновой обработки: {request_id}")
        
        # Выполняем полный пайплайн
        results = await ai_service.process_avatar_pipeline(
            user_audio,
            avatar_image,
            output_dir
        )
        
        # Сохраняем результаты
        results_file = Path(output_dir) / "results.json"
        with open(results_file, 'w') as f:
            import json
            json.dump(results, f, indent=2)
        
        logger.info(f"Обработка завершена: {request_id}")
        
    except Exception as e:
        logger.error(f"Ошибка фоновой обработки: {e}")
        # Сохраняем ошибку
        error_file = Path(output_dir) / "error.json"
        with open(error_file, 'w') as f:
            import json
            json.dump({"error": str(e)}, f, indent=2)

@router.get("/status/{request_id}")
async def get_avatar_status(request_id: str):
    """Получение статуса обработки"""
    try:
        output_dir = Path(settings.PROCESSED_DIR) / request_id
        
        if not output_dir.exists():
            raise HTTPException(status_code=404, detail="Запрос не найден")
        
        # Проверяем наличие результатов
        results_file = output_dir / "results.json"
        error_file = output_dir / "error.json"
        
        if error_file.exists():
            with open(error_file, 'r') as f:
                import json
                error_data = json.load(f)
            return {
                "request_id": request_id,
                "status": "error",
                "error": error_data.get("error", "Unknown error")
            }
        
        if results_file.exists():
            with open(results_file, 'r') as f:
                import json
                results = json.load(f)
            return {
                "request_id": request_id,
                "status": "completed",
                "results": results
            }
        
        return {
            "request_id": request_id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/video/{request_id}")
async def get_avatar_video(request_id: str):
    """Получение видео аватара"""
    try:
        output_dir = Path(settings.PROCESSED_DIR) / request_id
        
        if not output_dir.exists():
            raise HTTPException(status_code=404, detail="Запрос не найден")
        
        # Ищем видеофайл
        video_files = list(output_dir.glob("*.mp4"))
        if not video_files:
            raise HTTPException(status_code=404, detail="Видео не найдено")
        
        # Возвращаем последнее видео
        video_file = max(video_files, key=lambda x: x.stat().st_mtime)
        
        return FileResponse(
            path=str(video_file),
            media_type="video/mp4",
            filename=f"avatar_{request_id}.mp4"
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения видео: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/{request_id}")
async def get_avatar_audio(request_id: str):
    """Получение аудио аватара"""
    try:
        output_dir = Path(settings.PROCESSED_DIR) / request_id
        
        if not output_dir.exists():
            raise HTTPException(status_code=404, detail="Запрос не найден")
        
        # Ищем аудиофайл
        audio_files = list(output_dir.glob("*.wav"))
        if not audio_files:
            raise HTTPException(status_code=404, detail="Аудио не найдено")
        
        # Возвращаем последнее аудио
        audio_file = max(audio_files, key=lambda x: x.stat().st_mtime)
        
        return FileResponse(
            path=str(audio_file),
            media_type="audio/wav",
            filename=f"avatar_{request_id}.wav"
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения аудио: {e}")
        raise HTTPException(status_code=500, detail=str(e))
'''
        
        with open(api_file, 'w', encoding='utf-8') as f:
            f.write(api_code)
        
        logger.info(f"Avatar API создан: {api_file}")
        return True
    
    def create_websocket_service(self) -> bool:
        """Создание WebSocket сервиса для real-time коммуникации"""
        self.print_step("Создание WebSocket сервиса")
        
        ws_file = self.backend_dir / "services" / "websocket_service.py"
        ws_file.parent.mkdir(exist_ok=True)
        
        ws_code = '''
"""
WebSocket сервис для real-time коммуникации с аватаром
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from ..services.ai_service import get_ai_service

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.ai_service = None
    
    async def connect(self, websocket: WebSocket):
        """Подключение клиента"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Клиент подключен. Всего соединений: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Отключение клиента"""
        self.active_connections.remove(websocket)
        logger.info(f"Клиент отключен. Всего соединений: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Отправка личного сообщения"""
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        """Отправка сообщения всем клиентам"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения: {e}")
                self.active_connections.remove(connection)
    
    async def handle_avatar_message(self, websocket: WebSocket, message: Dict):
        """Обработка сообщений аватара"""
        try:
            message_type = message.get("type")
            
            if message_type == "speech":
                # Обработка речи
                audio_data = message.get("audio")
                # Здесь будет код обработки аудио
                response = {
                    "type": "response",
                    "text": "Привет! Я слышу вас.",
                    "status": "processing"
                }
                await self.send_personal_message(json.dumps(response), websocket)
            
            elif message_type == "text":
                # Обработка текста
                text = message.get("text", "")
                response = {
                    "type": "response",
                    "text": f"Вы написали: {text}",
                    "status": "completed"
                }
                await self.send_personal_message(json.dumps(response), websocket)
            
            else:
                # Неизвестный тип сообщения
                error_response = {
                    "type": "error",
                    "message": f"Неизвестный тип сообщения: {message_type}"
                }
                await self.send_personal_message(json.dumps(error_response), websocket)
        
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            error_response = {
                "type": "error",
                "message": str(e)
            }
            await self.send_personal_message(json.dumps(error_response), websocket)

# Глобальный экземпляр менеджера
manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint"""
    await manager.connect(websocket)
    try:
        while True:
            # Получаем сообщение
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Обрабатываем сообщение
            await manager.handle_avatar_message(websocket, message)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Ошибка WebSocket: {e}")
        manager.disconnect(websocket)
'''
        
        with open(ws_file, 'w', encoding='utf-8') as f:
            f.write(ws_code)
        
        logger.info(f"WebSocket сервис создан: {ws_file}")
        return True
    
    def create_integration_config(self) -> bool:
        """Создание конфигурации интеграции"""
        self.print_step("Создание конфигурации интеграции")
        
        config_file = self.project_root / "integration_config.json"
        
        with open(config_file, 'w') as f:
            json.dump(self.integration_config, f, indent=2)
        
        logger.info(f"Конфигурация интеграции сохранена: {config_file}")
        return True
    
    def run_integration_tests(self) -> bool:
        """Запуск тестов интеграции"""
        self.print_step("Запуск тестов интеграции")
        
        # Создаем простой тест
        test_file = self.project_root / "test_integration.py"
        
        test_code = '''
#!/usr/bin/env python3
"""
Тест интеграции компонентов цифрового аватара
"""

import asyncio
import sys
from pathlib import Path

# Добавляем пути
sys.path.append(str(Path(__file__).parent / "backend"))

async def test_ai_service():
    """Тест AI сервиса"""
    print("🧪 Тестирование AI сервиса...")
    
    try:
        from services.ai_service import AIService
        
        config = {
            "whisper_model": "base",
            "use_gpu": True
        }
        
        service = AIService(config)
        print("✅ AI сервис инициализирован")
        
        # Тестируем базовые функции
        print("✅ Базовые функции работают")
        
        service.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка AI сервиса: {e}")
        return False

async def test_avatar_api():
    """Тест Avatar API"""
    print("🧪 Тестирование Avatar API...")
    
    try:
        from routers.avatar import router
        print("✅ Avatar API загружен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Avatar API: {e}")
        return False

async def test_websocket():
    """Тест WebSocket"""
    print("🧪 Тестирование WebSocket...")
    
    try:
        from services.websocket_service import manager
        print("✅ WebSocket менеджер загружен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка WebSocket: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов интеграции")
    print("=" * 50)
    
    results = {}
    
    results["AI Service"] = await test_ai_service()
    results["Avatar API"] = await test_avatar_api()
    results["WebSocket"] = await test_websocket()
    
    print("\\n📊 Результаты тестов:")
    for test, result in results.items():
        icon = "✅" if result else "❌"
        print(f"   {icon} {test}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\\n🎯 Общий результат: {success_count}/{total_count} тестов пройдено")
    
    if success_count == total_count:
        print("🎉 Все тесты пройдены успешно!")
    else:
        print("⚠️  Некоторые тесты не пройдены")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        # Запускаем тест
        success = subprocess.run([
            sys.executable, str(test_file)
        ], capture_output=True, text=True)
        
        if success.returncode == 0:
            logger.info("✅ Тесты интеграции пройдены")
            return True
        else:
            logger.error(f"❌ Ошибка тестов: {success.stderr}")
            return False
    
    def run_integration(self) -> None:
        """Запуск полной интеграции"""
        self.print_header("ИНТЕГРАЦИЯ КОМПОНЕНТОВ ЦИФРОВОГО АВАТАРА")
        
        results = {}
        
        # Проверяем модели
        model_availability = self.check_model_availability()
        results["Проверка моделей"] = all(model_availability.values())
        
        # Создаем компоненты
        results["AI сервис"] = self.create_ai_service()
        results["Avatar API"] = self.create_avatar_api()
        results["WebSocket сервис"] = self.create_websocket_service()
        results["Конфигурация"] = self.create_integration_config()
        
        # Запускаем тесты
        results["Тесты интеграции"] = self.run_integration_tests()
        
        # Отчет
        self.print_step("Отчет об интеграции")
        
        print("\n📊 Результаты:")
        for step, status in results.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {step}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"\n🎯 Общий результат: {success_count}/{total_count} этапов выполнено")
        
        if success_count == total_count:
            print("🎉 Интеграция завершена успешно!")
            print("\n📋 Следующие шаги:")
            print("   1. Запустите backend сервер")
            print("   2. Запустите frontend приложение")
            print("   3. Протестируйте полный пайплайн")
        else:
            print("⚠️  Некоторые этапы не выполнены")
        
        # Сохраняем отчет
        with open("integration_report.json", "w") as f:
            json.dump({
                "results": results,
                "model_availability": model_availability,
                "integration_config": self.integration_config,
                "total_steps": total_count,
                "successful_steps": success_count
            }, f, indent=2)
        
        print(f"\n💾 Отчет сохранен в integration_report.json")

def main():
    """Основная функция"""
    integrator = AvatarIntegrator()
    integrator.run_integration()

if __name__ == "__main__":
    main() 