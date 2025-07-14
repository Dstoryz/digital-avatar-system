from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import torch
import logging
from typing import Any
import tempfile
import os

router = APIRouter()

try:
    import whisper
except ImportError:
    whisper = None

logger = logging.getLogger("whisper_api")

@router.post("/recognize-speech", summary="Распознавание речи (ASR)", tags=["AI"], response_description="Результат распознавания речи")
async def recognize_speech(
    audio: UploadFile = File(..., description="Аудиофайл для распознавания (WAV/OGG/MP3)")
) -> Any:
    """
    Распознаёт речь из аудиофайла с помощью Whisper.
    Возвращает JSON с текстом и confidence.
    """
    if whisper is None:
        logger.error("Whisper не установлен")
        raise HTTPException(status_code=500, detail="Whisper не установлен на сервере")
    if not torch.cuda.is_available():
        logger.warning("CUDA недоступен, используется CPU")
    try:
        # Сохраняем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[-1]) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name
        logger.info(f"Файл для распознавания: {tmp_path}")
        # Загружаем модель (кешируется)
        with torch.cuda.amp.autocast():
            model = whisper.load_model("base", device="cuda" if torch.cuda.is_available() else "cpu")
            result = model.transcribe(tmp_path, language="ru")
        logger.info(f"Распознанный текст: {result.get('text')}")
        return JSONResponse({
            "text": result.get("text", ""),
            "confidence": result.get("avg_logprob", None),
            "language": result.get("language", None)
        })
    except Exception as e:
        logger.error(f"Ошибка распознавания речи: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка распознавания речи: {e}")
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        torch.cuda.empty_cache()
        logger.info("GPU память очищена после ASR") 