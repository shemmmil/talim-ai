from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.api.deps import get_supabase_service, get_openai_service, get_current_user_id
from app.services.supabase_service import SupabaseService
from app.services.openai_service import OpenAIService
from app.services.roadmap_service import RoadmapService
from app.services.assessment_service import AssessmentService
from app.schemas.roadmap import (
    RoadmapResponse,
    RoadmapDetailResponse,
    RoadmapSectionResponse,
    LearningMaterialResponse,
    PracticeTaskResponse,
    SelfCheckQuestionResponse
)
from uuid import UUID as UUIDType

router = APIRouter(prefix="/api/roadmaps", tags=["roadmaps"])


def get_roadmap_service(
    supabase_service: SupabaseService = Depends(get_supabase_service),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> RoadmapService:
    return RoadmapService(supabase_service, openai_service)


def get_assessment_service(
    supabase_service: SupabaseService = Depends(get_supabase_service),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> AssessmentService:
    return AssessmentService(supabase_service, openai_service)


@router.get(
    "/{assessment_id}",
    response_model=RoadmapDetailResponse,
    summary="Получить roadmap по assessment",
    description="Возвращает персональный roadmap для завершенного тестирования. Если roadmap еще не создан, генерирует его автоматически через GPT-4"
)
async def get_roadmap_by_assessment(
    assessment_id: UUID = ..., description="ID завершенного тестирования",
    roadmap_service: RoadmapService = Depends(get_roadmap_service),
    assessment_service: AssessmentService = Depends(get_assessment_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Получить roadmap для завершенного тестирования.
    
    Если roadmap еще не существует, автоматически генерирует его через GPT-4 на основе результатов тестирования.
    
    Roadmap включает:
    - Секции по компетенциям (в порядке приоритета)
    - Материалы для изучения (статьи, видео, курсы, документация)
    - Практические задачи
    - Вопросы для самопроверки
    
    Требования:
    - Assessment должен быть в статусе 'completed'
    """
    try:
        # Проверяем доступ к assessment
        assessment = await assessment_service.get_assessment_with_progress(str(assessment_id))
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        if assessment.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Проверяем что assessment завершен
        if assessment.get('status') != 'completed':
            raise HTTPException(status_code=400, detail="Assessment must be completed to generate roadmap")

        # Получаем roadmap
        roadmap = await roadmap_service.supabase.get_roadmap_by_assessment(str(assessment_id))

        if not roadmap:
            # Генерируем roadmap если его еще нет
            roadmap = await roadmap_service.generate_roadmap(str(assessment_id))
        else:
            # Получаем полный roadmap со всеми секциями
            roadmap = await roadmap_service.supabase.get_roadmap_with_sections(roadmap['id'])

        # Формируем ответ
        sections = []
        for section in roadmap.get('sections', []):
            competency = section.get('competencies', {})
            sections.append(RoadmapSectionResponse(
                id=UUIDType(section['id']),
                competency_id=UUIDType(section['competency_id']) if section.get('competency_id') else None,
                competency_name=competency.get('name') if competency else None,
                title=section.get('title'),
                description=section.get('description'),
                order_index=section.get('order_index'),
                estimated_duration_hours=section.get('estimated_duration_hours'),
                status=section.get('status'),
                completed_at=section.get('completed_at'),
                learning_materials=[
                    LearningMaterialResponse(
                        id=UUIDType(m['id']),
                        type=m['type'],
                        title=m.get('title'),
                        description=m.get('description'),
                        url=m.get('url'),
                        author=m.get('author'),
                        duration_minutes=m.get('duration_minutes'),
                        difficulty=m.get('difficulty'),
                        language=m.get('language'),
                        is_free=m.get('is_free', True),
                        order_index=m.get('order_index'),
                        rating=m.get('rating')
                    )
                    for m in section.get('learning_materials', [])
                ],
                practice_tasks=[
                    PracticeTaskResponse(
                        id=UUIDType(t['id']),
                        title=t.get('title'),
                        description=t.get('description'),
                        task_type=t['task_type'],
                        difficulty=t.get('difficulty'),
                        estimated_time_minutes=t.get('estimated_time_minutes'),
                        requirements=t.get('requirements'),
                        hints=t.get('hints'),
                        order_index=t.get('order_index')
                    )
                    for t in section.get('practice_tasks', [])
                ],
                self_check_questions=[
                    SelfCheckQuestionResponse(
                        id=UUIDType(q['id']),
                        question_text=q.get('question_text'),
                        question_type=q.get('question_type'),
                        options=q.get('options'),
                        explanation=q.get('explanation'),
                        difficulty=q.get('difficulty'),
                        order_index=q.get('order_index')
                    )
                    for q in section.get('self_check_questions', [])
                ]
            ))

        return RoadmapDetailResponse(
            id=UUIDType(roadmap['id']),
            assessment_id=UUIDType(roadmap['assessment_id']),
            title=roadmap.get('title'),
            description=roadmap.get('description'),
            estimated_duration_weeks=roadmap.get('estimated_duration_weeks'),
            difficulty_level=roadmap.get('difficulty_level'),
            generated_at=roadmap['generated_at'],
            updated_at=roadmap['updated_at'],
            status=roadmap.get('status'),
            sections=sections
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching roadmap: {str(e)}")


@router.get(
    "/{roadmap_id}/sections",
    response_model=RoadmapDetailResponse,
    summary="Получить детальные секции roadmap",
    description="Возвращает полную информацию о roadmap со всеми секциями, материалами, задачами и вопросами"
)
async def get_roadmap_sections(
    roadmap_id: UUID = ..., description="ID roadmap",
    roadmap_service: RoadmapService = Depends(get_roadmap_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Получить детальные секции roadmap.
    
    Возвращает полную структуру roadmap:
    - Все секции с описаниями
    - Материалы для изучения в каждой секции
    - Практические задачи
    - Вопросы для самопроверки
    
    Секции упорядочены по приоритету и order_index.
    """
    try:
        roadmap = await roadmap_service.supabase.get_roadmap_with_sections(str(roadmap_id))

        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")

        # Проверяем доступ через assessment
        assessment = await roadmap_service.supabase.get_assessment(roadmap['assessment_id'])
        if not assessment or assessment.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Формируем ответ аналогично предыдущему endpoint
        sections = []
        for section in roadmap.get('sections', []):
            competency = section.get('competencies', {})
            sections.append(RoadmapSectionResponse(
                id=UUIDType(section['id']),
                competency_id=UUIDType(section['competency_id']) if section.get('competency_id') else None,
                competency_name=competency.get('name') if competency else None,
                title=section.get('title'),
                description=section.get('description'),
                order_index=section.get('order_index'),
                estimated_duration_hours=section.get('estimated_duration_hours'),
                status=section.get('status'),
                completed_at=section.get('completed_at'),
                learning_materials=[
                    LearningMaterialResponse(
                        id=UUIDType(m['id']),
                        type=m['type'],
                        title=m.get('title'),
                        description=m.get('description'),
                        url=m.get('url'),
                        author=m.get('author'),
                        duration_minutes=m.get('duration_minutes'),
                        difficulty=m.get('difficulty'),
                        language=m.get('language'),
                        is_free=m.get('is_free', True),
                        order_index=m.get('order_index'),
                        rating=m.get('rating')
                    )
                    for m in section.get('learning_materials', [])
                ],
                practice_tasks=[
                    PracticeTaskResponse(
                        id=UUIDType(t['id']),
                        title=t.get('title'),
                        description=t.get('description'),
                        task_type=t['task_type'],
                        difficulty=t.get('difficulty'),
                        estimated_time_minutes=t.get('estimated_time_minutes'),
                        requirements=t.get('requirements'),
                        hints=t.get('hints'),
                        order_index=t.get('order_index')
                    )
                    for t in section.get('practice_tasks', [])
                ],
                self_check_questions=[
                    SelfCheckQuestionResponse(
                        id=UUIDType(q['id']),
                        question_text=q.get('question_text'),
                        question_type=q.get('question_type'),
                        options=q.get('options'),
                        explanation=q.get('explanation'),
                        difficulty=q.get('difficulty'),
                        order_index=q.get('order_index')
                    )
                    for q in section.get('self_check_questions', [])
                ]
            ))

        return RoadmapDetailResponse(
            id=UUIDType(roadmap['id']),
            assessment_id=UUIDType(roadmap['assessment_id']),
            title=roadmap.get('title'),
            description=roadmap.get('description'),
            estimated_duration_weeks=roadmap.get('estimated_duration_weeks'),
            difficulty_level=roadmap.get('difficulty_level'),
            generated_at=roadmap['generated_at'],
            updated_at=roadmap['updated_at'],
            status=roadmap.get('status'),
            sections=sections
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching roadmap sections: {str(e)}")
