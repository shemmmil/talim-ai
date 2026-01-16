from fastapi import Depends, HTTPException, Header
from typing import Optional
from app.database import get_supabase_client
from app.config import settings
from app.services.supabase_service import SupabaseService
from app.services.openai_service import OpenAIService
from supabase import Client

# Global instances
_openai_service: Optional[OpenAIService] = None
_supabase_service: Optional[SupabaseService] = None


def get_supabase() -> Client:
    """Dependency для получения Supabase клиента"""
    return get_supabase_client()


def get_supabase_service(db: Client = Depends(get_supabase)) -> SupabaseService:
    """Dependency для получения SupabaseService"""
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService(db)
    return _supabase_service


def get_openai_service() -> OpenAIService:
    """Dependency для получения OpenAIService"""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout
        )
    return _openai_service


async def get_current_user_id(
    authorization: Optional[str] = Header(
        None, 
        alias="Authorization", 
        description="JWT токен передается с фронтенда в заголовке Authorization. Формат: 'Bearer {jwt_token}'. "
                    "User ID извлекается из поля 'sub' в JWT токене."
    )
) -> str:
    """
    Получить user_id из JWT токена в заголовке Authorization.
    
    Поддерживаемые форматы:
    - "Bearer {jwt_token}" (JWT токен от Keycloak или другого провайдера)
    - "{jwt_token}" (JWT токен без префикса Bearer)
    
    User ID извлекается из поля 'sub' в декодированном JWT токене.
    
    Args:
        authorization: Заголовок Authorization с JWT токеном
        
    Returns:
        user_id: UUID строка пользователя из поля 'sub' JWT токена
        
    Note:
        Пользователь будет автоматически создан в БД при первом обращении, если его нет.
        
    Raises:
        HTTPException 401: Если заголовок не передан
        HTTPException 400: Если токен невалидный или не содержит user_id
    """
    from fastapi import HTTPException
    from jose import jwt
    
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required. Please provide JWT token in Authorization header."
        )
    
    # Извлекаем токен из заголовка
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
    else:
        token = authorization.strip()
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="JWT token is required in Authorization header"
        )
    
    try:
        # Декодируем JWT токен без проверки подписи и других валидаций
        # В production рекомендуется проверять подпись токена
        # Передаем пустую строку как key, так как мы не проверяем подпись
        decoded_token = jwt.decode(
            token,
            key="",  # Пустой ключ, так как не проверяем подпись
            options={
                "verify_signature": False,  # Пропускаем проверку подписи
                "verify_aud": False,  # Пропускаем проверку аудитории
                "verify_exp": False,  # Пропускаем проверку срока действия
                "verify_iat": False,  # Пропускаем проверку времени выдачи
                "verify_nbf": False,  # Пропускаем проверку "not before"
                "verify_iss": False,  # Пропускаем проверку издателя
            }
        )
        
        # Извлекаем user_id из поля 'sub' (subject) JWT токена
        user_id = decoded_token.get('sub')
        
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="JWT token does not contain 'sub' field (user_id)"
            )
        
        return str(user_id)
        
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JWT token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error decoding JWT token: {str(e)}"
        )
