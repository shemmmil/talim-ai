from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from uuid import UUID
from app.api.deps import get_supabase_service, get_openai_service, get_current_user_id
from app.services.supabase_service import SupabaseService
from app.services.openai_service import OpenAIService
from app.services.assessment_service import AssessmentService
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentStartResponse,
    AssessmentResponse,
    CompetencyInfo,
)

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


def get_assessment_service(
    supabase_service: SupabaseService = Depends(get_supabase_service),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> AssessmentService:
    return AssessmentService(supabase_service, openai_service)


@router.post(
    "",
    response_model=AssessmentStartResponse,
    summary="Начать новое тестирование",
    description="Создает новое тестирование для указанного направления и возвращает список компетенций для тестирования. "
                "По результатам тестирования будет сформирован персональный roadmap."
)
async def create_assessment(
    assessment_data: AssessmentCreate,
    assessment_service: AssessmentService = Depends(get_assessment_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Начать новое тестирование компетенций по направлению.
    
    Создает новую запись assessment со статусом 'in_progress' и возвращает:
    - ID созданного тестирования
    - Список компетенций для тестирования
    - Статус тестирования
    
    Для каждой компетенции создается competency_assessment запись.
    По результатам тестирования будет автоматически сформирован персональный roadmap.
    
    Args:
        assessment_data: Объект с полем direction (текст направления, например "backend(golang, sql)")
    """
    try:
        result = await assessment_service.start_assessment_by_direction(
            user_id,
            assessment_data.direction
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating assessment: {str(e)}")


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
            competency = ca.get('competencies', {})
            competency_assessments.append(
                CompetencyAssessmentResponse(
                    id=UUID(ca['id']),
                    competency_id=UUID(ca['competency_id']),
                    competency_name=competency.get('name'),
                    ai_assessed_score=ca.get('ai_assessed_score'),
                    confidence_level=ca.get('confidence_level'),
                    gap_analysis=ca.get('gap_analysis'),
                    completed_at=ca.get('completed_at')
                )
            )

        role = assessment.get('roles', {})
        return AssessmentResponse(
            id=assessment['id'],
            user_id=assessment['user_id'],
            role_id=assessment['role_id'],
            role_name=role.get('name'),
            status=assessment['status'],
            overall_score=assessment.get('overall_score'),
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
    
    После завершения можно сгенерировать roadmap через GET /api/roadmaps/{assessment_id}
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


