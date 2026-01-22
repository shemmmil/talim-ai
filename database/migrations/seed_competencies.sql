-- Скрипт для создания компетенций и их связи с направлениями/технологиями
-- Выполните после seed_technologies.sql

-- ============================================
-- 1. СОЗДАНИЕ КОМПЕТЕНЦИЙ ДЛЯ FRONTEND ТЕХНОЛОГИЙ
-- ============================================

-- React компетенции
INSERT INTO competencies (name, description, category, importance_weight, order_index)
SELECT * FROM (VALUES
  ('React Basics', 'Основы React: компоненты, JSX, props, state', 'Языки программирования', 5, 1),
  ('React Hooks', 'React Hooks: useState, useEffect, useContext, custom hooks', 'Фреймворки', 5, 2),
  ('React Router', 'Маршрутизация в React приложениях', 'Фреймворки', 4, 3),
  ('State Management', 'Управление состоянием: Redux, Zustand, Context API', 'Архитектура', 4, 4),
  ('React Performance', 'Оптимизация производительности React приложений', 'Оптимизация', 3, 5),
  ('Testing React', 'Тестирование React компонентов: Jest, React Testing Library', 'Тестирование', 3, 6)
) AS v(name, description, category, importance_weight, order_index)
WHERE NOT EXISTS (SELECT 1 FROM competencies WHERE competencies.name = v.name);

-- Vue компетенции
INSERT INTO competencies (name, description, category, importance_weight, order_index)
SELECT * FROM (VALUES
  ('Vue Basics', 'Основы Vue.js: компоненты, директивы, data binding', 'Языки программирования', 5, 1),
  ('Vue Composition API', 'Composition API и setup() функция', 'Фреймворки', 5, 2),
  ('Vue Router', 'Маршрутизация в Vue приложениях', 'Фреймворки', 4, 3),
  ('Vuex/Pinia', 'Управление состоянием в Vue', 'Архитектура', 4, 4),
  ('Vue Performance', 'Оптимизация производительности Vue приложений', 'Оптимизация', 3, 5)
) AS v(name, description, category, importance_weight, order_index)
WHERE NOT EXISTS (SELECT 1 FROM competencies WHERE competencies.name = v.name);

-- ============================================
-- 2. СОЗДАНИЕ КОМПЕТЕНЦИЙ ДЛЯ BACKEND ТЕХНОЛОГИЙ
-- ============================================

-- Go компетенции
INSERT INTO competencies (name, description, category, importance_weight, order_index)
SELECT * FROM (VALUES
  ('Go Basics', 'Основы Go: синтаксис, типы данных, функции', 'Языки программирования', 5, 1),
  ('Go Concurrency', 'Горутины, каналы, sync пакет', 'Продвинутые темы', 5, 2),
  ('Go Standard Library', 'Работа со стандартной библиотекой Go', 'Языки программирования', 4, 3),
  ('Go Web Development', 'Создание веб-серверов: net/http, gorilla/mux', 'Веб-разработка', 4, 4),
  ('Go Testing', 'Тестирование в Go: testing пакет, табличные тесты', 'Тестирование', 3, 5),
  ('Go Best Practices', 'Идиоматичный Go код, error handling', 'Лучшие практики', 4, 6)
) AS v(name, description, category, importance_weight, order_index)
WHERE NOT EXISTS (SELECT 1 FROM competencies WHERE competencies.name = v.name);

-- PHP компетенции
INSERT INTO competencies (name, description, category, importance_weight, order_index)
SELECT * FROM (VALUES
  ('PHP Basics', 'Основы PHP: синтаксис, типы данных, функции', 'Языки программирования', 5, 1),
  ('OOP in PHP', 'Объектно-ориентированное программирование в PHP', 'Языки программирования', 5, 2),
  ('PHP Frameworks', 'Работа с фреймворками: Laravel, Symfony', 'Фреймворки', 5, 3),
  ('PHP Database', 'Работа с БД: PDO, Eloquent ORM', 'Базы данных', 4, 4),
  ('PHP Security', 'Безопасность в PHP приложениях', 'Безопасность', 4, 5)
) AS v(name, description, category, importance_weight, order_index)
WHERE NOT EXISTS (SELECT 1 FROM competencies WHERE competencies.name = v.name);

