from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
import logging
from app.api.deps import get_supabase_service, get_openai_service, get_current_user_id
from app.services.supabase_service import SupabaseService
from app.services.openai_service import OpenAIService
from app.services.assessment_service import AssessmentService
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentStartResponse,
    AssessmentResponse,
    CompetencyInfo,
    CompetencyAssessmentResponse,
)
from app.schemas.question import QuestionGenerateResponse, AnswerResponse, AnswerEvaluation
from app.utils.audio import validate_audio_file, save_temp_audio_file, cleanup_temp_file
from app.config import settings
from fastapi import UploadFile, File, Form

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


def get_assessment_service(
    supabase_service: SupabaseService = Depends(get_supabase_service),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> AssessmentService:
    return AssessmentService(supabase_service, openai_service)


# ============================================================================
# LEGACY ENDPOINTS (Deprecated - use /api/catalog instead)
# ============================================================================

@router.get(
    "/directions",
    summary="Получить список направлений (deprecated)",
    description="⚠️ DEPRECATED: Используйте GET /api/catalog/directions вместо этого.",
    deprecated=True
)
async def get_directions_legacy(
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """
    Получить список всех направлений.
    
    ⚠️ DEPRECATED: Этот endpoint устарел. 
    Используйте GET /api/catalog/directions?include_technologies=true
    """
    try:
        directions = await supabase_service.get_all_directions()
        return {
            "directions": directions,
            "deprecated": True,
            "message": "This endpoint is deprecated. Use /api/catalog/directions instead."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching directions: {str(e)}")


@router.get(
    "/directions/{direction_id}/technologies",
    summary="Получить технологии направления (deprecated)",
    description="⚠️ DEPRECATED: Используйте GET /api/catalog/directions вместо этого.",
    deprecated=True
)
async def get_direction_technologies_legacy(
    direction_id: UUID,
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """
    Получить технологии для направления.
    
    ⚠️ DEPRECATED: Используйте GET /api/catalog/directions?include_technologies=true
    """
    try:
        direction = await supabase_service.get_direction(str(direction_id))
        if not direction:
            raise HTTPException(status_code=404, detail="Direction not found")
        
        technologies = await supabase_service.get_direction_technologies(str(direction_id))
        
        result = []
        for dt in technologies:
            technology = dt.get('technologies', {})
            if technology:
                result.append({
                    "id": technology['id'],
                    "name": technology.get('name'),
                    "description": technology.get('description'),
                    "order_index": dt.get('order_index')
                })
        
        return {
            "direction": direction,
            "technologies": result,
            "deprecated": True,
            "message": "This endpoint is deprecated. Use /api/catalog/directions instead."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching direction technologies: {str(e)}")


@router.get(
    "/directions/{direction_id}/competencies",
    summary="Получить компетенции направления (deprecated)",
    description="⚠️ DEPRECATED: Компетенции теперь привязаны к технологиям.",
    deprecated=True
)
async def get_direction_competencies_legacy(
    direction_id: UUID,
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """⚠️ DEPRECATED endpoint"""
    try:
        direction = await supabase_service.get_direction(str(direction_id))
        if not direction:
            raise HTTPException(status_code=404, detail="Direction not found")
        
        competencies = await supabase_service.get_direction_competencies(str(direction_id))
        
        result = []
        for dc in competencies:
            competency = dc.get('competencies', {})
            if competency:
                result.append({
                    "id": competency['id'],
                    "name": competency.get('name'),
                    "description": competency.get('description'),
                    "category": competency.get('category'),
                    "order_index": dc.get('order_index')
                })
        
        return {
            "direction": direction,
            "competencies": result,
            "deprecated": True,
            "message": "This endpoint is deprecated. Use /api/catalog/technologies/{id}/competencies instead."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching direction competencies: {str(e)}")


@router.get(
    "/technologies/{technology_id}/competencies",
    summary="Получить компетенции технологии (deprecated)",
    description="⚠️ DEPRECATED: Используйте /api/catalog/technologies/{id}/competencies",
    deprecated=True
)
async def get_technology_competencies_legacy(
    technology_id: UUID,
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """⚠️ DEPRECATED endpoint"""
    try:
        technology = await supabase_service.get_technology(str(technology_id))
        if not technology:
            raise HTTPException(status_code=404, detail="Technology not found")
        
        competencies = await supabase_service.get_technology_competencies(str(technology_id))
        
        result = []
        for tc in competencies:
            competency = tc.get('competencies', {})
            if competency:
                result.append({
                    "id": competency['id'],
                    "name": competency.get('name'),
                    "description": competency.get('description'),
                    "category": competency.get('category'),
                    "order_index": tc.get('order_index')
                })
        
        return {
            "technology": technology,
            "competencies": result,
            "deprecated": True,
            "message": "This endpoint is deprecated. Use /api/catalog/technologies/{id}/competencies instead."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching technology competencies: {str(e)}")


# ============================================================================
# ASSESSMENT MANAGEMENT
# ============================================================================

@router.post(
    "/{assessment_id}/restart",
    response_model=AssessmentStartResponse,
    summary="Перезапустить assessment",
    description="Создает новый assessment с теми же параметрами (direction + technology). Увеличивает attempt_number."
)
async def restart_assessment(
    assessment_id: UUID,
    assessment_service: AssessmentService = Depends(get_assessment_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Перезапустить assessment с теми же параметрами.
    
    Создает новый assessment с:
    - Теми же direction и technology
    - Теми же компетенциями
    - attempt_number = старый attempt_number + 1
    - Новым UUID
    - Статусом 'in_progress'
    
    Полезно для повторного прохождения тестирования.
    """
    try:
        # Получаем старый assessment
        old_assessment = await assessment_service.get_assessment_with_progress(str(assessment_id))
        if not old_assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        if old_assessment['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Извлекаем direction и technology
        direction = old_assessment.get('directions', {})
        technology = old_assessment.get('technologies', {})
        
        if not direction or not direction.get('name'):
            raise HTTPException(
                status_code=400, 
                detail="Cannot restart: assessment has no direction information"
            )
        
        # Создаем новый assessment с теми же параметрами
        result = await assessment_service.start_assessment_by_direction(
            user_id,
            direction.get('name'),
            technology.get('name') if technology else None
        )
        
        return AssessmentStartResponse(
            assessment_id=result['assessment_id'],
            competencies=[
                CompetencyInfo(
                    id=c['id'],
                    name=c['name'],
                    description=c.get('description'),
                    category=c.get('category'),
                    importance_weight=c.get('importance_weight'),
                    order_index=c.get('order_index')
                )
                for c in result['competencies']
            ],
            status=result['status']
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting assessment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error restarting assessment: {str(e)}")


@router.post(
    "",
    response_model=AssessmentStartResponse,
    summary="Начать новое тестирование",
    description="Создает новое тестирование для указанного направления и возвращает список компетенций для тестирования."
)
async def create_assessment(
    assessment_data: AssessmentCreate,
    assessment_service: AssessmentService = Depends(get_assessment_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Начать новое тестирование компетенций по направлению и технологии.
    
    Создает новую запись assessment со статусом 'in_progress' и возвращает:
    - ID созданного тестирования
    - Список компетенций для тестирования
    - Статус тестирования
    
    Для каждой компетенции создается competency_assessment запись.
    
    Args:
        assessment_data: Объект с полями:
            - direction: название направления (например, "backend", "frontend")
            - technology: опциональное название технологии (например, "go", "php", "python")
    
    Если указана technology, используются компетенции технологии.
    Если technology не указана, используются общие компетенции направления.
    """
    try:
        result = await assessment_service.start_assessment_by_direction(
            user_id,
            assessment_data.direction,
            assessment_data.technology
        )

        competencies = [
            CompetencyInfo(
                id=c['id'],
                name=c['name'],
                description=c.get('description'),
                category=c.get('category'),
                importance_weight=c.get('importance_weight'),
                order_index=c.get('order_index')
            )
            for c in result['competencies']
        ]

        return AssessmentStartResponse(
            assessment_id=result['assessment_id'],
            competencies=competencies,
            status=result['status']
        )
    except ValueError as e:
        # Ошибки валидации (нет компетенций и т.д.)
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating assessment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating assessment: {str(e)}")


@router.get(
    "",
    response_model=List[AssessmentResponse],
    summary="Получить список тестирований пользователя",
    description="Возвращает список всех тестирований пользователя, отсортированных по номеру попытки и дате"
)
async def get_user_assessments(
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id),
    status: Optional[str] = Query(None, description="Фильтр по статусу (in_progress, completed, abandoned)"),
    direction_id: Optional[UUID] = Query(None, description="Фильтр по направлению"),
    technology_id: Optional[UUID] = Query(None, description="Фильтр по технологии")
):
    """
    Получить список всех тестирований пользователя.
    
    Возвращает все попытки прохождения тестирования для пользователя,
    отсортированные по номеру попытки (от новых к старым) и дате начала.
    
    Можно отфильтровать по направлению, технологии и/или статусу.
    
    ⚡ ОПТИМИЗИРОВАНО: Не загружает связанные данные (roles, directions, technologies)
    для списка. Используйте GET /api/assessments/{id} для детальной информации.
    """
    try:
        # Простой запрос без joins
        query = supabase_service.client.table('assessments') \
            .select('id, user_id, role_id, direction_id, technology_id, status, overall_score, attempt_number, started_at, completed_at') \
            .eq('user_id', user_id)
        
        if status:
            query = query.eq('status', status)
        
        if direction_id:
            query = query.eq('direction_id', str(direction_id))
        
        if technology_id:
            query = query.eq('technology_id', str(technology_id))
        
        response = query \
            .order('attempt_number', desc=True) \
            .order('started_at', desc=True) \
            .execute()
        
        assessments = response.data if response.data else []
        
        # Простой маппинг без дополнительных запросов
        result = []
        for assessment in assessments:
            result.append(
                AssessmentResponse(
                    id=assessment['id'],
                    user_id=assessment['user_id'],
                    role_id=assessment.get('role_id'),
                    role_name=None,  # Не загружаем для списка
                    direction_id=assessment.get('direction_id'),
                    technology_id=assessment.get('technology_id'),
                    status=assessment['status'],
                    overall_score=assessment.get('overall_score'),
                    attempt_number=assessment.get('attempt_number', 1),
                    started_at=assessment['started_at'],
                    completed_at=assessment.get('completed_at'),
                    competency_assessments=[]  # Не загружаем детали для списка
                )
            )
        
        return result
    except Exception as e:
        logger.error(f"Error fetching assessments: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching assessments: {str(e)}")


@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
    summary="Получить информацию о тестировании",
    description="Возвращает детальную информацию о тестировании, включая статус, оценки по компетенциям и прогресс"
)
async def get_assessment(
    assessment_id: UUID = ..., description="ID тестирования",
    assessment_service: AssessmentService = Depends(get_assessment_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Получить информацию о тестировании.
    
    Возвращает:
    - Основную информацию о тестировании (статус, общий балл, даты)
    - Оценки по каждой компетенции
    - Детали оценки (балл, уровень уверенности, пробелы в знаниях)
    """
    """Получить информацию о тестировании"""
    try:
        assessment = await assessment_service.get_assessment_with_progress(str(assessment_id))
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        # Проверяем что assessment принадлежит пользователю
        if assessment.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Формируем ответ
        competency_assessments = []
        for ca in assessment.get('competency_assessments', []):
            # Handle None values from Supabase joins
            competency = ca.get('competencies') or {}
            competency_assessments.append(
                CompetencyAssessmentResponse(
                    id=UUID(ca['id']),
                    competency_id=UUID(ca['competency_id']),
                    competency_name=competency.get('name') if competency else None,
                    ai_assessed_score=ca.get('ai_assessed_score'),
                    confidence_level=ca.get('confidence_level'),
                    gap_analysis=ca.get('gap_analysis'),
                    completed_at=ca.get('completed_at')
                )
            )

        # Handle None values from Supabase joins
        role = assessment.get('roles') or {}
        return AssessmentResponse(
            id=assessment['id'],
            user_id=assessment['user_id'],
            role_id=assessment.get('role_id'),
            role_name=role.get('name'),
            direction_id=assessment.get('direction_id'),
            technology_id=assessment.get('technology_id'),
            status=assessment['status'],
            overall_score=assessment.get('overall_score'),
            attempt_number=assessment.get('attempt_number', 1),
            started_at=assessment['started_at'],
            completed_at=assessment.get('completed_at'),
            competency_assessments=competency_assessments
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching assessment: {str(e)}")


@router.post(
    "/{assessment_id}/complete",
    summary="Завершить тестирование",
    description="Завершает тестирование, вычисляет общий балл и устанавливает статус 'completed'"
)
async def complete_assessment(
    assessment_id: UUID = ..., description="ID тестирования",
    assessment_service: AssessmentService = Depends(get_assessment_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Завершить тестирование.
    
    Выполняет:
    1. Вычисление общего балла на основе оценок по компетенциям (с учетом весов)
    2. Обновление статуса на 'completed'
    3. Установку даты завершения
    
    Если assessment уже завершен, просто возвращает текущее состояние.
    """
    try:
        # Проверяем что assessment принадлежит пользователю
        assessment = await assessment_service.get_assessment_with_progress(str(assessment_id))
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        if assessment.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Если уже завершен, просто возвращаем
        if assessment.get('status') == 'completed':
            return {
                "message": "Assessment already completed",
                "assessment": assessment,
                "already_completed": True
            }

        result = await assessment_service.complete_assessment(str(assessment_id))
        return {
            "message": "Assessment completed",
            "assessment": result,
            "already_completed": False
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing assessment: {str(e)}")


@router.delete(
    "/{assessment_id}",
    summary="Отменить/удалить assessment",
    description="Устанавливает статус 'abandoned' для assessment. Данные остаются в БД для статистики."
)
async def abandon_assessment(
    assessment_id: UUID,
    assessment_service: AssessmentService = Depends(get_assessment_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Отменить/удалить assessment.
    
    Устанавливает статус 'abandoned' вместо физического удаления.
    Это позволяет сохранить данные для статистики и аналитики.
    
    Если нужно физически удалить данные (GDPR right to be forgotten),
    используйте admin API.
    """
    try:
        # Проверяем что assessment принадлежит пользователю
        assessment = await assessment_service.get_assessment_with_progress(str(assessment_id))
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        if assessment.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Нельзя отменить уже завершенный assessment
        if assessment.get('status') == 'completed':
            raise HTTPException(
                status_code=400, 
                detail="Cannot abandon a completed assessment. Use restart to create a new one."
            )
        
        # Устанавливаем статус 'abandoned'
        result = await supabase_service.update_assessment_status(
            str(assessment_id),
            'abandoned'
        )
        
        return {
            "message": "Assessment abandoned",
            "assessment": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error abandoning assessment: {str(e)}")


# ============================================================================
# TESTING ENDPOINTS (Questions & Answers)
# ============================================================================

@router.post(
    "/{assessment_id}/questions",
    response_model=QuestionGenerateResponse,
    summary="Получить следующий вопрос",
    description="Получает вопрос для тестирования компетенции из базы данных (RESTful endpoint)"
)
async def get_next_question(
    assessment_id: UUID,
    competency_id: UUID = Form(..., description="ID компетенции"),
    question_number: int = Form(..., description="Номер вопроса (1-5)", ge=1, le=5),
    difficulty: Optional[int] = Form(None, description="Уровень сложности (1-5)", ge=1, le=5),
    assessment_service: AssessmentService = Depends(get_assessment_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    openai_service: OpenAIService = Depends(get_openai_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Получить следующий вопрос для компетенции (новый RESTful endpoint).
    
    Это альтернативный путь для /api/questions/generate с более RESTful структурой:
    POST /api/assessments/{assessment_id}/questions
    
    Логика идентична существующему endpoint.
    """
    # Импортируем функцию из questions.py
    from app.api.questions import generate_question as old_generate_question
    
    # Переиспользуем существующую логику
    return await old_generate_question(
        assessment_id=assessment_id,
        competency_id=competency_id,
        question_number=question_number,
        difficulty=difficulty,
        assessment_service=assessment_service,
        supabase_service=supabase_service,
        user_id=user_id
    )


@router.post(
    "/{assessment_id}/answers",
    response_model=AnswerResponse,
    summary="Отправить ответ на вопрос",
    description="Отправляет голосовой ответ, транскрибирует и оценивает его (RESTful endpoint)"
)
async def submit_answer(
    assessment_id: UUID,
    competency_id: UUID = Form(..., description="ID компетенции"),
    question_text: str = Form(..., description="Текст вопроса"),
    difficulty: int = Form(3, description="Сложность вопроса (1-5)", ge=1, le=5),
    question_id: Optional[UUID] = Form(None, description="ID вопроса из БД"),
    audio: UploadFile = File(..., description="Аудио файл с ответом"),
    assessment_service: AssessmentService = Depends(get_assessment_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    openai_service: OpenAIService = Depends(get_openai_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Отправить ответ на вопрос (новый RESTful endpoint).
    
    Это альтернативный путь для /api/questions/answer с более RESTful структурой:
    POST /api/assessments/{assessment_id}/answers
    
    Процесс:
    1. Валидация аудио
    2. Транскрипция через Whisper
    3. Оценка через GPT-4
    4. Сохранение результата (только оценки, без транскрипта)
    5. Обновление competency_assessment
    6. Опционально: авто-завершение assessment
    """
    # Импортируем функцию из questions.py
    from app.api.questions import submit_answer as old_submit_answer
    
    # Переиспользуем существующую логику
    response = await old_submit_answer(
        assessment_id=assessment_id,
        competency_id=competency_id,
        question_text=question_text,
        difficulty=difficulty,
        question_id=question_id,
        audio=audio,
        assessment_service=assessment_service,
        supabase_service=supabase_service,
        openai_service=openai_service,
        user_id=user_id
    )
    
    # Проверяем, все ли компетенции протестированы (авто-complete)
    try:
        assessment = await assessment_service.get_assessment_with_progress(str(assessment_id))
        all_competencies = assessment.get('competency_assessments', [])
        
        if all_competencies:
            # Проверяем, что все компетенции имеют оценки
            all_completed = all(
                ca.get('ai_assessed_score') is not None 
                for ca in all_competencies
            )
            
            if all_completed and assessment.get('status') == 'in_progress':
                # Автоматически завершаем assessment
                completed_assessment = await assessment_service.complete_assessment(str(assessment_id))
                
                # Добавляем информацию об авто-завершении
                response_dict = response.dict() if hasattr(response, 'dict') else response
                response_dict['assessment_auto_completed'] = True
                response_dict['overall_score'] = completed_assessment.get('overall_score')
                
                logger.info(f"Assessment {assessment_id} auto-completed with score {completed_assessment.get('overall_score')}")
                
                return response_dict
    except Exception as e:
        # Не критично, если авто-complete не сработал
        logger.warning(f"Auto-complete check failed for assessment {assessment_id}: {e}")
    
    return response


