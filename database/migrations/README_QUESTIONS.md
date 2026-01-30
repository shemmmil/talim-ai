# Добавление вопросов в базу данных

## Проблема: "noMoreQuestions": true

Если при запросе вопроса вы получаете `"noMoreQuestions": true`, это значит что **в базе данных нет вопросов для этой компетенции**.

---

## Решение: Применить seed скрипты

### Шаг 1: Определить технологию

Посмотрите, какая технология используется в вашем assessment:
- **React** → используйте `seed_react_questions.sql`
- **Angular** → используйте `seed_angular_questions.sql` (если есть)
- **Vue** → создайте свой seed или используйте существующий

### Шаг 2: Применить скрипт в Supabase

#### Для React:

```sql
-- 1. Открыть Supabase Dashboard
-- 2. Перейти в SQL Editor
-- 3. Скопировать содержимое файла seed_react_questions.sql
-- 4. Выполнить (Run)
```

#### Для Angular:

```sql
-- ВАЖНО: Сначала применить компетенции (если еще не применили)
-- 1. Выполнить seed_angular_competencies.sql
-- 2. Затем выполнить seed_angular_questions.sql

-- В SQL Editor:
-- Скопировать содержимое seed_angular_questions.sql
-- Выполнить (Run)
```

#### Или через CLI:

```bash
# React
supabase db execute -f database/migrations/seed_react_questions.sql

# Angular (сначала компетенции, потом вопросы)
supabase db execute -f database/migrations/seed_angular_competencies.sql
supabase db execute -f database/migrations/seed_angular_questions.sql

# Или через psql
psql -h your-host -U postgres -d postgres -f database/migrations/seed_react_questions.sql
psql -h your-host -U postgres -d postgres -f database/migrations/seed_angular_questions.sql
```

---

## Проверка

После выполнения скрипта проверьте:

```sql
-- ДЛЯ REACT:
SELECT 
  c.name as competency,
  COUNT(q.id) as questions_count,
  MIN(q.difficulty) as min_difficulty,
  MAX(q.difficulty) as max_difficulty
FROM competencies c
LEFT JOIN questions q ON q.competency_id = c.id
WHERE c.name IN (
  'React Basics', 'React Hooks', 'React Router', 
  'State Management', 'React Performance', 'Testing React'
)
GROUP BY c.name
ORDER BY c.name;

-- ДЛЯ ANGULAR:
SELECT 
  c.name as competency,
  COUNT(q.id) as questions_count,
  MIN(q.difficulty) as min_difficulty,
  MAX(q.difficulty) as max_difficulty
FROM competencies c
LEFT JOIN questions q ON q.competency_id = c.id
WHERE c.name IN (
  'Angular Basics', 'TypeScript', 'Angular Components', 
  'Angular Services & DI', 'Angular Routing', 'RxJS',
  'Angular Forms', 'Angular HTTP', 'Angular State Management',
  'Angular Testing', 'Angular Performance', 'Angular CLI'
)
GROUP BY c.name
ORDER BY c.name;
```

**Ожидаемый результат для React:**
```
competency         | questions_count | min_difficulty | max_difficulty
-------------------+-----------------+----------------+---------------
React Basics       |               8 |              1 |              5
React Hooks        |               8 |              1 |              5
React Performance  |               6 |              2 |              5
React Router       |               7 |              1 |              5
State Management   |               7 |              1 |              5
Testing React      |               7 |              1 |              5
```

**Ожидаемый результат для Angular:**
```
competency               | questions_count | min_difficulty | max_difficulty
------------------------+-----------------+----------------+---------------
Angular Basics          |               8 |              1 |              5
Angular CLI             |               6 |              2 |              5
Angular Components      |               8 |              1 |              5
Angular Forms           |               7 |              2 |              5
Angular HTTP            |               6 |              2 |              5
Angular Performance     |               6 |              3 |              5
Angular Routing         |               7 |              2 |              5
Angular Services & DI   |               7 |              1 |              5
Angular State Management|               6 |              3 |              5
Angular Testing         |               6 |              2 |              5
RxJS                    |               8 |              2 |              5
TypeScript              |               7 |              1 |              5
```

---

## Доступные seed скрипты

### ✅ React (готов)
- **Файл:** `seed_react_questions.sql`
- **Компетенции:** 6 (React Basics, React Hooks, React Router, State Management, React Performance, Testing React)
- **Вопросов:** ~43
- **Уровни сложности:** 1-5

