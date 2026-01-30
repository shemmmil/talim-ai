-- Миграция: Оптимизация question_history - убираем избыточные данные
-- Дата: 2026-01-26
-- Описание: Удаляем текстовые транскрипты, храним только оценки и результаты

-- Шаг 1: Добавляем новые колонки для структурированных данных
ALTER TABLE question_history 
ADD COLUMN IF NOT EXISTS score INTEGER CHECK (score BETWEEN 1 AND 5);

ALTER TABLE question_history 
ADD COLUMN IF NOT EXISTS understanding_depth VARCHAR(20) 
CHECK (understanding_depth IN ('shallow', 'medium', 'deep'));

ALTER TABLE question_history 
ADD COLUMN IF NOT EXISTS feedback TEXT;

ALTER TABLE question_history 
ADD COLUMN IF NOT EXISTS knowledge_gaps TEXT[];

-- Шаг 2: Мигрируем данные из ai_evaluation JSONB в отдельные колонки
UPDATE question_history 
SET 
  score = (ai_evaluation->>'score')::INTEGER,
  understanding_depth = ai_evaluation->>'understandingDepth',
  feedback = ai_evaluation->>'feedback',
  knowledge_gaps = ARRAY(
    SELECT jsonb_array_elements_text(ai_evaluation->'knowledgeGaps')
  )
WHERE ai_evaluation IS NOT NULL
  AND score IS NULL;

-- Шаг 3: Удаляем избыточные колонки (осторожно - данные будут потеряны!)
-- ⚠️ Раскомментируйте только после подтверждения, что миграция данных прошла успешно

-- ALTER TABLE question_history DROP COLUMN IF EXISTS user_answer_transcript;
-- ALTER TABLE question_history DROP COLUMN IF EXISTS audio_duration_seconds;
-- ALTER TABLE question_history DROP COLUMN IF EXISTS transcription_confidence;
-- ALTER TABLE question_history DROP COLUMN IF EXISTS ai_evaluation;

-- Шаг 4: Делаем score обязательным для новых записей
-- ALTER TABLE question_history ALTER COLUMN score SET NOT NULL;

-- Шаг 5: Создаем индексы для производительности
CREATE INDEX IF NOT EXISTS idx_question_history_score 
ON question_history(score) 
WHERE score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_question_history_is_correct 
ON question_history(is_correct) 
WHERE is_correct IS NOT NULL;

-- Шаг 6: Добавляем комментарии к колонкам
COMMENT ON COLUMN question_history.score IS 'Итоговый балл AI оценки (1-5)';
COMMENT ON COLUMN question_history.understanding_depth IS 'Глубина понимания: shallow, medium, deep';
COMMENT ON COLUMN question_history.feedback IS 'Краткий конструктивный фидбек (2-3 предложения)';
COMMENT ON COLUMN question_history.knowledge_gaps IS 'Массив выявленных пробелов в знаниях';

-- Проверка: сколько места освободилось
-- SELECT 
--   pg_size_pretty(pg_total_relation_size('question_history')) as table_size,
--   count(*) as total_records
-- FROM question_history;
