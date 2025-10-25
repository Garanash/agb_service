"""
API endpoints для управления аватарами пользователей
"""

import os
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from PIL import Image
import uuid

from database import get_db
from models import User
from api.v1.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Настройки для аватаров
AVATAR_UPLOAD_DIR = Path("uploads/avatars")
AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
AVATAR_SIZES = [(32, 32), (64, 64), (128, 128), (256, 256)]

@router.post("/upload")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Загрузка аватара пользователя"""
    
    try:
        # Проверяем тип файла
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Проверяем размер файла
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Генерируем уникальное имя файла
        file_id = str(uuid.uuid4())
        original_filename = f"{file_id}{file_extension}"
        
        # Сохраняем оригинальный файл
        original_path = AVATAR_UPLOAD_DIR / original_filename
        with open(original_path, "wb") as f:
            f.write(file_content)
        
        # Создаем миниатюры разных размеров
        avatar_urls = {}
        try:
            with Image.open(original_path) as img:
                # Конвертируем в RGB если нужно
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                for size in AVATAR_SIZES:
                    # Создаем миниатюру
                    thumbnail = img.copy()
                    thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
                    
                    # Сохраняем миниатюру
                    thumbnail_filename = f"{file_id}_{size[0]}x{size[1]}.jpg"
                    thumbnail_path = AVATAR_UPLOAD_DIR / thumbnail_filename
                    thumbnail.save(thumbnail_path, "JPEG", quality=85)
                    
                    avatar_urls[f"{size[0]}x{size[1]}"] = f"/uploads/avatars/{thumbnail_filename}"
        
        except Exception as e:
            logger.error(f"Ошибка создания миниатюр: {e}")
            # Удаляем оригинальный файл если не удалось создать миниатюры
            if original_path.exists():
                original_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка обработки изображения"
            )
        
        # Удаляем оригинальный файл (оставляем только миниатюры)
        if original_path.exists():
            original_path.unlink()
        
        # Обновляем аватар пользователя в базе данных
        avatar_url = avatar_urls.get("128x128", "")
        current_user.avatar_url = avatar_url
        db.commit()
        
        logger.info(f"✅ Аватар загружен для пользователя {current_user.username}: {avatar_url}")
        
        return {
            "message": "Аватар успешно загружен",
            "avatar_url": avatar_url,
            "avatar_urls": avatar_urls
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки аватара: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка загрузки аватара"
        )

@router.delete("/remove")
async def remove_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление аватара пользователя"""
    
    try:
        if not current_user.avatar_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="У пользователя нет аватара"
            )
        
        # Удаляем файлы аватара
        avatar_path = Path(current_user.avatar_url)
        if avatar_path.exists():
            avatar_path.unlink()
        
        # Удаляем все размеры аватара
        file_id = avatar_path.stem.split('_')[0]
        for size in AVATAR_SIZES:
            size_filename = f"{file_id}_{size[0]}x{size[1]}.jpg"
            size_path = AVATAR_UPLOAD_DIR / size_filename
            if size_path.exists():
                size_path.unlink()
        
        # Обновляем пользователя в базе данных
        current_user.avatar_url = None
        db.commit()
        
        logger.info(f"✅ Аватар удален для пользователя {current_user.username}")
        
        return {"message": "Аватар успешно удален"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка удаления аватара: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка удаления аватара"
        )

@router.get("/info")
async def get_avatar_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации об аватаре пользователя"""
    
    avatar_info = {
        "has_avatar": bool(current_user.avatar_url),
        "avatar_url": current_user.avatar_url,
        "avatar_urls": {}
    }
    
    if current_user.avatar_url:
        # Генерируем URL для всех размеров
        avatar_path = Path(current_user.avatar_url)
        file_id = avatar_path.stem.split('_')[0]
        
        for size in AVATAR_SIZES:
            size_filename = f"{file_id}_{size[0]}x{size[1]}.jpg"
            size_path = AVATAR_UPLOAD_DIR / size_filename
            if size_path.exists():
                avatar_info["avatar_urls"][f"{size[0]}x{size[1]}"] = f"/uploads/avatars/{size_filename}"
    
    return avatar_info
