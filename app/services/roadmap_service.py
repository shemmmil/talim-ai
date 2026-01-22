from typing import Dict, List, Optional
import logging
from app.services.supabase_service import SupabaseService
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class RoadmapService:
    def __init__(self, supabase_service: SupabaseService, openai_service: OpenAIService):
        self.supabase = supabase_service
        self.openai = openai_service

    async def generate_roadmap(self, assessment_id: str) -> Dict:
        """Сгенерировать roadmap на основе результатов assessment"""
        # Получаем assessment с результатами
        assessment = await self.supabase.get_assessment(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # Получаем название направления (из directions или roles)
        direction = assessment.get('directions', {})
        role = assessment.get('roles', {})
        
        if direction:
            role_name = direction.get('display_name') or direction.get('name', 'Техническое направление')
        elif role:
            role_name = role.get('name', 'Техническое направление')
        else:
            role_name = 'Техническое направление'

        # Формируем результаты для GPT
        competency_assessments = assessment.get('competency_assessments', [])
        assessment_results = []

        for ca in competency_assessments:
            competency = ca.get('competencies', {})
            assessment_results.append({
                'competency_id': competency.get('id'),
                'competency_name': competency.get('name'),
                'description': competency.get('description'),
                'score': ca.get('ai_assessed_score', 0),
                'confidence_level': ca.get('confidence_level'),
                'gap_analysis': ca.get('gap_analysis', {}),
                'knowledge_gaps': ca.get('gap_analysis', {}).get('knowledgeGaps', []) if isinstance(ca.get('gap_analysis'), dict) else []
            })

        # Генерируем roadmap через GPT
        roadmap_data = await self.openai.generate_roadmap(role_name, assessment_results)

        # Сохраняем roadmap в БД
        roadmap = await self.supabase.create_roadmap(
            assessment_id=assessment_id,
            title=roadmap_data.get('title', f'Roadmap for {role_name}'),
            description=roadmap_data.get('description'),
            estimated_duration_weeks=roadmap_data.get('estimatedDurationWeeks'),
            difficulty_level=None,  # Можно вычислить на основе секций
            priority_order=None  # Можно структурировать
        )

        roadmap_id = roadmap['id']

        # Сохраняем секции и их содержимое
        sections_data = roadmap_data.get('sections', [])
        for idx, section_data in enumerate(sections_data):
            # Находим competency_id по имени компетенции
            competency_id = None
            competency_name = section_data.get('competency')
            for result in assessment_results:
                if result['competency_name'] == competency_name:
                    competency_id = result['competency_id']
                    break

            # Создаем секцию
            section = await self.supabase.create_roadmap_section(
                roadmap_id=roadmap_id,
                competency_id=competency_id,
                title=section_data.get('competency', 'Untitled Section'),
                description=section_data.get('description'),
                order_index=idx + 1,
                estimated_duration_hours=section_data.get('estimatedHours')
            )

            section_id = section['id']

            # Learning materials
            materials = section_data.get('learningMaterials', [])
            for mat_idx, material in enumerate(materials):
                await self.supabase.create_learning_material(
                    roadmap_section_id=section_id,
                    material_type=material.get('type', 'article'),
                    title=material.get('title', ''),
                    url=material.get('url'),
                    description=material.get('description'),
                    author=material.get('author'),
                    duration_minutes=material.get('estimatedHours', 0) * 60 if material.get('estimatedHours') else None,
                    difficulty=material.get('difficulty'),
                    language=material.get('language'),
                    is_free=material.get('isFree', True),
                    order_index=mat_idx + 1,
                    rating=None
                )

            # Practice tasks
            tasks = section_data.get('practiceTasks', [])
            for task_idx, task in enumerate(tasks):
                requirements = task.get('requirements', {})
                await self.supabase.create_practice_task(
                    roadmap_section_id=section_id,
                    title=task.get('title', ''),
                    task_type=task.get('taskType', 'coding'),
                    description=task.get('description'),
                    difficulty=task.get('difficulty'),
                    estimated_time_minutes=task.get('estimatedHours', 0) * 60 if task.get('estimatedHours') else None,
                    requirements=requirements,
                    hints=requirements.get('hints'),
                    solution_example=None,
                    order_index=task_idx + 1
                )

            # Self-check questions
            questions = section_data.get('selfCheckQuestions', [])
            for q_idx, question in enumerate(questions):
                await self.supabase.create_self_check_question(
                    roadmap_section_id=section_id,
                    question_text=question.get('question', ''),
                    question_type=question.get('questionType', 'open_ended'),
                    options=None,  # Можно структурировать если multiple_choice
                    correct_answer=question.get('correctAnswer'),
                    explanation=question.get('explanation'),
                    difficulty=None,
                    order_index=q_idx + 1
                )

        return await self.supabase.get_roadmap_with_sections(roadmap_id)
