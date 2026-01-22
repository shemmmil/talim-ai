# Порядок выполнения миграций

## Важно: Сначала примените базовую схему

Перед выполнением миграций убедитесь, что базовая схема из `database/schema.sql` уже применена. Она содержит все основные таблицы:
- `users`, `roles`, `competencies`
- `assessments`, `competency_assessments`
- `question_history`
- и другие базовые таблицы

## Порядок выполнения миграций

Выполняйте миграции **строго в следующем порядке**:

### 1. `add_directions_table.sql`
**Зависимости:** Требует существования таблиц `competencies` и `assessments`

**Что делает:**
- Создает таблицу `directions` (направления разработки)
- Создает таблицу `direction_competencies` (связь направлений и компетенций)
- Добавляет колонку `direction_id` в таблицу `assessments`
- Создает индексы

**Почему первой:** Создает базовую структуру для направлений, которая нужна для технологий

---

### 2. `add_technologies_table.sql`
**Зависимости:** Требует существования таблиц `directions`, `competencies` и `assessments`

**Что делает:**
- Создает таблицу `technologies` (технологии/стек)
- Создает таблицу `direction_technologies` (связь направлений и технологий)
- Создает таблицу `technology_competencies` (связь технологий и компетенций)
- Добавляет колонку `technology_id` в таблицу `assessments`
- Создает индексы

**Почему второй:** Зависит от `directions`, созданной в первой миграции

---

### 3. `add_questions_table.sql`
**Зависимости:** Требует существования таблиц `competencies` и `question_history`

**Что делает:**
- Создает таблицу `questions` (предварительно сгенерированные вопросы)
- Добавляет колонку `question_id` в таблицу `question_history`
- Создает индексы

**Почему третьей:** Независима от направлений/технологий, но может выполняться в любом порядке после базовой схемы

---

## Опциональные скрипты

### `seed_technologies.sql` ⭐ РЕКОМЕНДУЕТСЯ
**Когда выполнять:** После всех миграций, для заполнения направлениями и технологиями

**Что делает:**
- Создает направления: Frontend, Backend, Fullstack, Mobile, DevOps, Data Science, QA
- Создает технологии для каждого направления:
  - Frontend: React, Vue, Angular, Svelte, Next.js, Nuxt.js
  - Backend: Go, PHP, Python, Node.js, Java, C#, Rust, Ruby
  - Mobile: React Native, Flutter, Swift, Kotlin, Ionic
  - DevOps: Docker, Kubernetes, Terraform, Ansible, Jenkins
  - Data Science: Python, R, SQL, Pandas, TensorFlow
- Связывает технологии с направлениями
- Выводит статистику созданных данных

### `seed_competencies.sql` ⭐ ОБЯЗАТЕЛЬНО
**Когда выполнять:** После `seed_technologies.sql`, для создания компетенций

**Что делает:**
- Создает компетенции для технологий:
  - React: React Basics, Hooks, Router, State Management и т.д.
  - Vue: Vue Basics, Composition API, Router, Vuex/Pinia и т.д.
  - Go: Go Basics, Concurrency, Web Development, Testing и т.д.
  - PHP: PHP Basics, OOP, Frameworks, Database, Security и т.д.
  - Python: Python Basics, OOP, Web Frameworks, Async, Testing и т.д.
  - Node.js: Node.js Basics, Express.js, Async, Database, Testing и т.д.
- Создает общие компетенции для направлений:
  - Frontend: JavaScript/TypeScript, HTML/CSS, Responsive Design и т.д.
  - Backend: RESTful API, Database Design, SQL, Authentication и т.д.
- Связывает компетенции с технологиями и направлениями
- Выводит статистику созданных данных

**Важно:** Без этого скрипта создание assessment будет возвращать ошибку "No competencies found"

### `seed_directions.sql`
**Когда выполнять:** После всех миграций, для заполнения тестовыми данными

**Что делает:**
- Добавляет примеры направлений
- Показывает примеры SQL для добавления компетенций к направлениям

---

## Быстрая команда для Supabase

Если вы используете Supabase SQL Editor, выполните миграции в таком порядке:

```sql
-- 1. Сначала базовая схема (если еще не применена)
-- Выполните database/schema.sql

-- 2. Затем миграции по порядку:
-- Выполните add_directions_table.sql
-- Выполните add_technologies_table.sql  
-- Выполните add_questions_table.sql

-- 3. Заполнение тестовыми данными (РЕКОМЕНДУЕТСЯ)
-- Выполните seed_technologies.sql (создаст направления и технологии)
-- Выполните seed_competencies.sql (ОБЯЗАТЕЛЬНО - создаст компетенции)
-- Выполните seed_directions.sql (дополнительные примеры, опционально)
```

---

## Проверка успешного применения

После выполнения миграций проверьте наличие таблиц:

```sql
-- Проверка таблиц направлений
SELECT * FROM directions LIMIT 1;
SELECT * FROM direction_competencies LIMIT 1;

-- Проверка таблиц технологий
SELECT * FROM technologies LIMIT 1;
SELECT * FROM direction_technologies LIMIT 1;
SELECT * FROM technology_competencies LIMIT 1;

-- Проверка таблицы вопросов
SELECT * FROM questions LIMIT 1;

-- Проверка обновленных колонок
SELECT direction_id, technology_id FROM assessments LIMIT 1;
SELECT question_id FROM question_history LIMIT 1;
```

Если все запросы выполняются без ошибок - миграции применены успешно!
