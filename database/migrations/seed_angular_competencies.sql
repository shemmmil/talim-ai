-- Скрипт для добавления компетенций Angular
-- Выполните после seed_competencies.sql

-- ============================================
-- СОЗДАНИЕ КОМПЕТЕНЦИЙ ДЛЯ ANGULAR
-- ============================================

-- Angular компетенции
INSERT INTO competencies (name, description, category, importance_weight, order_index)
SELECT * FROM (VALUES
  ('Angular Basics', 'Основы Angular: компоненты, модули, директивы, сервисы', 'Языки программирования', 5, 1),
  ('TypeScript', 'TypeScript для Angular: типы, интерфейсы, декораторы', 'Языки программирования', 5, 2),
  ('Angular Components', 'Компоненты Angular: lifecycle hooks, @Input/@Output, ViewChild', 'Фреймворки', 5, 3),
  ('Angular Services & DI', 'Сервисы и Dependency Injection в Angular', 'Архитектура', 5, 4),
  ('Angular Routing', 'Маршрутизация: Router, Guards, Resolvers', 'Фреймворки', 4, 5),
  ('RxJS', 'Reactive Extensions: Observables, Operators, Subjects', 'Продвинутые темы', 5, 6),
  ('Angular Forms', 'Работа с формами: Template-driven и Reactive Forms', 'Фреймворки', 4, 7),
  ('Angular HTTP', 'HTTP клиент: HttpClient, interceptors, error handling', 'Веб-разработка', 4, 8),
  ('Angular State Management', 'Управление состоянием: NgRx, Akita, Services', 'Архитектура', 4, 9),
  ('Angular Testing', 'Тестирование: Jasmine, Karma, Angular Testing Utilities', 'Тестирование', 3, 10),
  ('Angular Performance', 'Оптимизация производительности: OnPush, Change Detection, Lazy Loading', 'Оптимизация', 3, 11),
  ('Angular CLI', 'Angular CLI: генерация компонентов, сборка, деплой', 'Инструменты', 3, 12)
) AS v(name, description, category, importance_weight, order_index)
WHERE NOT EXISTS (SELECT 1 FROM competencies WHERE competencies.name = v.name);

-- ============================================
-- СВЯЗЫВАНИЕ КОМПЕТЕНЦИЙ С ТЕХНОЛОГИЕЙ ANGULAR
-- ============================================

INSERT INTO technology_competencies (technology_id, competency_id, order_index)
SELECT 
  t.id as technology_id,
  c.id as competency_id,
  c.order_index
FROM technologies t
CROSS JOIN competencies c
WHERE t.name = 'angular' 
  AND c.name IN (
    'Angular Basics', 'TypeScript', 'Angular Components', 
    'Angular Services & DI', 'Angular Routing', 'RxJS',
    'Angular Forms', 'Angular HTTP', 'Angular State Management',
    'Angular Testing', 'Angular Performance', 'Angular CLI'
  )
ON CONFLICT (technology_id, competency_id) DO NOTHING;

-- ============================================
-- ПРОВЕРКА РЕЗУЛЬТАТОВ
-- ============================================

-- Проверка компетенций для Angular
SELECT 'Angular competencies:' as info;
SELECT 
  t.name as technology,
  c.name as competency,
  c.description,
  tc.order_index
FROM technology_competencies tc
JOIN technologies t ON tc.technology_id = t.id
JOIN competencies c ON tc.competency_id = c.id
WHERE t.name = 'angular'
ORDER BY tc.order_index;

-- Статистика
SELECT 
  'Summary:' as info,
  (SELECT COUNT(*) FROM competencies WHERE name LIKE 'Angular%' OR name = 'TypeScript') as angular_competencies_count,
  (SELECT COUNT(*) FROM technology_competencies tc 
   JOIN technologies t ON tc.technology_id = t.id 
   WHERE t.name = 'angular') as angular_links_count;