### ✅ Angular (готов)
- **Файл компетенций:** `seed_angular_competencies.sql`
- **Файл вопросов:** `seed_angular_questions.sql` ⭐ NEW!
- **Компетенции:** 12 (Angular Basics, TypeScript, Components, Services & DI, Routing, RxJS, Forms, HTTP, State Management, Testing, Performance, CLI)
- **Вопросов:** ~78
- **Уровни сложности:** 1-5

### ❌ Vue, Svelte, etc.
- Нужно создать свои seed файлы

---

## Создание своих вопросов

### Шаблон для новых вопросов:

```sql
INSERT INTO questions (competency_id, question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
SELECT 
  c.id,
  'Ваш вопрос здесь?',
  3,  -- Сложность 1-5
  1,  -- Номер вопроса 1-5
  '["Ключевой момент 1", "Ключевой момент 2", "Ключевой момент 3"]'::jsonb,
  '2-3 минуты'
FROM competencies c
WHERE c.name = 'Название компетенции'
ON CONFLICT DO NOTHING;
```

### Рекомендации:

1. **Сложность (difficulty):**
   - 1 = Базовые концепции, определения
   - 2 = Понимание основ, простые примеры
   - 3 = Практическое применение
   - 4 = Глубокое понимание, edge cases
   - 5 = Экспертный уровень, архитектура

2. **Ключевые моменты (expected_key_points):**
   - 3-5 пунктов
   - Короткие формулировки
   - Что должно быть в правильном ответе

3. **Время ответа:**
   - 1-2 минуты для простых вопросов
   - 3-4 минуты для средних
   - 4-5 минут для сложных

4. **Question number:**
   - 1-5 для каждого уровня сложности
   - Можно использовать NULL для любого номера

---

## Структура данных

```
competencies (компетенции)
  ├── id
  ├── name (React Basics, React Hooks, ...)
  └── questions (вопросы)
      ├── id
      ├── competency_id
      ├── question_text
      ├── difficulty (1-5)
      ├── question_number (1-5 или NULL)
      ├── expected_key_points (JSONB массив)
      ├── estimated_answer_time
      └── used_count (счетчик использования)
```

---

## Автоматическая генерация вопросов (будущее)

В будущем планируется:
- Автоматическая генерация вопросов через GPT-4
- API endpoint для добавления вопросов
- Админ панель для управления вопросами

Пока используйте SQL seed скрипты.

---

## Troubleshooting

### Q: Вопросы не появляются после добавления
**A:** Проверьте:
1. Название компетенции совпадает **точно** (case-sensitive)
2. Компетенция привязана к технологии через `technology_competencies`
3. Выполните проверочный запрос выше

### Q: "noMoreQuestions": true даже после добавления вопросов
**A:** Возможные причины:
1. Все вопросы уже использованы в текущем assessment
2. Не найдены вопросы для указанной сложности
3. Не найдены вопросы для указанного question_number

**Решение:** Добавьте больше вопросов или попробуйте другую сложность.

### Q: Как очистить историю использования вопросов?
**A:** 
```sql
-- Сбросить счетчик использования
UPDATE questions SET used_count = 0;

-- Или удалить историю для конкретного assessment
DELETE FROM question_history 
WHERE competency_assessment_id IN (
  SELECT id FROM competency_assessments 
  WHERE assessment_id = 'your-assessment-id'
);
```

---

## Полезные команды

```sql
-- Посмотреть все вопросы для компетенции
SELECT 
  question_text, 
  difficulty, 
  question_number,
  used_count
FROM questions q
JOIN competencies c ON c.id = q.competency_id
WHERE c.name = 'React Basics'
ORDER BY difficulty, question_number;

-- Посмотреть сколько раз использовался каждый вопрос
SELECT 
  c.name,
  AVG(q.used_count)::int as avg_usage,
  MIN(q.used_count) as min_usage,
  MAX(q.used_count) as max_usage
FROM questions q
JOIN competencies c ON c.id = q.competency_id
GROUP BY c.name
ORDER BY avg_usage DESC;

-- Найти вопросы без ключевых моментов
SELECT 
  c.name,
  q.question_text,
  q.difficulty
FROM questions q
JOIN competencies c ON c.id = q.competency_id
WHERE q.expected_key_points IS NULL 
   OR jsonb_array_length(q.expected_key_points) = 0;
```

---

**После применения seed скрипта перезапустите сервер и попробуйте снова!**
