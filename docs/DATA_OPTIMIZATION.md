# Оптимизация хранения данных

## Обзор

Начиная с версии 1.1.0, система Talim AI оптимизирована для эффективного хранения данных. 
Мы **НЕ храним текстовые транскрипты ответов пользователей**, а сохраняем только:
- Итоговые оценки (баллы)
- Результаты (правильно/неправильно)
- Краткий фидбек
- Выявленные пробелы в знаниях

## Преимущества

### 1. Экономия места
- **Было:** ~25KB на assessment (50 вопросов × 500 символов транскрипта)
- **Стало:** ~2KB на assessment (только структурированные данные)
- **Экономия:** 90% места в базе данных

### 2. Приватность
- Не храним дословные ответы пользователей
- Только агрегированные результаты и оценки
- GDPR compliance из коробки

### 3. Производительность
- Быстрее запросы к БД
- Меньше трафика
- Упрощенные индексы

## Структура данных

### До оптимизации (deprecated)

```sql
question_history:
  - user_answer_transcript TEXT         -- ❌ 100-1000 символов
  - audio_duration_seconds INTEGER      -- ❌ Не используется
  - transcription_confidence FLOAT      -- ❌ Не используется
  - ai_evaluation JSONB                 -- ❌ Дублирует данные
```

### После оптимизации (текущая)

```sql
question_history:
  - score INTEGER (1-5)                 -- ✅ Итоговый балл
  - is_correct BOOLEAN                  -- ✅ Правильно/неправильно
  - understanding_depth VARCHAR(20)     -- ✅ shallow/medium/deep
  - feedback TEXT                       -- ✅ Краткий фидбек (2-3 предложения)
  - knowledge_gaps TEXT[]               -- ✅ Массив пробелов в знаниях
```

## Что хранится на каждом уровне

### Уровень 1: Assessment (сессия тестирования)
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "direction_id": "uuid",
  "technology_id": "uuid",
  "status": "completed",
  "overall_score": 3.8,
  "attempt_number": 1,
  "started_at": "2026-01-26T10:00:00Z",
  "completed_at": "2026-01-26T10:45:00Z"
}
```
**Хранится:** Вся история попыток пользователя

---

### Уровень 2: Competency Assessment (оценка по компетенции)
```json
{
  "id": "uuid",
  "assessment_id": "uuid",
  "competency_id": "uuid",
  "ai_assessed_score": 4,
  "confidence_level": "high",
  "gap_analysis": {
    "knowledgeGaps": ["React hooks lifecycle", "useEffect dependencies"]
  },
  "test_session_data": {
    "questionsCount": 5,
    "answeredCount": 5,
    "averageScore": 3.8
  }
}
```
**Хранится:** Агрегированные результаты по каждой компетенции

---

### Уровень 3: Question History (детальная история вопросов)
```json
{
  "id": "uuid",
  "competency_assessment_id": "uuid",
  "question_id": "uuid",
  "question_text": "Объясните разницу между useMemo и useCallback",
  "difficulty_level": 3,
  
  // ⭐ Только оценки и результаты (NO TRANSCRIPT!)
  "score": 4,
  "is_correct": true,
  "understanding_depth": "deep",
  "feedback": "Отличное понимание разницы между хуками. Хорошо объяснил use cases.",
  "knowledge_gaps": [],
  
  "time_spent_seconds": 120,
  "asked_at": "2026-01-26T10:15:00Z",
  "answered_at": "2026-01-26T10:17:00Z"
}
```
**Хранится:** Детальные оценки по каждому вопросу (БЕЗ текста ответа)

---

## Миграция данных

### Шаг 1: Применить миграцию схемы

```bash
# Применить миграцию
psql -h your-supabase-host -U postgres -d postgres -f database/migrations/optimize_question_history.sql
```

### Шаг 2: Обновить код приложения

Код уже обновлен в:
- ✅ `app/services/supabase_service.py` - метод `update_question_history()`
- ✅ `app/api/questions.py` - обработка ответов
- ✅ `app/services/assessment_service.py` - работа с историей

### Шаг 3: Проверить работу

```bash
# Запустить сервер
python -m app.main

