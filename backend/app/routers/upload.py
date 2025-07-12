import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import aiofiles
from PIL import Image
import io
import uuid
from datetime import datetime

from ..config import settings

router = APIRouter(prefix="/upload", tags=["upload"])

# Создаем папки если их нет
UPLOAD_DIR = Path("app/static/uploads")
PROCESSED_DIR = Path("app/static/processed")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

for subdir in ["photos", "audio", "videos", "models"]:
    (UPLOAD_DIR / subdir).mkdir(exist_ok=True)

for subdir in ["avatars", "audio_clips", "animations"]:
    (PROCESSED_DIR / subdir).mkdir(exist_ok=True)

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png", 
    "image/webp": ".webp"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 5

async def validate_image_file(file: UploadFile) -> str:
    """Валидация изображения"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла. Поддерживаются: {', '.join(ALLOWED_IMAGE_TYPES.keys())}"
        )
    
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимум: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    return ALLOWED_IMAGE_TYPES[file.content_type]

async def process_image(image_data: bytes, extension: str) -> dict:
    """Обработка изображения для создания аватара"""
    try:
        # Открываем изображение
        image = Image.open(io.BytesIO(image_data))
        
        # Получаем информацию об изображении
        width, height = image.size
        format_name = image.format
        mode = image.mode
        
        # Проверяем минимальное разрешение
        if width < 512 or height < 512:
            raise HTTPException(
                status_code=400,
                detail="Изображение слишком маленькое. Минимум: 512x512 пикселей"
            )
        
        # Конвертируем в RGB если нужно
        if mode != 'RGB':
            image = image.convert('RGB')
        
        # Оптимизируем размер для SadTalker (рекомендуется 512x512)
        target_size = (512, 512)
        if width != 512 or height != 512:
            image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        return {
            "width": width,
            "height": height,
            "format": format_name,
            "mode": mode,
            "optimized_size": target_size
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка обработки изображения: {str(e)}"
        )

@router.post("/photos")
async def upload_photos(
    files: List[UploadFile] = File(...),
    description: Optional[str] = Form(None)
):
    """
    Загрузка фотографий для создания аватара
    """
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Слишком много файлов. Максимум: {MAX_FILES}"
        )
    
    uploaded_files = []
    session_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, file in enumerate(files):
        try:
            # Валидация файла
            extension = await validate_image_file(file)
            
            # Читаем содержимое файла
            content = await file.read()
            
            # Обрабатываем изображение
            image_info = await process_image(content, extension)
            
            # Генерируем уникальное имя файла
            filename = f"avatar_{session_id}_{timestamp}_{i+1}{extension}"
            file_path = UPLOAD_DIR / "photos" / filename
            
            # Сохраняем файл
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Создаем оптимизированную версию для SadTalker
            optimized_filename = f"optimized_{filename}"
            optimized_path = PROCESSED_DIR / "avatars" / optimized_filename
            
            # Обрабатываем и сохраняем оптимизированную версию
            image = Image.open(io.BytesIO(content))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image = image.resize((512, 512), Image.Resampling.LANCZOS)
            
            async with aiofiles.open(optimized_path, 'wb') as f:
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=95)
                await f.write(buffer.getvalue())
            
            uploaded_files.append({
                "original_name": file.filename,
                "saved_name": filename,
                "optimized_name": optimized_filename,
                "size": len(content),
                "image_info": image_info,
                "upload_path": str(file_path),
                "optimized_path": str(optimized_path)
            })
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка загрузки файла {file.filename}: {str(e)}"
            )
    
    return JSONResponse({
        "message": f"Успешно загружено {len(uploaded_files)} файлов",
        "session_id": session_id,
        "files": uploaded_files,
        "description": description,
        "total_files": len(uploaded_files)
    })

@router.get("/photos/{session_id}")
async def get_uploaded_photos(session_id: str):
    """
    Получение информации о загруженных фотографиях
    """
    photos_dir = UPLOAD_DIR / "photos"
    avatars_dir = PROCESSED_DIR / "avatars"
    
    # Ищем файлы с данным session_id
    original_files = list(photos_dir.glob(f"avatar_{session_id}_*"))
    optimized_files = list(avatars_dir.glob(f"optimized_avatar_{session_id}_*"))
    
    if not original_files:
        raise HTTPException(
            status_code=404,
            detail="Фотографии с данным session_id не найдены"
        )
    
    files_info = []
    for orig_file in original_files:
        # Ищем соответствующую оптимизированную версию
        optimized_file = next(
            (f for f in optimized_files if f.name.replace("optimized_", "") == orig_file.name),
            None
        )
        
        try:
            # Получаем информацию о файле
            stat = orig_file.stat()
            image = Image.open(orig_file)
            
            files_info.append({
                "original_name": orig_file.name,
                "optimized_name": optimized_file.name if optimized_file else None,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "dimensions": image.size,
                "format": image.format,
                "mode": image.mode
            })
        except Exception as e:
            # Пропускаем файлы с ошибками
            continue
    
    return JSONResponse({
        "session_id": session_id,
        "files": files_info,
        "total_files": len(files_info)
    })

@router.delete("/photos/{session_id}")
async def delete_uploaded_photos(session_id: str):
    """
    Удаление загруженных фотографий
    """
    photos_dir = UPLOAD_DIR / "photos"
    avatars_dir = PROCESSED_DIR / "avatars"
    
    # Ищем файлы с данным session_id
    original_files = list(photos_dir.glob(f"avatar_{session_id}_*"))
    optimized_files = list(avatars_dir.glob(f"optimized_avatar_{session_id}_*"))
    
    deleted_count = 0
    
    # Удаляем оригинальные файлы
    for file in original_files:
        try:
            file.unlink()
            deleted_count += 1
        except Exception as e:
            continue
    
    # Удаляем оптимизированные файлы
    for file in optimized_files:
        try:
            file.unlink()
        except Exception as e:
            continue
    
    if deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Фотографии с данным session_id не найдены"
        )
    
    return JSONResponse({
        "message": f"Удалено {deleted_count} файлов",
        "session_id": session_id,
        "deleted_count": deleted_count
    })

@router.get("/status")
async def get_upload_status():
    """
    Получение статуса системы загрузки
    """
    try:
        # Проверяем доступность папок
        photos_count = len(list((UPLOAD_DIR / "photos").glob("*")))
        avatars_count = len(list((PROCESSED_DIR / "avatars").glob("*")))
        
        # Проверяем свободное место
        total, used, free = shutil.disk_usage(UPLOAD_DIR)
        
        return JSONResponse({
            "status": "ok",
            "upload_dir": str(UPLOAD_DIR),
            "processed_dir": str(PROCESSED_DIR),
            "photos_count": photos_count,
            "avatars_count": avatars_count,
            "disk_space": {
                "total_gb": total // (1024**3),
                "used_gb": used // (1024**3),
                "free_gb": free // (1024**3),
                "free_percent": round((free / total) * 100, 2)
            },
            "limits": {
                "max_file_size_mb": MAX_FILE_SIZE // (1024*1024),
                "max_files": MAX_FILES,
                "allowed_formats": list(ALLOWED_IMAGE_TYPES.keys())
            }
        })
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения статуса: {str(e)}"
        ) 