-- Python компетенции
INSERT INTO competencies (name, description, category, importance_weight, order_index)
SELECT * FROM (VALUES
  ('Python Basics', 'Основы Python: синтаксис, типы данных, функции', 'Языки программирования', 5, 1),
  ('Python OOP', 'Объектно-ориентированное программирование в Python', 'Языки программирования', 5, 2),
  ('Python Web Frameworks', 'Django, Flask, FastAPI', 'Фреймворки', 5, 3),
  ('Python Database', 'Работа с БД: SQLAlchemy, Django ORM', 'Базы данных', 4, 4),
  ('Python Async', 'Асинхронное программирование: asyncio, async/await', 'Продвинутые темы', 4, 5),
  ('Python Testing', 'Тестирование: pytest, unittest', 'Тестирование', 3, 6)
) AS v(name, description, category, importance_weight, order_index)
WHERE NOT EXISTS (SELECT 1 FROM competencies WHERE competencies.name = v.name);

-- Node.js компетенции
INSERT INTO competencies (name, description, category, importance_weight, order_index)
SELECT * FROM (VALUES
  ('Node.js Basics', 'Основы Node.js: модули, события, потоки', 'Языки программирования', 5, 1),
  ('Express.js', 'Создание веб-серверов с Express.js', 'Фреймворки', 5, 2),
  ('Node.js Async', 'Асинхронное программирование: callbacks, promises, async/await', 'Продвинутые темы', 5, 3),
  ('Node.js Database', 'Работа с БД: MongoDB, PostgreSQL, Sequelize', 'Базы данных', 4, 4),
  ('Node.js Testing', 'Тестирование: Jest, Mocha', 'Тестирование', 3, 5)
) AS v(name, description, category, importance_weight, order_index)
WHERE NOT EXISTS (SELECT 1 FROM competencies WHERE competencies.name = v.name);

-- ============================================
-- 3. ОБЩИЕ КОМПЕТЕНЦИИ ДЛЯ НАПРАВЛЕНИЙ
-- ============================================

-- Общие Frontend компетенции
INSERT INTO competencies (name, description, category, importance_weight, order_index)
SELECT * FROM (VALUES
  ('JavaScript/TypeScript', 'Знание JavaScript ES6+ и TypeScript', 'Языки программирования', 5, 1),
  ('HTML/CSS', 'Верстка и стилизация: HTML5, CSS3, Flexbox, Grid', 'Верстка', 5, 2),
  ('Responsive Design', 'Адаптивный дизайн и mobile-first подход', 'Верстка', 4, 3),
  ('Web Performance', 'Оптимизация производительности веб-приложений', 'Оптимизация', 4, 4),
  ('Browser APIs', 'Работа с браузерными API: DOM, Fetch, LocalStorage', 'Веб-разработка', 4, 5),
  ('Build Tools', 'Инструменты сборки: Webpack, Vite, Parcel', 'Инструменты', 3, 6),
  ('Version Control', 'Git и системы контроля версий', 'Инструменты', 4, 7)
) AS v(name, description, category, importance_weight, order_index)
WHERE NOT EXISTS (SELECT 1 FROM competencies WHERE competencies.name = v.name);

-- Общие Backend компетенции
INSERT INTO competencies (name, description, category, importance_weight, order_index)
SELECT * FROM (VALUES
  ('RESTful API', 'Проектирование и разработка REST API', 'Веб-разработка', 5, 1),
  ('Database Design', 'Проектирование баз данных, нормализация', 'Базы данных', 5, 2),
  ('SQL', 'Работа с SQL: запросы, индексы, оптимизация', 'Базы данных', 5, 3),
  ('Authentication & Authorization', 'Аутентификация и авторизация: JWT, OAuth', 'Безопасность', 5, 4),
  ('API Security', 'Безопасность API: CORS, rate limiting, input validation', 'Безопасность', 4, 5),
  ('Caching', 'Кэширование: Redis, Memcached', 'Оптимизация', 4, 6),
  ('Microservices', 'Архитектура микросервисов', 'Архитектура', 3, 7),
  ('Docker', 'Контейнеризация приложений', 'DevOps', 3, 8)
) AS v(name, description, category, importance_weight, order_index)
WHERE NOT EXISTS (SELECT 1 FROM competencies WHERE competencies.name = v.name);

-- ============================================
-- 4. СВЯЗЫВАНИЕ КОМПЕТЕНЦИЙ С ТЕХНОЛОГИЯМИ
-- ============================================

-- React компетенции
INSERT INTO technology_competencies (technology_id, competency_id, order_index)
SELECT 
  t.id as technology_id,
  c.id as competency_id,
  c.order_index
FROM technologies t
CROSS JOIN competencies c
WHERE t.name = 'react' 
  AND c.name IN (
    'React Basics', 'React Hooks', 'React Router', 
    'State Management', 'React Performance', 'Testing React'
  )
ON CONFLICT (technology_id, competency_id) DO NOTHING;

-- Vue компетенции
INSERT INTO technology_competencies (technology_id, competency_id, order_index)
SELECT 
  t.id as technology_id,
  c.id as competency_id,
  c.order_index
