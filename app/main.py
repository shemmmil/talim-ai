from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
import json
from app.config import settings
from app.database import init_db
from app.api import roles, assessments, questions, admin

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Talim AI - Backend для тестирования компетенций",
    description="""
    API для системы AI-тестирования профессиональных компетенций через голосовое собеседование.
    
    ## Основные возможности
    
    * **Тестирование компетенций**: Адаптивное голосовое тестирование с использованием GPT-4
    * **Транскрипция аудио**: Автоматическая транскрипция ответов через Whisper API
    * **Оценка ответов**: AI-оценка с выявлением пробелов в знаниях
    
    ## Документация
    
    * Swagger UI: `/docs`
    * ReDoc: `/redoc`
    * OpenAPI JSON: `/openapi.json`
    
    ## Аутентификация
    
    User ID передается с фронтенда в заголовке `Authorization`:
    - Формат: `Authorization: Bearer {user_id}` или `Authorization: {user_id}`
    - Заголовок обязателен для всех защищенных endpoints
    """,
    version="1.0.0",
    contact={
        "name": "Talim AI",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(roles.router)
app.include_router(assessments.router)
app.include_router(questions.router)
app.include_router(admin.router)


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения"""
    logger.info("Starting Talim AI Backend...")
    try:
        init_db()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Talim AI Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    """
    Получить OpenAPI схему в JSON формате.
    Используется фронтендом для генерации типов и API клиентов.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return openapi_schema


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )
