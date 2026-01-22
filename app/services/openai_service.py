from openai import AsyncOpenAI
import json
from typing import Optional, Dict, List
import logging
from httpx import Timeout
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, api_key: str, timeout: int = 180):
        """
        Инициализация OpenAI сервиса
        
        Args:
            api_key: API ключ OpenAI
            timeout: Таймаут для запросов в секундах (по умолчанию 180)
        """
        # Создаем таймаут: connect=10s, read=timeout, write=10s, pool=5s
        http_timeout = Timeout(
            connect=10.0,
            read=float(timeout),
            write=10.0,
            pool=5.0
        )
        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=http_timeout
        )

    async def transcribe_audio(self, audio_file_path: str, language: str = "ru") -> Dict:
        """
        Транскрибирует аудио в текст через Whisper API

        Args:
            audio_file_path: Путь к файлу аудио
            language: Язык аудио (ru, en, auto)

        Returns:
            Dict с текстом и метаданными
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language if language != "auto" else None,
                    response_format="verbose_json",
                    temperature=0
                )

            return {
                "text": transcript.text,
                "language": transcript.language,
                "duration": getattr(transcript, "duration", None),
            }

        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            error_str = str(e).lower()
            
            # Обработка ошибки квоты
            if "insufficient_quota" in error_str or "429" in error_str or "quota" in error_str:
                raise HTTPException(
                    status_code=402,
                    detail="OpenAI API quota exceeded. Please check your OpenAI account billing and increase your usage limits. "
                           "For more information, visit: https://platform.openai.com/docs/guides/error-codes/api-errors"
                ) from e
            
            raise

    async def generate_question(
        self,
        role_name: str,
        competency_name: str,
        competency_description: str,
        question_number: int,
        difficulty: int,
        previous_answers: Optional[List[Dict]] = None,
        knowledge_gaps: Optional[List[str]] = None
    ) -> Dict:
        """
        Генерирует вопрос через GPT-4

        Returns:
            Dict с вопросом и метаданными
        """
        system_prompt = """Ты эксперт по оценке технических компетенций специалистов. 
Твоя задача - генерировать вопросы для голосового собеседования, которые помогут объективно оценить уровень знаний кандидата.

Принципы создания вопросов:
1. Вопросы должны проверять ПОНИМАНИЕ, а не заученные факты
2. Кандидат будет отвечать ГОЛОСОМ (устно), поэтому вопрос должен подразумевать развернутый ответ на 1-3 минуты
3. Избегай вопросов типа "да/нет" или simple choice
4. Вопрос должен выявлять глубину понимания концепций
5. Адаптируй сложность под уровень кандидата на основе предыдущих ответов

Уровни сложности:
- 1/5: Базовые концепции, определения
- 2/5: Понимание основ, простые примеры
- 3/5: Практическое применение, типичные кейсы
- 4/5: Глубокое понимание, edge cases, оптимизация
- 5/5: Экспертный уровень, архитектурные решения, trade-offs

Всегда возвращай ответ ТОЛЬКО в JSON формате без дополнительного текста."""

        previous_answers_text = ""
        if previous_answers:
            previous_answers_text = "\n".join([
                f"Вопрос {i+1}: {ans.get('question', 'N/A')}\n"
                f"Ответ: {ans.get('answer', '')[:200]}...\n"
                f"Оценка: {ans.get('score', 0)}/5"
                for i, ans in enumerate(previous_answers)
            ])
        else:
            previous_answers_text = "Это первый вопрос по данной компетенции."

        knowledge_gaps_text = ""
        if knowledge_gaps:
            knowledge_gaps_text = f'\n\nВыявленные пробелы в знаниях: {", ".join(knowledge_gaps)}'

        user_prompt = f"""Роль: {role_name}
Компетенция: {competency_name}
Описание: {competency_description}
Текущий вопрос: {question_number} из 5
Уровень сложности: {difficulty}/5

Контекст предыдущих ответов:
{previous_answers_text}
{knowledge_gaps_text if knowledge_gaps_text else ''}

Сгенерируй ОДИН вопрос для голосового ответа, который:
1. Соответствует уровню сложности {difficulty}/5
2. Проверяет глубину понимания компетенции "{competency_name}"
{f'3. Желательно затрагивает один из пробелов: {knowledge_gaps[0] if knowledge_gaps else ""}' if knowledge_gaps else ''}

Верни JSON в формате:
{{
  "question": "текст вопроса",
  "difficulty": {difficulty},
  "expectedKeyPoints": ["ключевой момент 1", "ключевой момент 2", "ключевой момент 3"],
  "estimatedAnswerTime": "1-2 минуты"
}}"""

        try:
            logger.info(f"Generating question for competency: {competency_name}, difficulty: {difficulty}")
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=500
            )
            logger.info("Question generated successfully")

            result = json.loads(response.choices[0].message.content)

            # Валидация ответа
            required_fields = ["question", "difficulty", "expectedKeyPoints", "estimatedAnswerTime"]
            if not all(field in result for field in required_fields):
                raise ValueError("Missing required fields in AI response")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            raise
        except TimeoutError as e:
            logger.error(f"Question generation timeout: {e}")
            raise HTTPException(
                status_code=504,
                detail="Request timed out. The question generation took too long. Please try again."
            ) from e
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            error_str = str(e).lower()
            
            # Обработка ошибки квоты
            if "insufficient_quota" in error_str or "429" in error_str or "quota" in error_str:
                raise HTTPException(
                    status_code=402,
                    detail="OpenAI API quota exceeded. Please check your OpenAI account billing and increase your usage limits. "
                           "For more information, visit: https://platform.openai.com/docs/guides/error-codes/api-errors"
                ) from e
            
            # Обработка таймаута
            if "timeout" in error_str or "timed out" in error_str:
                raise HTTPException(
                    status_code=504,
                    detail="Request timed out. The question generation took too long. Please try again."
                ) from e
            
            raise

    async def evaluate_answer(
        self,
        question_text: str,
        transcript: str,
        competency_name: str,
        difficulty: int
    ) -> Dict:
        """
        Оценивает ответ кандидата через GPT-4

        Returns:
            Dict с оценкой и фидбеком
        """
        system_prompt = """Ты эксперт по оценке технических ответов кандидатов на собеседованиях.
Твоя задача - объективно оценить устный ответ кандидата, который был транскрибирован в текст.

Критерии оценки:
1. **Правильность (score 1-5)**:
   - 1: Полностью неправильный или нерелевантный ответ
   - 2: Частично правильный, много ошибок
   - 3: В целом правильный, но с недочетами
   - 4: Правильный и достаточно полный ответ
   - 5: Отличный ответ, все ключевые моменты, примеры

2. **Глубина понимания (understandingDepth)**:
   - shallow: Поверхностное понимание, общие фразы, нет конкретики
   - medium: Понимает основы, но не углубляется в детали
   - deep: Глубокое понимание, примеры из практики, нюансы

3. **Выявление пробелов**:
   - Конкретные темы/концепции, которые кандидат не знает или путает
   - Что нужно изучить дополнительно

4. **Адаптивность**:
   - Если ответ хороший (4-5) → увеличить сложность
   - Если средний (3) → оставить ту же сложность
   - Если слабый (1-2) → уменьшить сложность

5. **Правильный ответ (correctAnswer)**:
   - Должен быть развернутым и полным
   - Включать все ключевые концепции, примеры, лучшие практики
   - Написан как для учебного материала - понятно и структурированно
   - Длина: 3-7 предложений для среднего вопроса, больше для сложных

6. **Ключевые моменты (expectedKeyPoints)**:
   - Список из 3-7 ключевых концепций/моментов, которые должны быть в правильном ответе
   - Каждый пункт - короткая формулировка (1-5 слов)
   - Должны отражать основной смысл правильного ответа

Учитывай что это транскрипция устной речи - могут быть запинки, повторы, неидеальная грамматика.

Всегда возвращай ответ ТОЛЬКО в JSON формате без дополнительного текста."""

        user_prompt = f"""Компетенция: {competency_name}
Уровень сложности вопроса: {difficulty}/5

Вопрос: {question_text}

Ответ кандидата (транскрибированный из голоса):
{transcript}

Оцени ответ и верни JSON со ВСЕМИ полями (обязательно все поля должны присутствовать):
{{
  "score": 1-5,
  "understandingDepth": "shallow|medium|deep",
  "isCorrect": true|false,
  "feedback": "Краткий конструктивный фидбек для кандидата (2-3 предложения)",
  "knowledgeGaps": ["пробел 1", "пробел 2"],
  "nextDifficulty": 1-5,
  "reasoning": "Объяснение почему выставлена такая оценка",
  "correctAnswer": "Эталонный правильный ответ на вопрос. Должен быть развернутым и содержать все ключевые моменты. Минимум 3-5 предложений.",
  "expectedKeyPoints": ["ключевой момент 1", "ключевой момент 2", "ключевой момент 3"]
}}

ВАЖНО: Все поля обязательны! Не пропускай ни одно поле."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000  # Увеличено для правильного ответа и всех полей
            )

            # Логируем сырой ответ для отладки
            raw_content = response.choices[0].message.content
            logger.debug(f"Raw GPT response: {raw_content[:500]}...")  # Первые 500 символов

            try:
                result = json.loads(raw_content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from GPT response: {e}")
                logger.error(f"Raw content: {raw_content}")
                raise ValueError(f"Invalid JSON response from GPT: {str(e)}")

            # Логируем полученный результат для отладки
            logger.debug(f"GPT evaluation result keys: {list(result.keys())}")
            logger.debug(f"GPT evaluation result: {result}")

            # Валидация обязательных полей (только критически важные)
            required_fields = ["score", "understandingDepth", "isCorrect",
                             "feedback", "knowledgeGaps", "nextDifficulty"]
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                logger.error(f"Missing required fields in evaluation: {missing_fields}")
                logger.error(f"Full result: {result}")
                logger.error(f"Response content: {response.choices[0].message.content}")
                raise ValueError(f"Missing required fields in evaluation: {missing_fields}")

            # Нормализация и значения по умолчанию для всех полей
            # Убеждаемся, что knowledgeGaps это список
            if not isinstance(result.get("knowledgeGaps"), list):
                result["knowledgeGaps"] = []

            # Убеждаемся, что expectedKeyPoints это список
            if "expectedKeyPoints" not in result or not isinstance(result.get("expectedKeyPoints"), list):
                result["expectedKeyPoints"] = []

            # Убеждаемся, что correctAnswer есть (если нет, генерируем базовый)
            if "correctAnswer" not in result or not result.get("correctAnswer"):
                result["correctAnswer"] = "Правильный ответ не был сгенерирован."

            # Убеждаемся, что reasoning есть (опциональное поле)
            if "reasoning" not in result:
                result["reasoning"] = None

            # Валидация типов
            if not isinstance(result.get("score"), int) or result.get("score") < 1 or result.get("score") > 5:
                logger.warning(f"Invalid score: {result.get('score')}, setting to 3")
                result["score"] = 3

            if result.get("understandingDepth") not in ["shallow", "medium", "deep"]:
                logger.warning(f"Invalid understandingDepth: {result.get('understandingDepth')}, setting to 'medium'")
                result["understandingDepth"] = "medium"

            if not isinstance(result.get("isCorrect"), bool):
                logger.warning(f"Invalid isCorrect: {result.get('isCorrect')}, setting to False")
                result["isCorrect"] = False

            if not isinstance(result.get("nextDifficulty"), int) or result.get("nextDifficulty") < 1 or result.get("nextDifficulty") > 5:
                logger.warning(f"Invalid nextDifficulty: {result.get('nextDifficulty')}, setting to 3")
                result["nextDifficulty"] = 3

            return result

        except TimeoutError as e:
            logger.error(f"Answer evaluation timeout: {e}")
            raise HTTPException(
                status_code=504,
                detail="Request timed out. The answer evaluation took too long. Please try again."
            ) from e
        except Exception as e:
            logger.error(f"Answer evaluation error: {e}")
            error_str = str(e).lower()
            
            # Обработка ошибки квоты
            if "insufficient_quota" in error_str or "429" in error_str or "quota" in error_str:
                raise HTTPException(
                    status_code=402,
                    detail="OpenAI API quota exceeded. Please check your OpenAI account billing and increase your usage limits. "
                           "For more information, visit: https://platform.openai.com/docs/guides/error-codes/api-errors"
                ) from e
            
            # Обработка таймаута
            if "timeout" in error_str or "timed out" in error_str:
                raise HTTPException(
                    status_code=504,
                    detail="Request timed out. The answer evaluation took too long. Please try again."
                ) from e
            
            raise

    async def determine_competencies_by_direction(self, direction: str) -> Dict:
        """
        Определяет компетенции для тестирования по тексту направления
        
        Args:
            direction: Текст направления, например "backend(golang, sql)"
        
        Returns:
            Dict с массивом компетенций
        """
        system_prompt = """Ты эксперт по определению технических компетенций для тестирования специалистов.
Твоя задача - определить список ключевых компетенций для тестирования на основе направления.

Компетенция должна быть:
- Конкретной и измеримой
- Релевантной для указанного направления
- Подходящей для голосового тестирования (можно проверить понимание устно)

Всегда возвращай ответ ТОЛЬКО в JSON формате без дополнительного текста."""

        user_prompt = f"""Направление: {direction}

Определи 5-7 ключевых компетенций для тестирования специалиста в этом направлении.

Верни JSON в формате:
{{
  "competencies": [
    {{
      "name": "Название компетенции",
      "description": "Краткое описание что проверяет эта компетенция",
      "category": "Категория (например, 'Языки программирования', 'Базы данных', 'Архитектура')"
    }}
  ]
}}"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.5,
                max_tokens=1000
            )

            result = json.loads(response.choices[0].message.content)
            
            # Валидация
            if "competencies" not in result or not isinstance(result["competencies"], list):
                raise ValueError("Invalid response format: missing competencies array")
            
            return result

        except Exception as e:
            logger.error(f"Error determining competencies: {e}")
            error_str = str(e).lower()
            
            # Обработка ошибки квоты
            if "insufficient_quota" in error_str or "429" in error_str or "quota" in error_str:
                raise HTTPException(
                    status_code=402,
                    detail="OpenAI API quota exceeded. Please check your OpenAI account billing and increase your usage limits. "
                           "For more information, visit: https://platform.openai.com/docs/guides/error-codes/api-errors"
                ) from e
            
            raise

    async def generate_roadmap(
        self,
        role_name: str,
        assessment_results: List[Dict]
    ) -> Dict:
        """
        Генерирует персональный roadmap через GPT-4

        Returns:
            Dict с roadmap структурой
        """
        system_prompt = """Ты эксперт по построению персональных планов обучения для IT-специалистов.
Твоя задача - создать детальный roadmap на основе результатов тестирования.

Принципы создания roadmap:
1. **Приоритизация**: Сначала критичные пробелы, затем улучшение сильных сторон
2. **Реалистичность**: Учитывай время на изучение (часы/недели)
3. **Баланс**: Теория + практика + самопроверка
4. **Качественные материалы**: Ссылки на проверенные ресурсы (документация, курсы, статьи)
5. **Прогрессия**: От простого к сложному

Структура roadmap:
- Секции по компетенциям (в порядке приоритета)
- Для каждой секции: теория, практические задачи, вопросы для самопроверки
- Материалы на русском и английском
- Бесплатные и платные варианты

Всегда возвращай ответ ТОЛЬКО в JSON формате без дополнительного текста."""

        user_prompt = f"""Роль: {role_name}

Результаты тестирования:
{json.dumps(assessment_results, indent=2, ensure_ascii=False)}

Создай детальный персональный roadmap в JSON формате:
{{
  "title": "План развития для {role_name}",
  "description": "Краткое описание плана",
  "estimatedDurationWeeks": 8-16,
  "sections": [
    {{
      "competency": "название компетенции",
      "currentScore": 2,
      "targetScore": 5,
      "priority": "high|medium|low",
      "description": "Что нужно изучить и почему",
      "topics": ["конкретная тема 1", "тема 2", "тема 3"],
      "estimatedHours": 20,
      "learningMaterials": [
        {{
          "type": "article|video|book|course|documentation|tutorial",
          "title": "Название материала",
          "url": "https://...",
          "description": "Что даст этот материал",
          "author": "автор (опционально)",
          "language": "ru|en",
          "isFree": true|false,
          "difficulty": "beginner|intermediate|advanced",
          "estimatedHours": 2
        }}
      ],
      "practiceTasks": [
        {{
          "title": "Название задачи",
          "description": "Детальное описание что нужно сделать",
          "taskType": "coding|quiz|project|case_study",
          "difficulty": 3,
          "estimatedHours": 4,
          "requirements": {{
            "description": "Требования к выполнению",
            "acceptanceCriteria": ["критерий 1", "критерий 2"],
            "hints": ["подсказка 1", "подсказка 2"]
          }}
        }}
      ],
      "selfCheckQuestions": [
        {{
          "question": "Вопрос для самопроверки",
          "questionType": "open_ended|multiple_choice",
          "correctAnswer": "Правильный ответ или ключевые моменты",
          "explanation": "Почему это правильный ответ"
        }}
      ]
    }}
  ]
}}

Требования:
1. Минимум 5 секций (по ключевым компетенциям)
2. Для каждой секции: минимум 3 материала, 2 задачи, 3 вопроса
3. Приоритизируй компетенции с низкими оценками
4. Включай как бесплатные, так и платные материалы
5. Материалы должны быть актуальными (2023-2024)"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.5,
                max_tokens=4000
            )

            result = json.loads(response.choices[0].message.content)

            return result

        except Exception as e:
            logger.error(f"Roadmap generation error: {e}")
            error_str = str(e).lower()
            
            # Обработка ошибки квоты
            if "insufficient_quota" in error_str or "429" in error_str or "quota" in error_str:
                raise HTTPException(
                    status_code=402,
                    detail="OpenAI API quota exceeded. Please check your OpenAI account billing and increase your usage limits. "
                           "For more information, visit: https://platform.openai.com/docs/guides/error-codes/api-errors"
                ) from e
            
            raise