FROM technologies t
CROSS JOIN competencies c
WHERE t.name = 'vue' 
  AND c.name IN (
    'Vue Basics', 'Vue Composition API', 'Vue Router', 
    'Vuex/Pinia', 'Vue Performance'
  )
ON CONFLICT (technology_id, competency_id) DO NOTHING;

-- Go компетенции
INSERT INTO technology_competencies (technology_id, competency_id, order_index)
SELECT 
  t.id as technology_id,
  c.id as competency_id,
  c.order_index
FROM technologies t
CROSS JOIN competencies c
WHERE t.name = 'go' 
  AND c.name IN (
    'Go Basics', 'Go Concurrency', 'Go Standard Library', 
    'Go Web Development', 'Go Testing', 'Go Best Practices'
  )
ON CONFLICT (technology_id, competency_id) DO NOTHING;

-- PHP компетенции
INSERT INTO technology_competencies (technology_id, competency_id, order_index)
SELECT 
  t.id as technology_id,
  c.id as competency_id,
  c.order_index
FROM technologies t
CROSS JOIN competencies c
WHERE t.name = 'php' 
  AND c.name IN (
    'PHP Basics', 'OOP in PHP', 'PHP Frameworks', 
    'PHP Database', 'PHP Security'
  )
ON CONFLICT (technology_id, competency_id) DO NOTHING;

-- Python компетенции
INSERT INTO technology_competencies (technology_id, competency_id, order_index)
SELECT 
  t.id as technology_id,
  c.id as competency_id,
  c.order_index
FROM technologies t
CROSS JOIN competencies c
WHERE t.name = 'python' 
  AND c.name IN (
    'Python Basics', 'Python OOP', 'Python Web Frameworks', 
    'Python Database', 'Python Async', 'Python Testing'
  )
ON CONFLICT (technology_id, competency_id) DO NOTHING;

-- Node.js компетенции
INSERT INTO technology_competencies (technology_id, competency_id, order_index)
SELECT 
  t.id as technology_id,
  c.id as competency_id,
  c.order_index
FROM technologies t
CROSS JOIN competencies c
WHERE t.name = 'nodejs' 
  AND c.name IN (
    'Node.js Basics', 'Express.js', 'Node.js Async', 
    'Node.js Database', 'Node.js Testing'
  )
ON CONFLICT (technology_id, competency_id) DO NOTHING;

-- ============================================
-- 5. СВЯЗЫВАНИЕ ОБЩИХ КОМПЕТЕНЦИЙ С НАПРАВЛЕНИЯМИ
-- ============================================

-- Общие Frontend компетенции
INSERT INTO direction_competencies (direction_id, competency_id, order_index)
SELECT 
  d.id as direction_id,
  c.id as competency_id,
  c.order_index
FROM directions d
CROSS JOIN competencies c
WHERE d.name = 'frontend' 
  AND c.name IN (
    'JavaScript/TypeScript', 'HTML/CSS', 'Responsive Design', 
    'Web Performance', 'Browser APIs', 'Build Tools', 'Version Control'
  )
ON CONFLICT (direction_id, competency_id) DO NOTHING;

-- Общие Backend компетенции
INSERT INTO direction_competencies (direction_id, competency_id, order_index)
SELECT 
  d.id as direction_id,
  c.id as competency_id,
  c.order_index
FROM directions d
CROSS JOIN competencies c
WHERE d.name = 'backend' 
  AND c.name IN (
    'RESTful API', 'Database Design', 'SQL', 
    'Authentication & Authorization', 'API Security', 
    'Caching', 'Microservices', 'Docker'
  )
ON CONFLICT (direction_id, competency_id) DO NOTHING;

-- ============================================
-- 6. ПРОВЕРКА РЕЗУЛЬТАТОВ
-- ============================================

-- Проверка компетенций для React
SELECT 'React competencies:' as info;
SELECT 
  t.name as technology,
  c.name as competency,
  tc.order_index
FROM technology_competencies tc
JOIN technologies t ON tc.technology_id = t.id
JOIN competencies c ON tc.competency_id = c.id
WHERE t.name = 'react'
ORDER BY tc.order_index;

-- Проверка общих компетенций для Frontend
SELECT 'Frontend direction competencies:' as info;
SELECT 
  d.name as direction,
  c.name as competency,
  dc.order_index
FROM direction_competencies dc
JOIN directions d ON dc.direction_id = d.id
JOIN competencies c ON dc.competency_id = c.id
WHERE d.name = 'frontend'
ORDER BY dc.order_index;

-- Статистика
SELECT 
  'Summary:' as info,
  (SELECT COUNT(*) FROM competencies) as competencies_count,
  (SELECT COUNT(*) FROM technology_competencies) as technology_links_count,
  (SELECT COUNT(*) FROM direction_competencies) as direction_links_count;
