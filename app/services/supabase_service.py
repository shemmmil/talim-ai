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

    async def get_last_attempt_number(
        self,
        user_id: str,
        direction_id: Optional[str] = None,
        technology_id: Optional[str] = None
    ) -> int:
        """Получить номер последней попытки для пользователя по направлению и технологии"""
        try:
            query = self.client.table('assessments') \
                .select('attempt_number') \
                .eq('user_id', user_id)
            
            if direction_id:
                query = query.eq('direction_id', direction_id)
            else:
                query = query.is_('direction_id', 'null')
            
            if technology_id:
                query = query.eq('technology_id', technology_id)
            else:
                query = query.is_('technology_id', 'null')
            
            response = query \
                .order('attempt_number', desc=True) \
                .limit(1) \
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get('attempt_number', 0) + 1
            
            return 1
        except Exception as e:
            logger.error(f"Error getting last attempt number: {e}")
            # В случае ошибки возвращаем 1 (первая попытка)
            return 1

    async def create_assessment_without_role(
        self, 
        user_id: str, 
        direction_id: Optional[str] = None,
        technology_id: Optional[str] = None
    ) -> Dict:
        """Создать новое тестирование без привязки к роли"""
        try:
            # Получаем номер попытки
            attempt_number = await self.get_last_attempt_number(
                user_id,
                direction_id,
                technology_id
            )
            
            assessment_data = {
                'user_id': user_id,
                'role_id': None,
                'status': 'in_progress',
                'attempt_number': attempt_number
            }
            
            if direction_id:
                assessment_data['direction_id'] = direction_id
            
            if technology_id:
                assessment_data['technology_id'] = technology_id
            
            response = self.client.table('assessments').insert(assessment_data).execute()
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

    # === DIRECTIONS ===

    async def find_or_create_direction(
        self,
        name: str,
        display_name: Optional[str] = None,
        technologies: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """Найти направление по имени или создать новое"""
        try:
            # Ищем существующее направление
            response = self.client.table('directions') \
                .select('*') \
                .eq('name', name.lower()) \
                .limit(1) \
                .execute()
            
            if response.data:
                return response.data[0]
            
            # Создаем новое направление
            direction_data = {
                'name': name.lower(),
                'display_name': display_name or name,
                'description': description
            }
            
            if technologies:
                direction_data['technologies'] = technologies
            
            response = self.client.table('directions').insert(direction_data).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError("Failed to create direction - no data returned")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error finding/creating direction: {e}")
            raise

    async def get_direction(self, direction_id: str) -> Optional[Dict]:
        """Получить направление по ID"""
        try:
            response = self.client.table('directions') \
                .select('*') \
                .eq('id', direction_id) \
                .maybe_single() \
                .execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Error fetching direction: {e}")
            raise

    async def get_all_directions(self) -> List[Dict]:
        """Получить все направления"""
        try:
            response = self.client.table('directions') \
                .select('*') \
                .order('name') \
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching directions: {e}")
            raise

    async def get_direction_competencies(self, direction_id: str) -> List[Dict]:
        """Получить компетенции для направления"""
        try:
            response = self.client.table('direction_competencies') \
                .select('*, competencies(*)') \
                .eq('direction_id', direction_id) \
                .order('order_index') \
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching direction competencies: {e}")
            raise

    async def create_direction_competency(
        self,
        direction_id: str,
        competency_id: str,
        order_index: Optional[int] = None
    ) -> Dict:
        """Создать связь между направлением и компетенцией"""
        try:
            data = {
                'direction_id': direction_id,
                'competency_id': competency_id
            }
            
            if order_index is not None:
                data['order_index'] = order_index
            
            response = self.client.table('direction_competencies').insert(data).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError("Failed to create direction_competency - no data returned")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating direction_competency: {e}")
            raise

    # === TECHNOLOGIES ===

    async def find_or_create_technology(
        self,
        name: str,
        description: Optional[str] = None
    ) -> Dict:
        """Найти технологию по имени или создать новую"""
        try:
            # Ищем существующую технологию
            response = self.client.table('technologies') \
                .select('*') \
                .eq('name', name.lower()) \
                .limit(1) \
                .execute()
            
            if response.data:
                return response.data[0]
            
            # Создаем новую технологию
            technology_data = {
                'name': name.lower(),
                'description': description
            }
            
            response = self.client.table('technologies').insert(technology_data).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError("Failed to create technology - no data returned")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error finding/creating technology: {e}")
            raise

    async def get_technology(self, technology_id: str) -> Optional[Dict]:
        """Получить технологию по ID"""
        try:
            response = self.client.table('technologies') \
                .select('*') \
                .eq('id', technology_id) \
                .maybe_single() \
                .execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Error fetching technology: {e}")
            raise

    async def get_direction_technologies(self, direction_id: str) -> List[Dict]:
        """Получить технологии для направления"""
        try:
            response = self.client.table('direction_technologies') \
                .select('*, technologies(*)') \
                .eq('direction_id', direction_id) \
                .order('order_index') \
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching direction technologies: {e}")
            raise

    async def get_technology_competencies(self, technology_id: str) -> List[Dict]:
        """Получить компетенции для технологии"""
        try:
            response = self.client.table('technology_competencies') \
                .select('*, competencies(*)') \
                .eq('technology_id', technology_id) \
                .order('order_index') \
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching technology competencies: {e}")
            raise

    async def create_direction_technology(
        self,
        direction_id: str,
        technology_id: str,
        order_index: Optional[int] = None
    ) -> Dict:
        """Создать связь между направлением и технологией"""
        try:
            data = {
                'direction_id': direction_id,
                'technology_id': technology_id
            }
            
            if order_index is not None:
                data['order_index'] = order_index
            
            response = self.client.table('direction_technologies').insert(data).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError("Failed to create direction_technology - no data returned")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating direction_technology: {e}")
            raise

    async def create_technology_competency(
        self,
        technology_id: str,
        competency_id: str,
        order_index: Optional[int] = None
    ) -> Dict:
        """Создать связь между технологией и компетенцией"""
        try:
            data = {
                'technology_id': technology_id,
                'competency_id': competency_id
            }
            
            if order_index is not None:
                data['order_index'] = order_index
            
            response = self.client.table('technology_competencies').insert(data).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError("Failed to create technology_competency - no data returned")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating technology_competency: {e}")
            raise

    async def get_assessments_by_user(
        self,
        user_id: str,
        direction_id: Optional[str] = None,
        technology_id: Optional[str] = None
    ) -> List[Dict]:
        """Получить список всех тестирований пользователя"""
        try:
            # Получаем assessments без join (чтобы избежать ошибок с NULL foreign keys)
            query = self.client.table('assessments') \
                .select('*') \
                .eq('user_id', user_id)
            
            if direction_id:
                query = query.eq('direction_id', direction_id)
            
            if technology_id:
                query = query.eq('technology_id', technology_id)
            
            response = query \
                .order('attempt_number', desc=True) \
                .order('started_at', desc=True) \
                .execute()
            
            assessments = response.data if response.data else []
            
            # Для каждого assessment получаем связанные данные, если они есть
            for assessment in assessments:
                # Получаем role, если role_id не NULL
                if assessment.get('role_id'):
                    try:
                        role_response = self.client.table('roles') \
                            .select('*') \
                            .eq('id', assessment['role_id']) \
                            .maybe_single() \
                            .execute()
                        if role_response.data:
                            assessment['roles'] = role_response.data
                    except Exception as e:
                        logger.warning(f"Could not fetch role for assessment {assessment.get('id')}: {e}")
                
                # Получаем direction, если direction_id не NULL
                if assessment.get('direction_id'):
                    try:
                        direction_response = self.client.table('directions') \
                            .select('*') \
                            .eq('id', assessment['direction_id']) \
                            .maybe_single() \
                            .execute()
                        if direction_response.data:
                            assessment['directions'] = direction_response.data
                    except Exception as e:
                        logger.warning(f"Could not fetch direction for assessment {assessment.get('id')}: {e}")
                
                # Получаем technology, если technology_id не NULL
                if assessment.get('technology_id'):
                    try:
                        technology_response = self.client.table('technologies') \
                            .select('*') \
                            .eq('id', assessment['technology_id']) \
                            .maybe_single() \
                            .execute()
                        if technology_response.data:
                            assessment['technologies'] = technology_response.data
                    except Exception as e:
                        logger.warning(f"Could not fetch technology for assessment {assessment.get('id')}: {e}")
            
            return assessments
        except Exception as e:
            logger.error(f"Error fetching user assessments: {e}")
            raise

    async def get_assessment(self, assessment_id: str) -> Optional[Dict]:
        """Получить информацию о тестировании"""
        try:
            # Получаем assessment с competency_assessments (это всегда работает)
            response = self.client.table('assessments') \
                .select('*, competency_assessments(*, competencies(*))') \
                .eq('id', assessment_id) \
                .maybe_single() \
                .execute()
            
            # maybe_single() возвращает None если запись не найдена
            if response.data is None:
                return None
            
            assessment = response.data
            
            # Получаем role, если role_id не NULL
            if assessment.get('role_id'):
                try:
                    role_response = self.client.table('roles') \
                        .select('*') \
                        .eq('id', assessment['role_id']) \
                        .maybe_single() \
                        .execute()
                    if role_response.data:
                        assessment['roles'] = role_response.data
                except Exception as e:
                    logger.warning(f"Could not fetch role for assessment {assessment_id}: {e}")
            
            # Получаем direction, если direction_id не NULL
            if assessment.get('direction_id'):
                try:
                    direction_response = self.client.table('directions') \
                        .select('*') \
                        .eq('id', assessment['direction_id']) \
                        .maybe_single() \
                        .execute()
                    if direction_response.data:
                        assessment['directions'] = direction_response.data
                except Exception as e:
                    logger.warning(f"Could not fetch direction for assessment {assessment_id}: {e}")
            
            # Получаем technology, если technology_id не NULL
            if assessment.get('technology_id'):
                try:
                    technology_response = self.client.table('technologies') \
                        .select('*') \
                        .eq('id', assessment['technology_id']) \
                        .maybe_single() \
                        .execute()
                    if technology_response.data:
                        assessment['technologies'] = technology_response.data
                except Exception as e:
                    logger.warning(f"Could not fetch technology for assessment {assessment_id}: {e}")
            
            return assessment
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

    # === QUESTIONS (предварительно сгенерированные вопросы) ===

    async def find_question(
        self,
        competency_id: str,
        difficulty: int,
        question_number: Optional[int] = None,
        exclude_question_ids: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Найти вопрос в БД по компетенции и сложности.
        
        Args:
            competency_id: ID компетенции
            difficulty: Уровень сложности (1-5)
            question_number: Опциональный номер вопроса (1-5)
            exclude_question_ids: Список ID вопросов, которые нужно исключить (уже использованные)
        """
        try:
            query = self.client.table('questions') \
                .select('*') \
                .eq('competency_id', competency_id) \
                .eq('difficulty', difficulty)
            
            if question_number is not None:
                query = query.eq('question_number', question_number)
            
            # Исключаем уже использованные вопросы
            filtered_questions = None
            if exclude_question_ids and len(exclude_question_ids) > 0:
                # Supabase не поддерживает .not().in() напрямую, поэтому используем фильтрацию
                # Получаем все вопросы и фильтруем в Python
                response = query \
                    .order('used_count') \
                    .execute()
                
                # Фильтруем исключенные вопросы
                filtered_questions = [
                    q for q in (response.data or [])
                    if str(q.get('id')) not in exclude_question_ids
                ]
                
                if filtered_questions:
                    logger.debug(
                        f"Searching question: competency_id={competency_id}, "
                        f"difficulty={difficulty}, question_number={question_number}, "
                        f"excluded={len(exclude_question_ids)} questions, "
                        f"found={len(filtered_questions)} available"
                    )
                    return filtered_questions[0]
            else:
                # Если нет исключений, используем старую логику
                response = query \
                    .order('used_count') \
                    .limit(1) \
                    .execute()
                
                logger.debug(
                    f"Searching question: competency_id={competency_id}, "
                    f"difficulty={difficulty}, question_number={question_number}, "
                    f"found={len(response.data) if response.data else 0}"
                )
                
                if response.data and len(response.data) > 0:
                    return response.data[0]
            
            # Если ничего не найдено, логируем для диагностики
            found_questions = filtered_questions if filtered_questions is not None else (response.data if response.data else [])
            if not found_questions:
                try:
                    check_query = self.client.table('questions') \
                        .select('id, difficulty, question_number', count='exact') \
                        .eq('competency_id', competency_id) \
                        .limit(10) \
                        .execute()
                    
                    available_questions = check_query.data if check_query.data else []
                    excluded_count = len(exclude_question_ids) if exclude_question_ids else 0
                    logger.warning(
                        f"No question found for competency_id={competency_id}, "
                        f"difficulty={difficulty}, question_number={question_number}. "
                        f"Excluded {excluded_count} questions. "
                        f"Available questions for this competency: {len(available_questions)}. "
                        f"Sample: {[(q.get('difficulty'), q.get('question_number')) for q in available_questions[:5]]}"
                    )
                except Exception as check_error:
                    logger.error(f"Error checking available questions: {check_error}")
                
                return None
            
            return None
        except Exception as e:
            logger.error(f"Error finding question: {e}", exc_info=True)
            raise

    async def create_question(
        self,
        competency_id: str,
        question_text: str,
        difficulty: int,
        question_number: Optional[int] = None,
        expected_key_points: Optional[List[str]] = None,
        estimated_answer_time: Optional[str] = None
    ) -> Dict:
        """Создать новый вопрос в БД"""
        try:
            question_data = {
                'competency_id': competency_id,
                'question_text': question_text,
                'difficulty': difficulty,
                'used_count': 0
            }
            
            if question_number is not None:
                question_data['question_number'] = question_number
            if expected_key_points is not None:
                question_data['expected_key_points'] = expected_key_points
            if estimated_answer_time is not None:
                question_data['estimated_answer_time'] = estimated_answer_time
            
            response = self.client.table('questions').insert(question_data).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError("Failed to create question - no data returned")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating question: {e}")
            raise

    async def increment_question_usage(self, question_id: str) -> Dict:
        """Увеличить счетчик использования вопроса"""
        try:
            # Получаем текущее значение used_count
            response = self.client.table('questions') \
                .select('used_count') \
                .eq('id', question_id) \
                .single() \
                .execute()
            
            if not response.data:
                raise ValueError(f"Question with id {question_id} not found")
            
            current_count = response.data.get('used_count', 0)
            
            # Увеличиваем счетчик
            update_response = self.client.table('questions') \
                .update({
                    'used_count': current_count + 1,
                    'updated_at': datetime.utcnow().isoformat()
                }) \
                .eq('id', question_id) \
                .execute()
            
            if not update_response.data or len(update_response.data) == 0:
                raise ValueError(f"Failed to update question usage - no data returned")
            
            return update_response.data[0]
        except Exception as e:
            logger.error(f"Error incrementing question usage: {e}")
            raise

    # === QUESTION HISTORY ===

    async def create_question_history(
        self,
        competency_assessment_id: str,
        question_text: str,
        difficulty_level: Optional[int] = None,
        question_type: Optional[str] = None,
        question_id: Optional[str] = None
    ) -> Dict:
        """Создать запись вопроса в истории"""
        try:
            history_data = {
                'competency_assessment_id': competency_assessment_id,
                'question_text': question_text,
                'difficulty_level': difficulty_level,
                'question_type': question_type
            }
            
            if question_id is not None:
                history_data['question_id'] = question_id
            
            response = self.client.table('question_history').insert(history_data).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError("Failed to create question history - no data returned")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating question history: {e}")
            raise

    async def update_question_history(
        self,
        question_id: str,
        score: Optional[int] = None,
        is_correct: Optional[bool] = None,
        understanding_depth: Optional[str] = None,
        feedback: Optional[str] = None,
        knowledge_gaps: Optional[List[str]] = None,
        time_spent_seconds: Optional[int] = None,
        # Для обратной совместимости (deprecated, будут игнорироваться)
        user_answer_transcript: Optional[str] = None,
        audio_duration_seconds: Optional[int] = None,
        transcription_confidence: Optional[float] = None,
        ai_evaluation: Optional[Dict] = None
    ) -> Dict:
        """
        Обновить запись вопроса с ответом.
        Сохраняет только оценки и результаты, без текстовых транскриптов.
        """
        try:
            update_data = {}
            
            # Новые структурированные поля
            if score is not None:
                update_data['score'] = score
            if is_correct is not None:
                update_data['is_correct'] = is_correct
            if understanding_depth is not None:
                update_data['understanding_depth'] = understanding_depth
            if feedback is not None:
                update_data['feedback'] = feedback
            if knowledge_gaps is not None:
                update_data['knowledge_gaps'] = knowledge_gaps
            if time_spent_seconds is not None:
                update_data['time_spent_seconds'] = time_spent_seconds
            
            # Для обратной совместимости: если передан ai_evaluation, извлекаем данные
            if ai_evaluation is not None:
                if 'score' not in update_data and 'score' in ai_evaluation:
                    update_data['score'] = ai_evaluation['score']
                if 'is_correct' not in update_data and 'isCorrect' in ai_evaluation:
                    update_data['is_correct'] = ai_evaluation['isCorrect']
                if 'understanding_depth' not in update_data and 'understandingDepth' in ai_evaluation:
                    update_data['understanding_depth'] = ai_evaluation['understandingDepth']
                if 'feedback' not in update_data and 'feedback' in ai_evaluation:
                    update_data['feedback'] = ai_evaluation['feedback']
                if 'knowledge_gaps' not in update_data and 'knowledgeGaps' in ai_evaluation:
                    update_data['knowledge_gaps'] = ai_evaluation['knowledgeGaps']
            
            # Устанавливаем время ответа, если есть данные для сохранения
            if update_data:
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

