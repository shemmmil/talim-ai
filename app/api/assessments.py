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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


@router.get(
    "/directions",
    summary="Получить список направлений",
    description="Возвращает список всех доступных направлений разработки"
)
async def get_directions(
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """Получить список всех направлений"""
    try:
        directions = await supabase_service.get_all_directions()
        return {"directions": directions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching directions: {str(e)}")


@router.get(
    "/directions/{direction_id}/technologies",
    summary="Получить технологии направления",
    description="Возвращает список технологий для указанного направления"
)
async def get_direction_technologies(
    direction_id: UUID = ..., description="ID направления",
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """Получить технологии для направления"""
    try:
        direction = await supabase_service.get_direction(str(direction_id))
        if not direction:
            raise HTTPException(status_code=404, detail="Direction not found")
        
        technologies = await supabase_service.get_direction_technologies(str(direction_id))
        
        # Форматируем ответ
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
            "technologies": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching direction technologies: {str(e)}")


@router.get(
    "/directions/{direction_id}/competencies",
    summary="Получить компетенции направления",
    description="Возвращает список общих компетенций для указанного направления"
)
async def get_direction_competencies(
    direction_id: UUID = ..., description="ID направления",
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """Получить компетенции для направления"""
    try:
        direction = await supabase_service.get_direction(str(direction_id))
        if not direction:
            raise HTTPException(status_code=404, detail="Direction not found")
        
        competencies = await supabase_service.get_direction_competencies(str(direction_id))
        
        # Форматируем ответ
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
            "competencies": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching direction competencies: {str(e)}")


@router.get(
    "/technologies/{technology_id}/competencies",
    summary="Получить компетенции технологии",
    description="Возвращает список компетенций для указанной технологии"
)
async def get_technology_competencies(
    technology_id: UUID = ..., description="ID технологии",
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """Получить компетенции для технологии"""
    try:
        technology = await supabase_service.get_technology(str(technology_id))
        if not technology:
            raise HTTPException(status_code=404, detail="Technology not found")
        
        competencies = await supabase_service.get_technology_competencies(str(technology_id))
        
        # Форматируем ответ
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
            "competencies": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching technology competencies: {str(e)}")


def get_assessment_service(
    supabase_service: SupabaseService = Depends(get_supabase_service),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> AssessmentService:
    return AssessmentService(supabase_service, openai_service)


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
    assessment_service: AssessmentService = Depends(get_assessment_service),
    user_id: str = Depends(get_current_user_id),
    direction_id: Optional[UUID] = Query(None, description="Фильтр по направлению"),
    technology_id: Optional[UUID] = Query(None, description="Фильтр по технологии")
):
    """
    Получить список всех тестирований пользователя.
    
    Возвращает все попытки прохождения тестирования для пользователя,
    отсортированные по номеру попытки (от новых к старым) и дате начала.
    
    Можно отфильтровать по направлению и/или технологии.
    """
    try:
        assessments = await assessment_service.get_user_assessments(
            user_id,
            str(direction_id) if direction_id else None,
            str(technology_id) if technology_id else None
        )
        
        result = []
        for assessment in assessments:
            role = assessment.get('roles') or {}
            result.append(
                AssessmentResponse(
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
                    competency_assessments=[]  # Не загружаем детали для списка
                )
            )
        
        return result
    except Exception as e:
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
    user_id: str = Depends(get_current_user_id)
):
    """
    Завершить тестирование.
    
    Выполняет:
    1. Вычисление общего балла на основе оценок по компетенциям (с учетом весов)
    2. Обновление статуса на 'completed'
    3. Установку даты завершения
    """
    """Завершить тестирование"""
    try:
        # Проверяем что assessment принадлежит пользователю
        assessment = await assessment_service.get_assessment_with_progress(str(assessment_id))
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        if assessment.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        result = await assessment_service.complete_assessment(str(assessment_id))
        return {"message": "Assessment completed", "assessment": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing assessment: {str(e)}")


