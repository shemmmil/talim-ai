# Руководство по миграции данных

## Миграция: Оптимизация хранения question_history

**Дата:** 2026-01-26  
**Версия:** 1.1.0  
**Файл миграции:** `optimize_question_history.sql`

---

## Что меняется?

### До миграции
```
question_history хранит:
- ✅ Вопросы и оценки
- ❌ Полные текстовые транскрипты (ЗАНИМАЮТ МНОГО МЕСТА)
- ❌ Метаданные аудио
- ❌ JSONB с дублирующимися данными
```

### После миграции
```
question_history хранит:
- ✅ Вопросы
- ✅ Только итоговые оценки (score, is_correct, feedback)
- ✅ Структурированные пробелы в знаниях
- ✅ Метрики (время ответа)
```

**Экономия:** ~90% места в базе данных

---

## Шаги миграции

### 1. Backup базы данных (ОБЯЗАТЕЛЬНО!)

```bash
# Для Supabase
# В Dashboard: Database → Backups → Create backup

# Для локальной PostgreSQL
pg_dump -h localhost -U postgres -d talim_ai > backup_$(date +%Y%m%d).sql
```

### 2. Проверить текущее состояние

```sql
-- Проверить размер таблицы ДО миграции
SELECT 
  pg_size_pretty(pg_total_relation_size('question_history')) as table_size,
  count(*) as total_records,
  count(*) FILTER (WHERE user_answer_transcript IS NOT NULL) as records_with_transcript
FROM question_history;
```

### 3. Применить миграцию

```bash
# Для Supabase: скопировать содержимое файла и выполнить в SQL Editor
# Database → SQL Editor → New Query → вставить содержимое optimize_question_history.sql

# Для локальной PostgreSQL:
psql -h localhost -U postgres -d talim_ai -f database/migrations/optimize_question_history.sql
```

### 4. Проверить результат

```sql
-- Убедиться, что данные мигрировали корректно
SELECT 
  count(*) as total,
  count(*) FILTER (WHERE score IS NOT NULL) as with_score,
  count(*) FILTER (WHERE understanding_depth IS NOT NULL) as with_depth,
  count(*) FILTER (WHERE feedback IS NOT NULL) as with_feedback
FROM question_history;

-- Все три счетчика должны быть одинаковыми
```

### 5. (Опционально) Удалить старые колонки

⚠️ **ВНИМАНИЕ:** Это действие необратимо! Данные будут потеряны.

Раскомментируйте строки в миграции:

```sql
ALTER TABLE question_history DROP COLUMN IF EXISTS user_answer_transcript;
ALTER TABLE question_history DROP COLUMN IF EXISTS audio_duration_seconds;
ALTER TABLE question_history DROP COLUMN IF EXISTS transcription_confidence;
ALTER TABLE question_history DROP COLUMN IF EXISTS ai_evaluation;
```

Или выполните вручную после подтверждения:

```sql
-- Проверьте, что больше не нужны старые данные
SELECT count(*) FROM question_history 
WHERE user_answer_transcript IS NOT NULL;

-- Если результат > 0, сделайте еще один backup!
-- Потом удалите:
ALTER TABLE question_history DROP COLUMN user_answer_transcript;
ALTER TABLE question_history DROP COLUMN audio_duration_seconds;
ALTER TABLE question_history DROP COLUMN transcription_confidence;
ALTER TABLE question_history DROP COLUMN ai_evaluation;

VACUUM FULL question_history;  -- Освободить место
```

### 6. Проверить размер таблицы ПОСЛЕ

```sql
SELECT 
  pg_size_pretty(pg_total_relation_size('question_history')) as table_size_after,
  count(*) as total_records
FROM question_history;
```

### 7. Обновить код приложения

Код уже обновлен в репозитории. Убедитесь, что используете последнюю версию:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### 8. Перезапустить сервер

```bash
# Остановить текущий процесс
# Ctrl+C

# Запустить заново
python -m app.main
```

---

## Откат миграции (если что-то пошло не так)

### Вариант 1: Восстановить из backup

```bash
# Для локальной PostgreSQL
psql -h localhost -U postgres -d talim_ai < backup_20260126.sql
```

### Вариант 2: Вернуть старые колонки

