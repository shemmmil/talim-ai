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

    async def start_assessment_by_direction(
        self, 
        user_id: str, 
        direction: str, 
        technology: Optional[str] = None
    ) -> Dict:
        """Начать новое тестирование по направлению и технологии"""
        # Убеждаемся, что пользователь существует в БД (создаем если нет)
        await self.supabase.get_or_create_user(user_id)
        
        # Находим направление в БД
        direction_obj = await self.supabase.find_or_create_direction(
            name=direction.lower(),
            display_name=direction
        )
        direction_id = direction_obj['id']
        
        technology_id = None
        competencies = []
        
        if technology:
            # Если указана технология, используем компетенции технологии
            technology_obj = await self.supabase.find_or_create_technology(
                name=technology.lower()
            )
            technology_id = technology_obj['id']
            
            # Получаем компетенции для технологии
            technology_competencies = await self.supabase.get_technology_competencies(
                str(technology_id)
            )
            
            logger.info(f"Found {len(technology_competencies)} technology competencies for {technology}")
            
            if not technology_competencies:
                # Проверяем, существует ли технология
                technology_obj = await self.supabase.find_or_create_technology(
                    name=technology.lower()
                )
                raise ValueError(
                    f"No competencies found for technology '{technology}' in direction '{direction}'. "
                    f"Please add competencies to the technology first. "
                    f"You can use the SQL script 'database/migrations/seed_angular_competencies.sql' "
                    f"or add competencies via the admin API at /api/admin/technologies/{technology_obj['id']}/competencies/{{competency_id}}"
                )
            
            # Извлекаем компетенции из структуры ответа Supabase
            competencies = []
            for tc in technology_competencies:
                comp = tc.get('competencies')
                # Supabase может вернуть компетенцию как объект или как массив
                if isinstance(comp, dict) and comp.get('id'):
                    competencies.append(comp)
                elif isinstance(comp, list) and len(comp) > 0:
                    competencies.extend([c for c in comp if c.get('id')])
        else:
            # Если технология не указана, используем общие компетенции направления
            direction_competencies = await self.supabase.get_direction_competencies(
                str(direction_id)
            )
            
            logger.info(f"Found {len(direction_competencies)} direction competencies for {direction}")
            
            if not direction_competencies:
                raise ValueError(
                    f"No competencies found for direction '{direction}'. "
                    f"Please add competencies to the direction first, or specify a technology."
                )
            
            # Извлекаем компетенции из структуры ответа Supabase
            competencies = []
            for dc in direction_competencies:
                comp = dc.get('competencies')
                # Supabase может вернуть компетенцию как объект или как массив
                if isinstance(comp, dict) and comp.get('id'):
                    competencies.append(comp)
                elif isinstance(comp, list) and len(comp) > 0:
                    competencies.extend([c for c in comp if c.get('id')])
        
        # Создаем assessment с direction_id и technology_id
        assessment = await self.supabase.create_assessment_without_role(
            user_id,
            direction_id=str(direction_id),
            technology_id=str(technology_id) if technology_id else None
        )

        # Проверяем, что есть компетенции
        if not competencies:
            raise ValueError(
                f"No competencies found. "
                f"Direction: '{direction}', Technology: '{technology or 'not specified'}'"
            )
        
        # Фильтруем валидные компетенции
        valid_competencies = [
            comp for comp in competencies 
            if comp and comp.get('id')
        ]
        
        if not valid_competencies:
            raise ValueError(
                f"No valid competencies found. "
                f"Direction: '{direction}', Technology: '{technology or 'not specified'}'"
            )
        
        # Создаем competency_assessments для каждой компетенции
        for competency in valid_competencies:
            try:
                await self.supabase.create_competency_assessment(
                    assessment['id'],
                    competency['id']
                )
            except Exception as e:
                logger.error(f"Error creating competency_assessment for competency {competency.get('id')}: {e}")
                # Продолжаем создание остальных компетенций
                continue

        return {
            "assessment_id": assessment['id'],
            "competencies": valid_competencies,
            "status": assessment['status']
        }

    async def get_user_assessments(
        self,
        user_id: str,
        direction_id: Optional[str] = None,
        technology_id: Optional[str] = None
    ) -> List[Dict]:
        """Получить список всех тестирований пользователя"""
        assessments = await self.supabase.get_assessments_by_user(
            user_id,
            direction_id,
            technology_id
        )
        return assessments

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
        # Получаем assessment с прогрессом
        assessment = await self.supabase.get_assessment(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        # Проверяем, есть ли ответы
        competency_assessments = assessment.get('competency_assessments', [])
        total_answers = 0
        answered_competencies = 0
        
        for ca in competency_assessments:
            ca_id = ca.get('id')
            if ca_id:
                question_history = await self.supabase.get_question_history(str(ca_id))
                answered_count = len([q for q in question_history if q.get('user_answer_transcript')])
                total_answers += answered_count
                if answered_count > 0:
                    answered_competencies += 1
        
        logger.info(
            f"Completing assessment {assessment_id}: "
            f"{answered_competencies}/{len(competency_assessments)} competencies have answers, "
            f"total {total_answers} answers"
        )
        
        if total_answers == 0:
            logger.warning(
                f"Assessment {assessment_id} is being completed without any answers. "
                f"This will result in overall_score = 0.0"
            )
        
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
