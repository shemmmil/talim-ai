import os
import tempfile
from pathlib import Path
from typing import BinaryIO, Optional
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)


def validate_audio_file(
    file: UploadFile,
    max_size_mb: int = 25,
    allowed_formats: Optional[list[str]] = None
) -> tuple[bool, Optional[str]]:
    """
    Валидация аудио файла
    
    Returns:
        (is_valid, error_message)
    """
    if allowed_formats is None:
        allowed_formats = [".webm", ".mp3", ".wav", ".m4a", ".ogg"]
    
    # Проверка расширения
    file_ext = Path(file.filename or "").suffix.lower()
    if file_ext not in allowed_formats:
        return False, f"Неподдерживаемый формат файла. Разрешенные форматы: {', '.join(allowed_formats)}"
    
    # Проверка размера (примерная, т.к. нужно прочитать файл)
    # В production лучше проверять Content-Length заголовок
    return True, None


async def save_temp_audio_file(file: UploadFile) -> str:
    """
    Сохраняет временный аудио файл
    
    Returns:
        Путь к временному файлу
    """
    suffix = Path(file.filename or "audio").suffix or ".webm"
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_path = tmp_file.name
        
        # Читаем и записываем содержимое
        content = await file.read()
        tmp_file.write(content)
        
        logger.info(f"Saved temporary audio file: {tmp_path} (size: {len(content)} bytes)")
        return tmp_path


def cleanup_temp_file(file_path: str):
    """Удаляет временный файл"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up temp file {file_path}: {e}")