# Создать тестовый assessment
curl -X POST http://localhost:8000/api/assessments \
  -H "Authorization: Bearer test-user-id" \
  -H "Content-Type: application/json" \
  -d '{"direction": "frontend", "technology": "react"}'

# Проверить, что данные сохраняются корректно
```

## API Changes

### ⚠️ Breaking Changes

#### Метод: `update_question_history()`

**Было:**
```python
await supabase_service.update_question_history(
    question_id=question_id,
    user_answer_transcript=transcript,  # ❌ Больше не используется
    audio_duration_seconds=45,           # ❌ Больше не используется
    ai_evaluation={...}                  # ❌ Deprecated (но работает)
)
```

**Стало:**
```python
await supabase_service.update_question_history(
    question_id=question_id,
    score=4,                             # ✅ Обязательно
    is_correct=True,                     # ✅ Обязательно
    understanding_depth="deep",          # ✅ Обязательно
    feedback="Отличный ответ!",          # ✅ Обязательно
    knowledge_gaps=["gap1", "gap2"]      # ✅ Обязательно
)
```

#### Обратная совместимость

Старый способ с `ai_evaluation` **всё ещё работает** - данные автоматически извлекаются:

```python
# Работает для обратной совместимости
await supabase_service.update_question_history(
    question_id=question_id,
    ai_evaluation={
        "score": 4,
        "isCorrect": True,
        "understandingDepth": "deep",
        "feedback": "...",
        "knowledgeGaps": [...]
    }
)
```

## Что делать, если нужны транскрипты?

### Вариант 1: Логирование для отладки

Добавить временное логирование в development окружении:

```python
# app/api/questions.py
if settings.environment == "development":
    logger.debug(f"User transcript: {transcription['text'][:200]}...")
```

### Вариант 2: Отдельная таблица для аудита

Если нужно хранить транскрипты для аудита:

```sql
CREATE TABLE question_transcripts_audit (
  id UUID PRIMARY KEY,
  question_history_id UUID REFERENCES question_history(id),
  transcript TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '7 days')
);

-- Автоудаление через 7 дней
CREATE EXTENSION IF NOT EXISTS pg_cron;
SELECT cron.schedule(
  'cleanup-transcripts',
  '0 4 * * *',
  'DELETE FROM question_transcripts_audit WHERE expires_at < NOW()'
);
```

## Проверка экономии места

### Запрос для проверки размера таблицы:

```sql
SELECT 
  pg_size_pretty(pg_total_relation_size('question_history')) as table_size,
  pg_size_pretty(pg_relation_size('question_history')) as data_size,
  pg_size_pretty(pg_total_relation_size('question_history') - pg_relation_size('question_history')) as indexes_size,
  count(*) as total_records
FROM question_history;
```

### Ожидаемые результаты:

| Метрика | До оптимизации | После оптимизации | Экономия |
|---------|----------------|-------------------|----------|
| Размер записи | ~1-2 KB | ~150-300 bytes | 85-90% |
| Индексы | Сложные | Простые | 50% |
| Запросы | Медленнее | Быстрее | 2-3x |

## FAQ

### Q: Можно ли восстановить старые транскрипты?

**A:** Нет, старые транскрипты будут удалены после применения миграции (шаг 3). 
Сделайте backup перед миграцией, если нужны данные для анализа.

### Q: Как это влияет на фронтенд?

**A:** Фронтенд получает те же данные в ответе `/api/questions/answer`:
```json
{
  "transcript": "...",  // ✅ Возвращается в ответе, но не сохраняется в БД
  "evaluation": {
    "score": 4,
    "isCorrect": true,
    "feedback": "...",
    // ... остальные поля
  }
}
```

### Q: Что делать с существующими assessments?

**A:** Они продолжат работать. Миграция автоматически переносит данные из `ai_evaluation` JSONB 
в новые структурированные поля.

## Заключение

Новая структура данных:
- ✅ Экономит 90% места в БД
- ✅ Повышает производительность
- ✅ Улучшает приватность
- ✅ Упрощает аналитику
- ✅ Сохраняет всю важную информацию

**При этом теряем:**
- ❌ Полные текстовые транскрипты ответов
- ❌ Возможность пересмотра оценок вручную

Но для большинства случаев **итоговый балл и фидбек важнее полного транскрипта**.
