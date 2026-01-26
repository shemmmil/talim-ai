-- Упрощенная версия скрипта для тестирования
-- Выполняйте по частям, чтобы найти проблему

-- ============================================
-- ШАГ 1: Проверка существования компетенций
-- ============================================

-- Проверьте, что компетенции существуют
SELECT 'Checking competencies...' as step;
SELECT id, name FROM competencies WHERE name IN ('React Basics', 'React Hooks', 'Go Basics') ORDER BY name;

-- ============================================
-- ШАГ 2: Создание одного вопроса для теста
-- ============================================

-- Создайте один вопрос вручную для проверки
-- Замените {COMPETENCY_ID} на реальный ID из шага 1
/*
INSERT INTO questions (competency_id, question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
VALUES (
  '{COMPETENCY_ID}',  -- Замените на реальный ID
  'Объясните, что такое компоненты в React и как они работают.',
  1,
  1,
  '["Компоненты как переиспользуемые блоки UI", "Функциональные компоненты", "Классовые компоненты"]'::jsonb,
  '2-3 минуты'
);
*/

-- ============================================
-- ШАГ 3: Проверка созданного вопроса
-- ============================================

SELECT 'Checking questions...' as step;
SELECT 
  q.id,
  q.question_text,
  q.difficulty,
  q.question_number,
  c.name as competency_name
FROM questions q
JOIN competencies c ON q.competency_id = c.id
LIMIT 10;

-- ============================================
-- ШАГ 4: Полная версия (выполняйте только если шаги 1-3 работают)
-- ============================================

-- React Basics - вопрос 1
DO $$
DECLARE
  comp_id UUID;
BEGIN
  -- Находим ID компетенции
  SELECT id INTO comp_id FROM competencies WHERE name = 'React Basics' LIMIT 1;
  
  IF comp_id IS NOT NULL THEN
    -- Создаем вопрос, если его еще нет
    INSERT INTO questions (competency_id, question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
    SELECT 
      comp_id,
      'Объясните, что такое компоненты в React и как они работают. В чем разница между функциональными и классовыми компонентами?',
      1,
      1,
      '["Компоненты как переиспользуемые блоки UI", "Функциональные компоненты с хуками", "Классовые компоненты с lifecycle методами"]'::jsonb,
      '2-3 минуты'
    WHERE NOT EXISTS (
      SELECT 1 FROM questions 
      WHERE competency_id = comp_id 
        AND difficulty = 1 
        AND question_number = 1
    );
    
    RAISE NOTICE 'Question created for React Basics (difficulty=1, number=1)';
  ELSE
    RAISE NOTICE 'Competency "React Basics" not found!';
  END IF;
END $$;

-- Проверка
SELECT 'React Basics questions:' as info;
SELECT 
  c.name as competency,
  q.question_text,
  q.difficulty,
  q.question_number
FROM questions q
JOIN competencies c ON q.competency_id = c.id
WHERE c.name = 'React Basics'
ORDER BY q.difficulty, q.question_number;
