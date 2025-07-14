"""
Роутер для интеграции с HierSpeech_TTS
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
from typing import Optional
import logging
from ..services.hier_tts_service import get_hier_tts_service, HierTTSService
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hier-tts", tags=["HierSpeech_TTS"])

class TTSRequest(BaseModel):
    text: str
    language: str = "ru"
    reference_audio_path: Optional[str] = None

class TTSResponse(BaseModel):
    audio_path: str
    duration: float
    sample_rate: int
    success: bool
    message: str

@router.get("/health")
async def health_check(
    hier_service: HierTTSService = Depends(get_hier_tts_service)
):
    """Проверка состояния HierSpeech_TTS API"""
    try:
        health_status = await hier_service.check_health()
        return health_status
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(
    request: TTSRequest,
    hier_service: HierTTSService = Depends(get_hier_tts_service)
):
    """
    Синтез речи через HierSpeech_TTS
    
    Args:
        request: Запрос с текстом и параметрами
        hier_service: Сервис HierSpeech_TTS
        
    Returns:
        Информация о сгенерированном аудио
    """
    try:
        logger.info(f"Синтез речи: '{request.text}' на языке {request.language}")
        
        # Синтезируем речь
        audio_path = await hier_service.synthesize_speech(
            text=request.text,
            language=request.language,
            reference_audio_path=request.reference_audio_path
        )
        
        if audio_path:
            # Получаем информацию о файле
            import wave
            try:
                with wave.open(audio_path, 'r') as wav_file:
                    duration = wav_file.getnframes() / wav_file.getframerate()
                    sample_rate = wav_file.getframerate()
            except Exception as e:
                logger.warning(f"Не удалось получить информацию о файле: {e}")
                duration = 0.0
                sample_rate = 22050
            
            return TTSResponse(
                audio_path=audio_path,
                duration=duration,
                sample_rate=sample_rate,
                success=True,
                message="Синтез речи выполнен успешно"
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail="Не удалось синтезировать речь"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка синтеза речи: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-reference")
async def upload_reference_audio(
    file: UploadFile = File(...),
    hier_service: HierTTSService = Depends(get_hier_tts_service)
):
    """
    Загрузка референсного аудиофайла
    
    Args:
        file: Аудиофайл для загрузки
        hier_service: Сервис HierSpeech_TTS
        
    Returns:
        Путь к сохранённому файлу
    """
    try:
        # Сохраняем файл временно
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Загружаем на API сервер
        server_path = await hier_service.upload_reference_audio(temp_path)
        
        # Удаляем временный файл
        os.unlink(temp_path)
        
        if server_path:
            return {"file_path": server_path, "success": True}
        else:
            raise HTTPException(
                status_code=500, 
                detail="Не удалось загрузить файл на сервер"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки файла: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """
    Получение аудиофайла по имени
    
    Args:
        filename: Имя аудиофайла
        
    Returns:
        Аудиофайл
    """
    try:
        import os
        from pathlib import Path
        
        # Ищем файл в локальной директории
        local_path = Path("temp_audio") / filename
        
        if local_path.exists():
            return FileResponse(
                path=str(local_path),
                media_type="audio/wav",
                filename=filename
            )
        else:
            raise HTTPException(status_code=404, detail="Audio file not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения файла: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 