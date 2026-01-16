from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # OpenAI
    openai_api_key: str
    openai_timeout: int = 180  # Таймаут для OpenAI API запросов в секундах (по умолчанию 180)
    
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Audio settings
    max_audio_file_size_mb: int = 25
    allowed_audio_formats: list[str] = [".webm", ".mp3", ".wav", ".m4a", ".ogg"]
    
    @field_validator('supabase_url', 'supabase_key', 'openai_api_key')
    @classmethod
    def validate_required_settings(cls, v: str, info) -> str:
        if not v or not v.strip():
            field_name = info.field_name
            raise ValueError(
                f"{field_name} is required but not set. "
                f"Please check your .env file and ensure {field_name.upper()} is set."
            )
        return v.strip()
    
    @field_validator('supabase_url')
    @classmethod
    def validate_supabase_url(cls, v: str) -> str:
        if not v.startswith('https://'):
            raise ValueError(
                "SUPABASE_URL must start with 'https://'. "
                f"Current value: {v[:20]}..."
            )
        return v
    
    @field_validator('supabase_key')
    @classmethod
    def validate_supabase_key(cls, v: str) -> str:
        """Валидация формата Supabase API ключа"""
        v = v.strip()
        
        # Supabase поддерживает два формата ключей:
        # 1. Стандартный JWT формат: начинается с 'eyJ', длина 200+ символов
        # 2. Новый формат: может начинаться с 'sb_' или других префиксов
        
        # Если это JWT токен (стандартный формат)
        if v.startswith('eyJ'):
            if len(v) < 100:
                raise ValueError(
                    f"SUPABASE_KEY (JWT формат) слишком короткий ({len(v)} символов). "
                    "JWT токены обычно имеют длину 200+ символов. "
                    "Проверьте, что вы скопировали ключ полностью."
                )
            if v.count('.') < 2:
                raise ValueError(
                    "SUPABASE_KEY (JWT формат) имеет неправильную структуру. "
                    "JWT токены должны содержать 3 части, разделенные точками."
                )
        # Если это новый формат (sb_publishable_, sb_secret_ и т.д.)
        elif v.startswith('sb_'):
            if len(v) < 20:
                raise ValueError(
                    f"SUPABASE_KEY (новый формат) слишком короткий ({len(v)} символов). "
                    "Проверьте, что ключ скопирован полностью."
                )
            # Новый формат поддерживается в supabase-py >= 2.27.0
        else:
            # Неизвестный формат - предупреждаем, но не блокируем
            if len(v) < 20:
                raise ValueError(
                    f"SUPABASE_KEY имеет неожиданный формат и слишком короткий ({len(v)} символов). "
                    "Стандартные Supabase ключи начинаются с 'eyJ' (JWT) или 'sb_' (новый формат). "
                    "Убедитесь, что вы используете правильный ключ из Supabase Dashboard → Settings → API."
                )
        
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Игнорировать дополнительные поля (например, SUPABASE_DB)


settings = Settings()
