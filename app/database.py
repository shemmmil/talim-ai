from supabase import create_client, Client
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Singleton для Supabase клиента
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Получить экземпляр Supabase клиента (singleton)"""
    global _supabase_client
    if _supabase_client is None:
        # Validate settings before creating client
        if not settings.supabase_url or not settings.supabase_key:
            error_msg = (
                "Supabase credentials are missing. "
                "Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
            logger.info("Supabase client initialized")
        except Exception as e:
            error_msg = (
                f"Failed to create Supabase client: {e}. "
                "Please verify that SUPABASE_URL and SUPABASE_KEY in your .env file are correct. "
                f"URL: {settings.supabase_url[:30]}... (truncated), "
                f"Key length: {len(settings.supabase_key)} characters"
            )
            logger.error(error_msg)
            raise ValueError(error_msg) from e
    return _supabase_client


def init_db():
    """Инициализация базы данных (можно добавить проверку подключения)"""
    try:
        client = get_supabase_client()
        # Простая проверка подключения
        client.table("users").select("id").limit(1).execute()
        logger.info("Database connection verified")
    except ValueError as e:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        error_msg = (
            f"Database initialization error: {e}. "
            "Please check your Supabase credentials and ensure the database is accessible."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
