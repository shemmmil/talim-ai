from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, Dict
from uuid import UUID
import logging
from app.api.deps import get_supabase_service, get_openai_service, get_current_user_id
from app.services.supabase_service import SupabaseService
from app.services.openai_service import OpenAIService
from app.services.assessment_service import AssessmentService
from app.utils.audio import validate_audio_file, save_temp_audio_file, cleanup_temp_file
from app.config import settings
from app.schemas.question import QuestionGenerateResponse, AnswerResponse, AnswerEvaluation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/questions", tags=["questions"])
# Новые RESTful эндпоинты будут в /api/assessments/{id}/questions и /api/assessments/{id}/answers


def get_assessment_service(
    supabase_service: SupabaseService = Depends(get_supabase_service),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> AssessmentService:
    return AssessmentService(supabase_service, openai_service)


@router.post(
    "/generate",
    response_model=QuestionGenerateResponse,
    summary="Получить вопрос",
    description="Получает вопрос для тестирования компетенции из базы данных. "
                "Вопрос должен быть предварительно добавлен в БД."
)
async def generate_question(
    assessment_id: UUID = Form(..., description="ID тестирования"),
    competency_id: UUID = Form(..., description="ID компетенции"),
    question_number: int = Form(..., description="Номер вопроса (1-5)", ge=1, le=5),
    difficulty: Optional[int] = Form(None, description="Уровень сложности (1-5). Если не указан, определяется автоматически", ge=1, le=5),
    assessment_service: AssessmentService = Depends(get_assessment_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Получить вопрос для тестирования компетенции из базы данных.
    
    - **assessment_id**: ID активного тестирования
    - **competency_id**: ID компетенции, по которой запрашивается вопрос
    - **question_number**: Номер вопроса в последовательности (от 1 до 5)
    - **difficulty**: Опциональный уровень сложности (1-5). Если не указан, определяется автоматически на основе предыдущих ответов
    
    Возвращает вопрос из БД, его сложность и ожидаемое время ответа.
    Если вопрос не найден, возвращает ошибку 404.
    """
    try:
        # Проверяем доступ к assessment
        assessment = await assessment_service.get_assessment_with_progress(str(assessment_id))
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        if assessment.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Получаем контекст
        context = await assessment_service.get_competency_assessment_context(
            str(assessment_id),
            str(competency_id)
        )

        # Определяем сложность
        if difficulty is None:
            difficulty = context.get('current_difficulty', 3)

        # Получаем информацию о компетенции
        # Если role_id есть - используем старый способ, иначе получаем компетенцию напрямую
        if assessment.get('role_id'):
            competencies = await supabase_service.get_role_competencies(assessment['role_id'])
            competency = next((c for c in competencies if str(c['id']) == str(competency_id)), None)
        else:
            # Получаем компетенцию напрямую из competency_assessments
            competency_assessments = assessment.get('competency_assessments', [])
            comp_assessment = next(
                (ca for ca in competency_assessments if str(ca.get('competency_id')) == str(competency_id)),
                None
            )
            if comp_assessment:
                competency = comp_assessment.get('competencies', {})
            else:
                competency = None
        
        if not competency:
            raise HTTPException(status_code=404, detail="Competency not found")

        # Получаем competency_assessment для получения уже использованных вопросов
        ca = await supabase_service.get_competency_assessment_by_ids(
            str(assessment_id),
            str(competency_id)
        )
        
        # Получаем список уже использованных вопросов для этого competency_assessment
        exclude_question_ids = []
        if ca and ca.get('id'):
            question_history = await supabase_service.get_question_history(str(ca['id']))
            # Собираем все question_id из истории, которые не None
            exclude_question_ids = [
                str(qh['question_id']) 
                for qh in question_history 
                if qh.get('question_id') is not None
            ]
            logger.info(
                f"Found {len(exclude_question_ids)} already used questions for "
                f"competency_assessment_id={ca['id']}"
            )

        # Ищем вопрос в БД, исключая уже использованные
        logger.info(
            f"Searching question: competency_id={competency_id}, "
            f"difficulty={difficulty}, question_number={question_number}, "
            f"excluding {len(exclude_question_ids)} used questions"
        )
        
        stored_question = await supabase_service.find_question(
            competency_id=str(competency_id),
            difficulty=difficulty,
            question_number=question_number,
            exclude_question_ids=exclude_question_ids if exclude_question_ids else None
        )

        if not stored_question:
            # Вопрос не найден в БД
            competency_name = competency.get('name', 'Unknown') if competency else 'Unknown'
            
            # Пытаемся найти вопрос без question_number (любой вопрос для этой компетенции и сложности)
            logger.info(f"Question not found with question_number, trying without it...")
            stored_question = await supabase_service.find_question(
                competency_id=str(competency_id),
                difficulty=difficulty,
                question_number=None,
                exclude_question_ids=exclude_question_ids if exclude_question_ids else None
            )
            
            if not stored_question:
                # Больше нет доступных вопросов для этой компетенции
                logger.info(
                    f"No more questions available for competency '{competency_name}' (id: {competency_id}) "
                    f"with difficulty {difficulty}. All questions have been used."
                )
                return QuestionGenerateResponse(
                    questionId=None,
                    questionText=None,
                    difficulty=None,
                    estimatedAnswerTime=None,
                    expectedKeyPoints=None,
                    noMoreQuestions=True
                )

        # Используем сохраненный вопрос
        logger.info(f"Using stored question from DB: {stored_question['id']}")
        
        # Увеличиваем счетчик использования
        await supabase_service.increment_question_usage(str(stored_question['id']))
        
        question_text = stored_question['question_text']
        # Обрабатываем expected_key_points - может быть списком или None
        expected_key_points_raw = stored_question.get('expected_key_points')
        if expected_key_points_raw is None:
            expected_key_points = []
        elif isinstance(expected_key_points_raw, list):
            expected_key_points = expected_key_points_raw
        else:
            # Если это строка или другой тип, пытаемся преобразовать
            expected_key_points = []
        
        estimated_answer_time = stored_question.get('estimated_answer_time', '1-2 минуты')
        question_id = stored_question['id']

        return QuestionGenerateResponse(
            questionId=UUID(question_id),
            questionText=question_text,
            difficulty=difficulty,
            estimatedAnswerTime=estimated_answer_time,
            expectedKeyPoints=expected_key_points,
            noMoreQuestions=False
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")


@router.post(
    "/answer",
    response_model=AnswerResponse,
    summary="Отправить голосовой ответ",
    description="Отправляет голосовой ответ на вопрос. Аудио файл транскрибируется через Whisper API, "
                "после чего ответ оценивается через GPT-4. Вопрос и ответ сохраняются в БД только после отправки."
)
async def submit_answer(
    assessment_id: UUID = Form(..., description="ID тестирования"),
    competency_id: UUID = Form(..., description="ID компетенции"),
    question_text: str = Form(..., description="Текст вопроса, на который отвечает пользователь"),
    difficulty: int = Form(3, description="Сложность вопроса (1-5)", ge=1, le=5),
    question_id: Optional[UUID] = Form(None, description="ID вопроса из БД (если был использован сохраненный вопрос)"),
    audio: UploadFile = File(..., description="Аудио файл с ответом (webm, mp3, wav, m4a, ogg). Максимум 25MB"),
    assessment_service: AssessmentService = Depends(get_assessment_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    openai_service: OpenAIService = Depends(get_openai_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Отправить голосовой ответ на вопрос.
    
    Процесс обработки:
    1. Валидация аудио файла (формат, размер)
    2. Транскрипция аудио в текст через OpenAI Whisper API
    3. Оценка ответа через GPT-4
    4. Сохранение вопроса и ответа в базу данных (впервые)
    5. Обновление оценки компетенции
    
    Поддерживаемые форматы: webm, mp3, wav, m4a, ogg
    Максимальный размер файла: 25 MB
    """
    temp_file_path = None

    try:
        # Проверяем доступ к assessment
        assessment = await assessment_service.get_assessment_with_progress(str(assessment_id))
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        if assessment.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Валидация файла
        is_valid, error_msg = validate_audio_file(
            audio,
            max_size_mb=settings.max_audio_file_size_mb,
            allowed_formats=settings.allowed_audio_formats
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Получаем или создаем competency_assessment
        ca = await supabase_service.get_competency_assessment_by_ids(
            str(assessment_id),
            str(competency_id)
        )
        if not ca:
            ca = await supabase_service.create_competency_assessment(
                str(assessment_id),
                str(competency_id)
            )
        
        if not ca or 'id' not in ca:
            raise HTTPException(
                status_code=500,
                detail="Failed to get or create competency assessment"
            )
        
        competency_assessment_id = ca['id']

        # Получаем информацию о компетенции
        competency_assessments = assessment.get('competency_assessments', [])
        comp_assessment = next(
            (ca_item for ca_item in competency_assessments if str(ca_item.get('competency_id')) == str(competency_id)),
            None
        )
        competency = comp_assessment.get('competencies', {}) if comp_assessment else {}

        # Проверяем доступ
        if assessment.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Сохраняем временный файл
        temp_file_path = await save_temp_audio_file(audio)

        # Транскрибируем аудио
        transcription = await openai_service.transcribe_audio(temp_file_path)

        # Оцениваем ответ
        evaluation = await openai_service.evaluate_answer(
            question_text=question_text,
            transcript=transcription['text'],
            competency_name=competency.get('name', 'Unknown') if competency else 'Unknown',
            difficulty=difficulty
        )

        # Используем переданный question_id или пытаемся найти вопрос по тексту
        stored_question_id = None
        if question_id:
            stored_question_id = str(question_id)
            logger.info(f"Using provided question_id: {stored_question_id}")
        else:
            # Пытаемся найти сохраненный вопрос по тексту и компетенции
            try:
                stored_question = await supabase_service.find_question(
                    competency_id=str(competency_id),
                    difficulty=difficulty
                )
                # Проверяем, что текст совпадает (примерно)
                if stored_question and stored_question.get('question_text') == question_text:
                    stored_question_id = str(stored_question['id'])
                    logger.info(f"Found stored question by text: {stored_question_id}")
            except Exception as e:
                logger.warning(f"Could not find stored question: {e}")

        # Сохраняем вопрос и ответ в БД (впервые, только после ответа)
        question_history = await supabase_service.create_question_history(
            competency_assessment_id=str(competency_assessment_id),
            question_text=question_text,
            difficulty_level=difficulty,
            question_type=None,
            question_id=stored_question_id
        )

        if not question_history or 'id' not in question_history:
            raise HTTPException(
                status_code=500,
                detail="Failed to create question history record"
            )

        # Обновляем вопрос с ответом и оценкой (сохраняем только оценки, не транскрипты)
        await supabase_service.update_question_history(
            question_id=str(question_history['id']),
            score=evaluation.get('score'),
            is_correct=evaluation.get('isCorrect'),
            understanding_depth=evaluation.get('understandingDepth'),
            feedback=evaluation.get('feedback'),
            knowledge_gaps=evaluation.get('knowledgeGaps', []),
            time_spent_seconds=None  # Можно добавить из фронтенда
            # Транскрипт НЕ сохраняется для экономии места
        )

        # Обновляем competency_assessment с учетом новой оценки
        # Собираем все оценки для этой компетенции
        all_questions = await supabase_service.get_question_history(
            str(competency_assessment_id)
        )

        # Используем новые структурированные поля
        answered_questions = [q for q in all_questions if q.get('score') is not None]
        if answered_questions:
            # Вычисляем средний балл
            scores = [q.get('score', 0) for q in answered_questions]
            avg_score = sum(scores) / len(scores) if scores else 0

            # Собираем все пробелы
            all_gaps = []
            for q in answered_questions:
                gaps = q.get('knowledge_gaps', [])
                if gaps:
                    all_gaps.extend(gaps)

            unique_gaps = list(set(all_gaps))

            # Определяем confidence_level на основе количества ответов
            if len(answered_questions) >= 5:
                confidence = 'high'
            elif len(answered_questions) >= 3:
                confidence = 'medium'
            else:
                confidence = 'low'

            # Округляем оценку (минимум 1, максимум 5)
            final_score = max(1, min(5, int(round(avg_score))))
            
            logger.info(
                f"Updating competency assessment {competency_assessment_id}: "
                f"scores={scores}, avg_score={avg_score}, final_score={final_score}, "
                f"confidence={confidence}, answered={len(answered_questions)}/{len(all_questions)}"
            )
            
            await supabase_service.update_competency_assessment(
                competency_assessment_id=str(competency_assessment_id),
                ai_assessed_score=final_score,
                confidence_level=confidence,
                gap_analysis={'knowledgeGaps': unique_gaps},
                test_session_data={
                    'questionsCount': len(all_questions),
                    'answeredCount': len(answered_questions),
                    'averageScore': avg_score
                }
            )

        return AnswerResponse(
            transcript=transcription['text'],
            evaluation=AnswerEvaluation(
                score=evaluation['score'],
                understandingDepth=evaluation['understandingDepth'],
                isCorrect=evaluation['isCorrect'],
                feedback=evaluation['feedback'],
                knowledgeGaps=evaluation['knowledgeGaps'],
                nextDifficulty=evaluation['nextDifficulty'],
                reasoning=evaluation.get('reasoning'),
                correctAnswer=evaluation.get('correctAnswer', ''),
                expectedKeyPoints=evaluation.get('expectedKeyPoints', [])
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing answer: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing answer: {str(e)}")
    finally:
        # Очищаем временный файл
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
