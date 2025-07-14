"""
API endpoints для TTS (Text-to-Speech).

Поддерживает ElevenLabs API для русской речи с клонированием голоса.

Автор: AI Assistant
Версия: 1.0.0
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any
import logging
import os
from pathlib import Path

from ..services.elevenlabs_tts import elevenlabs_tts_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tts", tags=["TTS"])

@router.get("/status")
async def get_tts_status() -> Dict[str, Any]:
    """Получение статуса TTS сервиса."""
    return {
        "service": "ElevenLabs TTS",
        "available": elevenlabs_tts_service.is_available(),
        "supports_russian": True,
        "voice_cloning": True
    }

@router.get("/voices")
async def get_available_voices() -> Dict[str, Any]:
    """Получение списка доступных голосов."""
    if not elevenlabs_tts_service.is_available():
        raise HTTPException(
            status_code=503, 
            detail="ElevenLabs API ключ не установлен. Установите переменную окружения ELEVENLABS_API_KEY"
        )
    
    result = await elevenlabs_tts_service.get_available_voices()
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.post("/clone-voice")
async def clone_voice(
    voice_name: str = Form(...),
    audio_file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Клонирование голоса из аудиофайла.
    
    Args:
        voice_name: Название для нового голоса
        audio_file: Аудиофайл для клонирования
    """
    if not elevenlabs_tts_service.is_available():
        raise HTTPException(
            status_code=503, 
            detail="ElevenLabs API ключ не установлен"
        )
    
    # Сохраняем загруженный файл
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"voice_clone_{voice_name}_{audio_file.filename}"
    
    try:
        with open(file_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        
        # Клонируем голос
        result = await elevenlabs_tts_service.clone_voice(voice_name, str(file_path))
        
        # Удаляем временный файл
        os.remove(file_path)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        # Удаляем временный файл в случае ошибки
        if file_path.exists():
            os.remove(file_path)
        logger.error(f"Ошибка клонирования голоса: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    voice_id: str = Form(...),
    output_filename: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Синтез речи с клонированным голосом.
    
    Args:
        text: Текст для синтеза (поддерживает русский)
        voice_id: ID клонированного голоса
        output_filename: Имя выходного файла (опционально)
    """
    if not elevenlabs_tts_service.is_available():
        raise HTTPException(
            status_code=503, 
            detail="ElevenLabs API ключ не установлен"
        )
    
    # Создаем имя файла
    if not output_filename:
        output_filename = f"synthesized_speech_{voice_id[:8]}.wav"
    
    # Путь для сохранения
    output_dir = Path("data/synthesized")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    
    # Синтезируем речь
    result = await elevenlabs_tts_service.synthesize_speech(
        text, voice_id, str(output_path)
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return {
        "success": True,
        "output_path": str(output_path),
        "text": text,
        "voice_id": voice_id
    }

@router.get("/download/{filename}")
async def download_synthesized_speech(filename: str):
    """Скачивание синтезированного аудиофайла."""
    file_path = Path("data/synthesized") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="audio/wav"
    )

@router.delete("/voices/{voice_id}")
async def delete_voice(voice_id: str) -> Dict[str, Any]:
    """Удаление клонированного голоса."""
    if not elevenlabs_tts_service.is_available():
        raise HTTPException(
            status_code=503, 
            detail="ElevenLabs API ключ не установлен"
        )
    
    result = await elevenlabs_tts_service.delete_voice(voice_id)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.post("/test-russian")
async def test_russian_synthesis() -> Dict[str, Any]:
    """Тест синтеза русской речи."""
    if not elevenlabs_tts_service.is_available():
        raise HTTPException(
            status_code=503, 
            detail="ElevenLabs API ключ не установлен"
        )
    
    # Получаем доступные голоса
    voices_result = await elevenlabs_tts_service.get_available_voices()
    
    if "error" in voices_result:
        raise HTTPException(status_code=500, detail=voices_result["error"])
    
    voices = voices_result.get("voices", [])
    if not voices:
        raise HTTPException(status_code=404, detail="Нет доступных голосов")
    
    # Используем первый доступный голос
    test_voice_id = voices[0]["voice_id"]
    test_text = "Привет! Это тест синтеза русской речи с ElevenLabs API."
    
    # Синтезируем тестовую речь
    output_dir = Path("data/synthesized")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "test_russian_speech.wav"
    
    result = await elevenlabs_tts_service.synthesize_speech(
        test_text, test_voice_id, str(output_path)
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return {
        "success": True,
        "test_text": test_text,
        "voice_used": voices[0]["name"],
        "output_path": str(output_path),
        "message": "Тест русской речи успешно выполнен"
    } 