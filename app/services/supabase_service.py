from supabase import Client
from typing import List, Dict, Optional
import logging
from uuid import UUID
from datetime import datetime

logger = logging.getLogger(__name__)


class SupabaseService:
    def __init__(self, client: Client):
        self.client = client

    # === ROLES & COMPETENCIES ===

    async def get_user_roles(self, user_id: str) -> List[Dict]:
        """Получить роли пользователя"""
        try:
            response = self.client.table('user_roles') \
                .select('*, roles(*)') \
                .eq('user_id', user_id) \
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching user roles: {e}")
            raise

    async def get_all_roles(self) -> List[Dict]:
        """Получить все роли"""
        try:
            response = self.client.table('roles') \
                .select('*') \
                .order('name') \
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching roles: {e}")
            raise

    async def get_role_competencies(self, role_id: str) -> List[Dict]:
        """Получить компетенции для роли"""
        try:
            response = self.client.table('competencies') \
                .select('*') \
                .eq('role_id', role_id) \
                .order('order_index') \
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching competencies: {e}")
            raise

    # === USERS ===

    async def get_or_create_user(self, user_id: str, email: Optional[str] = None, full_name: Optional[str] = None) -> Dict:
        """Получить пользователя или создать нового, если его нет"""
        try:
            # Пытаемся получить пользователя
            response = self.client.table('users') \
                .select('*') \
                .eq('id', user_id) \
                .execute()
            
            if response.data:
                # Пользователь существует, обновляем last_login
                self.client.table('users') \
                    .update({'last_login': datetime.utcnow().isoformat()}) \
                    .eq('id', user_id) \
                    .execute()
                return response.data[0]
            
            # Пользователь не существует, создаем нового
            # Используем уникальный email на основе user_id, если email не передан
            user_email = email or f"user-{user_id}@temp.local"
            
            user_data = {
                'id': user_id,
                'email': user_email,
                'created_at': datetime.utcnow().isoformat(),
                'last_login': datetime.utcnow().isoformat()
            }
            
            if full_name:
                user_data['full_name'] = full_name
            
            response = self.client.table('users').insert(user_data).execute()
            logger.info(f"Created new user: {user_id}")
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error getting/creating user: {e}")
            raise

    # === ASSESSMENTS ===

    async def create_assessment(self, user_id: str, role_id: str) -> Dict:
        """Создать новое тестирование (старый метод для обратной совместимости)"""
        try:
            response = self.client.table('assessments').insert({
                'user_id': user_id,
                'role_id': role_id,
                'status': 'in_progress'
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating assessment: {e}")
            raise

    async def create_assessment_without_role(self, user_id: str) -> Dict:
        """Создать новое тестирование без привязки к роли"""
        try:
            response = self.client.table('assessments').insert({
                'user_id': user_id,
                'role_id': None,  # Не храним направление в БД
                'status': 'in_progress'
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating assessment: {e}")
            raise

    async def find_or_create_competency_by_name(
        self, 
        name: str, 
        description: str = "", 
        category: str = ""
    ) -> Dict:
        """Найти компетенцию по имени или создать новую (без привязки к роли)"""
        try:
            # Ищем существующую компетенцию
            response = self.client.table('competencies') \
                .select('*') \
                .eq('name', name) \
                .limit(1) \
                .execute()
            
            if response.data:
                return response.data[0]
            
            # Создаем новую компетенцию без role_id
            response = self.client.table('competencies').insert({
                'name': name,
                'description': description,
                'category': category,
                'role_id': None,  # Компетенция не привязана к роли
                'importance_weight': 3,
                'order_index': 0
            }).execute()
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error finding/creating competency: {e}")
            raise

    async def get_assessment(self, assessment_id: str) -> Optional[Dict]:
        """Получить информацию о тестировании"""
        try:
            response = self.client.table('assessments') \
                .select('*, roles(*), competency_assessments(*, competencies(*))') \
                .eq('id', assessment_id) \
                .single() \
                .execute()
            
            # single() может вернуть None если запись не найдена
            if response.data is None:
                return None
            
            return response.data
        except Exception as e:
            logger.error(f"Error fetching assessment: {e}")
            raise

    async def update_assessment_status(
        self,
        assessment_id: str,
        status: str,
        overall_score: Optional[float] = None
    ) -> Dict:
        """Обновить статус тестирования"""
        try:
            update_data = {'status': status}
            if overall_score is not None:
                update_data['overall_score'] = overall_score
            if status == 'completed':
                update_data['completed_at'] = datetime.utcnow().isoformat()

            response = self.client.table('assessments') \
                .update(update_data) \
                .eq('id', assessment_id) \
                .execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error updating assessment: {e}")
            raise

    # === COMPETENCY ASSESSMENTS ===

    async def create_competency_assessment(
        self,
        assessment_id: str,
        competency_id: str
    ) -> Dict:
        """Создать оценку компетенции"""
        try:
            response = self.client.table('competency_assessments').insert({
                'assessment_id': assessment_id,
                'competency_id': competency_id
            }).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError(f"Failed to create competency assessment - no data returned")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating competency assessment: {e}")
            raise

    async def update_competency_assessment(
        self,
        competency_assessment_id: str,
        ai_assessed_score: Optional[int] = None,
        confidence_level: Optional[str] = None,
        gap_analysis: Optional[Dict] = None,
        test_session_data: Optional[Dict] = None
    ) -> Dict:
        """Обновить оценку компетенции"""
        try:
            update_data = {}
            if ai_assessed_score is not None:
                update_data['ai_assessed_score'] = ai_assessed_score
            if confidence_level is not None:
                update_data['confidence_level'] = confidence_level
            if gap_analysis is not None:
                update_data['gap_analysis'] = gap_analysis
            if test_session_data is not None:
                update_data['test_session_data'] = test_session_data
            if ai_assessed_score is not None:
                update_data['completed_at'] = datetime.utcnow().isoformat()

            response = self.client.table('competency_assessments') \
                .update(update_data) \
                .eq('id', competency_assessment_id) \
                .execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError(f"Competency assessment with id {competency_assessment_id} not found or not updated")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error updating competency assessment: {e}")
            raise

    async def get_competency_assessment_by_ids(
        self,
        assessment_id: str,
        competency_id: str
    ) -> Optional[Dict]:
        """Получить оценку компетенции по assessment и competency id"""
        try:
            response = self.client.table('competency_assessments') \
                .select('*') \
                .eq('assessment_id', assessment_id) \
                .eq('competency_id', competency_id) \
                .maybe_single() \
                .execute()
            
            # maybe_single() возвращает None если запись не найдена
            if response.data is None:
                return None
            
            return response.data
        except Exception as e:
            logger.error(f"Error fetching competency assessment: {e}")
            raise

    # === QUESTION HISTORY ===

    async def create_question_history(
        self,
        competency_assessment_id: str,
        question_text: str,
        difficulty_level: Optional[int] = None,
        question_type: Optional[str] = None
    ) -> Dict:
        """Создать запись вопроса в истории"""
        try:
            response = self.client.table('question_history').insert({
                'competency_assessment_id': competency_assessment_id,
                'question_text': question_text,
                'difficulty_level': difficulty_level,
                'question_type': question_type
            }).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError("Failed to create question history - no data returned")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating question history: {e}")
            raise

    async def update_question_history(
        self,
        question_id: str,
        user_answer_transcript: Optional[str] = None,
        audio_duration_seconds: Optional[int] = None,
        transcription_confidence: Optional[float] = None,
        is_correct: Optional[bool] = None,
        ai_evaluation: Optional[Dict] = None,
        time_spent_seconds: Optional[int] = None
    ) -> Dict:
        """Обновить запись вопроса с ответом"""
        try:
            update_data = {}
            if user_answer_transcript is not None:
                update_data['user_answer_transcript'] = user_answer_transcript
            if audio_duration_seconds is not None:
                update_data['audio_duration_seconds'] = audio_duration_seconds
            if transcription_confidence is not None:
                update_data['transcription_confidence'] = transcription_confidence
            if is_correct is not None:
                update_data['is_correct'] = is_correct
            if ai_evaluation is not None:
                update_data['ai_evaluation'] = ai_evaluation
            if time_spent_seconds is not None:
                update_data['time_spent_seconds'] = time_spent_seconds
            if user_answer_transcript is not None:
                update_data['answered_at'] = datetime.utcnow().isoformat()

            response = self.client.table('question_history') \
                .update(update_data) \
                .eq('id', question_id) \
                .execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError(f"Question history with id {question_id} not found or not updated")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error updating question history: {e}")
            raise

    async def get_question_history(
        self,
        competency_assessment_id: str
    ) -> List[Dict]:
        """Получить историю вопросов для компетенции"""
        try:
            response = self.client.table('question_history') \
                .select('*') \
                .eq('competency_assessment_id', competency_assessment_id) \
                .order('asked_at') \
                .execute()
            
            if not response.data:
                return []
            
            return response.data
        except Exception as e:
            logger.error(f"Error fetching question history: {e}")
            raise

    # === ROADMAPS ===

    async def create_roadmap(
        self,
        assessment_id: str,
        title: str,
        description: Optional[str] = None,
        estimated_duration_weeks: Optional[int] = None,
        difficulty_level: Optional[int] = None,
        priority_order: Optional[Dict] = None
    ) -> Dict:
        """Создать roadmap"""
        try:
            response = self.client.table('roadmaps').insert({
                'assessment_id': assessment_id,
                'title': title,
                'description': description,
                'estimated_duration_weeks': estimated_duration_weeks,
                'difficulty_level': difficulty_level,
                'priority_order': priority_order,
                'status': 'active'
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating roadmap: {e}")
            raise

    async def get_roadmap_by_assessment(self, assessment_id: str) -> Optional[Dict]:
        """Получить roadmap по assessment id"""
        try:
            response = self.client.table('roadmaps') \
                .select('*') \
                .eq('assessment_id', assessment_id) \
                .maybe_single() \
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching roadmap: {e}")
            raise

    async def get_roadmap_with_sections(self, roadmap_id: str) -> Optional[Dict]:
        """Получить roadmap со всеми секциями и материалами"""
        try:
            # Получаем roadmap
            roadmap_response = self.client.table('roadmaps') \
                .select('*') \
                .eq('id', roadmap_id) \
                .single() \
                .execute()

            roadmap = roadmap_response.data

            # Получаем секции
            sections_response = self.client.table('roadmap_sections') \
                .select('*, competencies(*)') \
                .eq('roadmap_id', roadmap_id) \
                .order('order_index') \
                .execute()

            sections = sections_response.data

            # Для каждой секции получаем материалы, задачи и вопросы
            for section in sections:
                section_id = section['id']

                # Learning materials
                materials_response = self.client.table('learning_materials') \
                    .select('*') \
                    .eq('roadmap_section_id', section_id) \
                    .order('order_index') \
                    .execute()
                section['learning_materials'] = materials_response.data

                # Practice tasks
                tasks_response = self.client.table('practice_tasks') \
                    .select('*') \
                    .eq('roadmap_section_id', section_id) \
                    .order('order_index') \
                    .execute()
                section['practice_tasks'] = tasks_response.data

                # Self-check questions
                questions_response = self.client.table('self_check_questions') \
                    .select('*') \
                    .eq('roadmap_section_id', section_id) \
                    .order('order_index') \
                    .execute()
                section['self_check_questions'] = questions_response.data

            roadmap['sections'] = sections
            return roadmap

        except Exception as e:
            logger.error(f"Error fetching roadmap with sections: {e}")
            raise

    async def create_roadmap_section(
        self,
        roadmap_id: str,
        competency_id: Optional[str],
        title: str,
        description: Optional[str] = None,
        order_index: Optional[int] = None,
        estimated_duration_hours: Optional[int] = None
    ) -> Dict:
        """Создать секцию roadmap"""
        try:
            response = self.client.table('roadmap_sections').insert({
                'roadmap_id': roadmap_id,
                'competency_id': competency_id,
                'title': title,
                'description': description,
                'order_index': order_index,
                'estimated_duration_hours': estimated_duration_hours,
                'status': 'not_started'
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating roadmap section: {e}")
            raise

    async def create_learning_material(
        self,
        roadmap_section_id: str,
        material_type: str,
        title: str,
        url: Optional[str] = None,
        description: Optional[str] = None,
        author: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        difficulty: Optional[str] = None,
        language: Optional[str] = None,
        is_free: bool = True,
        order_index: Optional[int] = None,
        rating: Optional[float] = None
    ) -> Dict:
        """Создать материал для обучения"""
        try:
            response = self.client.table('learning_materials').insert({
                'roadmap_section_id': roadmap_section_id,
                'type': material_type,
                'title': title,
                'url': url,
                'description': description,
                'author': author,
                'duration_minutes': duration_minutes,
                'difficulty': difficulty,
                'language': language,
                'is_free': is_free,
                'order_index': order_index,
                'rating': rating
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating learning material: {e}")
            raise

    async def create_practice_task(
        self,
        roadmap_section_id: str,
        title: str,
        task_type: str,
        description: Optional[str] = None,
        difficulty: Optional[int] = None,
        estimated_time_minutes: Optional[int] = None,
        requirements: Optional[Dict] = None,
        hints: Optional[Dict] = None,
        solution_example: Optional[str] = None,
        order_index: Optional[int] = None
    ) -> Dict:
        """Создать практическую задачу"""
        try:
            response = self.client.table('practice_tasks').insert({
                'roadmap_section_id': roadmap_section_id,
                'title': title,
                'task_type': task_type,
                'description': description,
                'difficulty': difficulty,
                'estimated_time_minutes': estimated_time_minutes,
                'requirements': requirements,
                'hints': hints,
                'solution_example': solution_example,
                'order_index': order_index
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating practice task: {e}")
            raise

    async def create_self_check_question(
        self,
        roadmap_section_id: str,
        question_text: str,
        question_type: Optional[str] = None,
        options: Optional[Dict] = None,
        correct_answer: Optional[str] = None,
        explanation: Optional[str] = None,
        difficulty: Optional[int] = None,
        order_index: Optional[int] = None
    ) -> Dict:
        """Создать вопрос для самопроверки"""
        try:
            response = self.client.table('self_check_questions').insert({
                'roadmap_section_id': roadmap_section_id,
                'question_text': question_text,
                'question_type': question_type,
                'options': options,
                'correct_answer': correct_answer,
                'explanation': explanation,
                'difficulty': difficulty,
                'order_index': order_index
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating self-check question: {e}")
            raise
