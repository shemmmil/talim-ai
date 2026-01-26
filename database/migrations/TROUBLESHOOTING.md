# Решение проблем с выполнением SQL скриптов

## Ошибка "Failed to fetch (api.supabase.com)"

Эта ошибка обычно означает проблему с сетью или API, а не с SQL синтаксисом.

### Быстрая диагностика

1. **Проверьте подключение:**
   ```sql
   SELECT 1 as test;
   ```

2. **Проверьте существование таблиц:**
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
     AND table_name IN ('competencies', 'questions', 'directions', 'technologies');
   ```

3. **Проверьте существование компетенций:**
   ```sql
   SELECT id, name FROM competencies 
   WHERE name IN ('React Basics', 'Go Basics') 
   LIMIT 5;
   ```

### Решение проблем

#### Проблема 1: Скрипт слишком большой

**Решение:** Выполняйте скрипт по частям или используйте `seed_questions_fixed.sql` (использует функцию)

#### Проблема 2: Ошибка сети/таймаут

**Решения:**
- Выполняйте скрипт в Supabase Dashboard SQL Editor (не через API)
- Разбейте скрипт на меньшие части
- Используйте транзакции для группировки операций

#### Проблема 3: Компетенции не найдены

**Проверка:**
```sql
-- Проверьте, что компетенции созданы
SELECT COUNT(*) as count FROM competencies;
SELECT name FROM competencies WHERE name LIKE '%React%' OR name LIKE '%Go%';
```

**Решение:** Сначала выполните `seed_competencies.sql`

### Альтернативный подход: Пошаговое выполнение

#### Шаг 1: Проверка данных
```sql
-- Проверьте компетенции
SELECT id, name FROM competencies WHERE name = 'React Basics';
```

#### Шаг 2: Создание одного вопроса вручную
```sql
-- Замените {COMPETENCY_ID} на ID из шага 1
INSERT INTO questions (
  competency_id, 
  question_text, 
  difficulty, 
  question_number, 
  expected_key_points, 
  estimated_answer_time
)
VALUES (
  '{COMPETENCY_ID}',  -- Вставьте реальный UUID
  'Объясните, что такое компоненты в React?',
  1,
  1,
  '["Компоненты", "Переиспользование", "JSX"]'::jsonb,
  '2-3 минуты'
);
```

#### Шаг 3: Проверка
```sql
SELECT q.*, c.name as competency_name
FROM questions q
JOIN competencies c ON q.competency_id = c.id
WHERE c.name = 'React Basics';
```

### Использование исправленной версии

Используйте `seed_questions_fixed.sql` - он:
- Использует функцию для более надежного выполнения
- Логирует каждый шаг
- Пропускает существующие вопросы
- Легче отлаживать

### Если ничего не помогает

1. **Выполняйте через Supabase Dashboard** (не через API клиент)
2. **Используйте простые INSERT без подзапросов:**
   ```sql
   -- Сначала получите ID компетенции
   SELECT id FROM competencies WHERE name = 'React Basics';
   
   -- Затем вставьте вопрос с этим ID
   INSERT INTO questions (competency_id, question_text, difficulty, question_number, ...)
   VALUES ('uuid-here', 'question text', 1, 1, ...);
   ```

3. **Проверьте логи Supabase Dashboard → Logs**

### Контакты для поддержки

Если проблема сохраняется:
- Проверьте статус Supabase: https://status.supabase.com
- Проверьте логи проекта в Supabase Dashboard
- Убедитесь, что у вас есть права на выполнение SQL