```sql
-- Добавить обратно удаленные колонки
ALTER TABLE question_history 
ADD COLUMN IF NOT EXISTS user_answer_transcript TEXT;

ALTER TABLE question_history 
ADD COLUMN IF NOT EXISTS audio_duration_seconds INTEGER;

ALTER TABLE question_history 
ADD COLUMN IF NOT EXISTS transcription_confidence FLOAT;

ALTER TABLE question_history 
ADD COLUMN IF NOT EXISTS ai_evaluation JSONB;

-- Восстановить данные из новых колонок в JSONB (если нужно)
UPDATE question_history 
SET ai_evaluation = jsonb_build_object(
  'score', score,
  'isCorrect', is_correct,
  'understandingDepth', understanding_depth,
  'feedback', feedback,
  'knowledgeGaps', knowledge_gaps
)
WHERE ai_evaluation IS NULL AND score IS NOT NULL;
```

---

## Тестирование после миграции

### 1. Создать новый assessment

```bash
curl -X POST http://localhost:8000/api/assessments \
  -H "Authorization: Bearer test-user" \
  -H "Content-Type: application/json" \
  -d '{
    "direction": "frontend",
    "technology": "react"
  }'
```

### 2. Получить вопрос и ответить

```bash
# Получить вопрос
curl -X POST http://localhost:8000/api/questions/generate \
  -H "Authorization: Bearer test-user" \
  -F "assessment_id=<assessment_id>" \
  -F "competency_id=<competency_id>" \
  -F "question_number=1"

# Отправить ответ (с аудио файлом)
curl -X POST http://localhost:8000/api/questions/answer \
  -H "Authorization: Bearer test-user" \
  -F "assessment_id=<assessment_id>" \
  -F "competency_id=<competency_id>" \
  -F "question_text=..." \
  -F "difficulty=3" \
  -F "audio=@test.webm"
```

### 3. Проверить в базе данных

```sql
-- Должны быть заполнены новые поля
SELECT 
  question_text,
  score,
  is_correct,
  understanding_depth,
  feedback,
  knowledge_gaps,
  user_answer_transcript  -- должен быть NULL
FROM question_history
ORDER BY created_at DESC
LIMIT 5;
```

---

## FAQ по миграции

### Q: Сколько времени займет миграция?

**A:** Зависит от количества данных:
- 1,000 записей: ~1-2 секунды
- 10,000 записей: ~5-10 секунд
- 100,000 записей: ~30-60 секунд

### Q: Можно ли применить миграцию на production без downtime?

**A:** Да, миграция добавляет колонки и мигрирует данные без блокировки таблицы. 
Удаление старых колонок требует короткой блокировки (~1 секунда).

**Рекомендуемый порядок для production:**

1. Применить миграцию (добавление колонок) - без downtime
2. Задеплоить новый код приложения - без downtime
3. Подождать 24 часа для проверки
4. Удалить старые колонки (шаг 5) - короткий downtime (~1 секунда)

### Q: Что делать, если миграция не работает?

1. Проверить логи PostgreSQL
2. Убедиться, что используется PostgreSQL 12+
3. Проверить права пользователя БД
4. Восстановить из backup и попробовать снова

### Q: Как проверить, что все работает?

Запустить тесты:

```bash
pytest tests/test_questions.py -v
pytest tests/test_assessments.py -v
```

---

## Контрольный чек-лист

Перед миграцией:
- [ ] Создан backup базы данных
- [ ] Проверен размер таблицы question_history
- [ ] Убедились, что PostgreSQL 12+
- [ ] Прочитали документацию

Во время миграции:
- [ ] Применен файл optimize_question_history.sql
- [ ] Проверено, что данные мигрировали (count с фильтрами)
- [ ] Нет ошибок в логах PostgreSQL

После миграции:
- [ ] Обновлен код приложения (git pull)
- [ ] Перезапущен сервер
- [ ] Создан тестовый assessment
- [ ] Проверена работа через API
- [ ] Проверен размер таблицы ПОСЛЕ (сравнить с ДО)

Опционально:
- [ ] Удалены старые колонки (необратимо!)
- [ ] Выполнен VACUUM FULL
- [ ] Обновлена документация

---

## Поддержка

Если возникли проблемы:
1. Проверьте логи: `tail -f logs/app.log`
2. Посмотрите документацию: `docs/DATA_OPTIMIZATION.md`
3. Восстановите из backup если нужно
