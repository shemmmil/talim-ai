from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, Dict
from uuid import UUID
import uuid
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


def get_assessment_service(
    supabase_service: SupabaseService = Depends(get_supabase_service),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> AssessmentService:
    return AssessmentService(supabase_service, openai_service)


@router.post(
    "/generate",
    response_model=QuestionGenerateResponse,
    summary="Сгенерировать вопрос",
    description="Генерирует адаптивный вопрос для тестирования компетенции через GPT-4. "
                "Вопрос генерируется на основе предыдущих ответов и выявленных пробелов в знаниях."
)
async def generate_question(
    assessment_id: UUID = Form(..., description="ID тестирования"),
    competency_id: UUID = Form(..., description="ID компетенции"),
    question_number: int = Form(..., description="Номер вопроса (1-7)", ge=1, le=7),
    difficulty: Optional[int] = Form(None, description="Уровень сложности (1-5). Если не указан, определяется автоматически", ge=1, le=5),
    assessment_service: AssessmentService = Depends(get_assessment_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
    openai_service: OpenAIService = Depends(get_openai_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Сгенерировать новый адаптивный вопрос для тестирования компетенции.
    
    - **assessment_id**: ID активного тестирования
    - **competency_id**: ID компетенции, по которой генерируется вопрос
    - **question_number**: Номер вопроса в последовательности (от 1 до 7)
    - **difficulty**: Опциональный уровень сложности (1-5). Если не указан, определяется автоматически на основе предыдущих ответов
    
    Возвращает сгенерированный вопрос, его сложность и ожидаемое время ответа.
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

        # Используем направление из контекста или название компетенции
        role_name = "Техническое направление"  # Упрощенное название, т.к. направление не хранится

        # Генерируем вопрос динамически на основе предыдущих ответов
        question_data = await openai_service.generate_question(
            role_name=role_name,
            competency_name=competency.get('name', ''),
            competency_description=competency.get('description', ''),
            question_number=question_number,
            difficulty=difficulty,
            previous_answers=context.get('previous_answers'),
            knowledge_gaps=context.get('knowledge_gaps')
        )

        # НЕ сохраняем вопрос в БД - он будет сохранен только после ответа
        # Возвращаем вопрос с временным ID (можно использовать UUID для идентификации на фронтенде)
        temp_question_id = str(uuid.uuid4())

        return QuestionGenerateResponse(
            questionId=UUID(temp_question_id),  # Временный ID для фронтенда
            questionText=question_data['question'],
            difficulty=difficulty,
            estimatedAnswerTime=question_data.get('estimatedAnswerTime', '1-2 минуты'),
            expectedKeyPoints=question_data.get('expectedKeyPoints', [])
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

        # Сохраняем вопрос и ответ в БД (впервые, только после ответа)
        question_history = await supabase_service.create_question_history(
            competency_assessment_id=str(competency_assessment_id),
            question_text=question_text,
            difficulty_level=difficulty,
            question_type=None
        )

        if not question_history or 'id' not in question_history:
            raise HTTPException(
                status_code=500,
                detail="Failed to create question history record"
            )

        # Обновляем вопрос с ответом и оценкой
        await supabase_service.update_question_history(
            question_id=str(question_history['id']),
            user_answer_transcript=transcription['text'],
            audio_duration_seconds=int(transcription.get('duration', 0)) if transcription.get('duration') else None,
            transcription_confidence=None,  # Whisper не возвращает confidence напрямую
            is_correct=evaluation.get('isCorrect'),
            ai_evaluation=evaluation,
            time_spent_seconds=None  # Можно добавить из фронтенда
        )

        # Обновляем competency_assessment с учетом новой оценки
        # Собираем все оценки для этой компетенции
        all_questions = await supabase_service.get_question_history(
            str(competency_assessment_id)
        )

        answered_questions = [q for q in all_questions if q.get('ai_evaluation')]
        if answered_questions:
            # Вычисляем средний балл
            scores = [q['ai_evaluation'].get('score', 0) for q in answered_questions]
            avg_score = sum(scores) / len(scores) if scores else 0

            # Собираем все пробелы
            all_gaps = []
            for q in answered_questions:
                gaps = q['ai_evaluation'].get('knowledgeGaps', [])
                all_gaps.extend(gaps)

            unique_gaps = list(set(all_gaps))

            # Определяем confidence_level на основе количества ответов
            if len(answered_questions) >= 5:
                confidence = 'high'
            elif len(answered_questions) >= 3:
                confidence = 'medium'
            else:
                confidence = 'low'

            await supabase_service.update_competency_assessment(
                competency_assessment_id=str(competency_assessment_id),
                ai_assessed_score=int(round(avg_score)),
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
