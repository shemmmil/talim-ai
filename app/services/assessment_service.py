from typing import Dict, List, Optional
from uuid import UUID
import logging
from app.services.supabase_service import SupabaseService
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class AssessmentService:
    def __init__(self, supabase_service: SupabaseService, openai_service: OpenAIService):
        self.supabase = supabase_service
        self.openai = openai_service

    async def start_assessment(self, user_id: str, role_id: str) -> Dict:
        """Начать новое тестирование (старый метод для обратной совместимости)"""
        # Создаем assessment
        assessment = await self.supabase.create_assessment(user_id, role_id)

        # Получаем компетенции для роли
        competencies = await self.supabase.get_role_competencies(role_id)

        # Создаем competency_assessments для каждой компетенции
        for competency in competencies:
            await self.supabase.create_competency_assessment(
                assessment['id'],
                competency['id']
            )

        return {
            "assessment_id": assessment['id'],
            "competencies": competencies,
            "status": assessment['status']
        }

    async def start_assessment_by_direction(self, user_id: str, direction: str) -> Dict:
        """Начать новое тестирование по направлению (тексту)"""
        # Убеждаемся, что пользователь существует в БД (создаем если нет)
        await self.supabase.get_or_create_user(user_id)
        
        # Определяем компетенции через GPT по тексту направления
        competencies_data = await self.openai.determine_competencies_by_direction(direction)
        
        # Создаем assessment БЕЗ role_id (NULL)
        assessment = await self.supabase.create_assessment_without_role(user_id)

        # Создаем competency_assessments для каждой компетенции
        competencies = []
        for comp_data in competencies_data.get('competencies', []):
            # Ищем компетенцию в БД по имени или создаем виртуальную
            competency = await self.supabase.find_or_create_competency_by_name(
                comp_data['name'],
                comp_data.get('description', ''),
                comp_data.get('category')
            )
            
            await self.supabase.create_competency_assessment(
                assessment['id'],
                competency['id']
            )
            competencies.append(competency)

        return {
            "assessment_id": assessment['id'],
            "competencies": competencies,
            "status": assessment['status']
        }

    async def get_assessment_with_progress(self, assessment_id: str) -> Optional[Dict]:
        """Получить assessment с прогрессом"""
        assessment = await self.supabase.get_assessment(assessment_id)
        return assessment

    async def calculate_overall_score(self, assessment_id: str) -> float:
        """Вычислить общий балл assessment на основе всех competency assessments"""
        assessment = await self.supabase.get_assessment(assessment_id)
        if not assessment:
            return 0.0

        competency_assessments = assessment.get('competency_assessments', [])
        if not competency_assessments:
            return 0.0

        total_score = 0.0
        total_weight = 0.0

        for ca in competency_assessments:
            score = ca.get('ai_assessed_score')
            if score is None:
                continue

            # Получаем вес компетенции
            competency = ca.get('competencies', {})
            weight = competency.get('importance_weight', 1) or 1

            total_score += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return round(total_score / total_weight, 2)

    async def complete_assessment(self, assessment_id: str) -> Dict:
        """Завершить тестирование и вычислить общий балл"""
        # Вычисляем общий балл
        overall_score = await self.calculate_overall_score(assessment_id)

        # Обновляем статус
        assessment = await self.supabase.update_assessment_status(
            assessment_id,
            'completed',
            overall_score
        )

        return assessment

    async def get_competency_assessment_context(
        self,
        assessment_id: str,
        competency_id: str
    ) -> Dict:
        """Получить контекст для генерации вопроса (предыдущие ответы, пробелы)"""
        # Получаем competency_assessment
        ca = await self.supabase.get_competency_assessment_by_ids(
            assessment_id,
            competency_id
        )

        if not ca:
            return {
                "previous_answers": [],
                "knowledge_gaps": [],
                "current_difficulty": 3
            }

        # Получаем историю вопросов
        question_history = await self.supabase.get_question_history(ca['id'])

        # Формируем предыдущие ответы
        previous_answers = []
        all_knowledge_gaps = []

        for qh in question_history:
            if qh.get('user_answer_transcript') and qh.get('ai_evaluation'):
                eval_data = qh['ai_evaluation']
                previous_answers.append({
                    'question': qh['question_text'],
                    'answer': qh['user_answer_transcript'],
                    'score': eval_data.get('score', 0)
                })
                # Собираем пробелы в знаниях
                gaps = eval_data.get('knowledgeGaps', [])
                all_knowledge_gaps.extend(gaps)

        # Определяем текущую сложность (последний вопрос или среднее)
        current_difficulty = 3
        if question_history:
            last_q = question_history[-1]
            if last_q.get('ai_evaluation'):
                current_difficulty = last_q['ai_evaluation'].get('nextDifficulty', 3)
            elif last_q.get('difficulty_level'):
                current_difficulty = last_q['difficulty_level']

        # Убираем дубликаты пробелов
        unique_gaps = list(set(all_knowledge_gaps))

        return {
            "previous_answers": previous_answers,
            "knowledge_gaps": unique_gaps,
            "current_difficulty": current_difficulty,
            "competency_assessment_id": ca['id'],
            "questions_asked": len(question_history)
        }
