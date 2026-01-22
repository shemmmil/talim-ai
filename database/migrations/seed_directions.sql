-- Скрипт для заполнения направлений и их компетенций
-- Выполните после применения миграции add_directions_table.sql

-- Примеры направлений
INSERT INTO directions (name, display_name, technologies, description) VALUES
('frontend', 'Frontend', 'React|Vue|Angular', 'Frontend разработка - создание пользовательских интерфейсов'),
('backend', 'Backend', 'Go|PHP|Python|Node.js', 'Backend разработка - серверная логика и API'),
('fullstack', 'Fullstack', 'React|Node.js|PostgreSQL', 'Fullstack разработка - полный цикл разработки'),
('mobile', 'Mobile', 'React Native|Flutter|Swift|Kotlin', 'Мобильная разработка - iOS и Android приложения'),
('devops', 'DevOps', 'Docker|Kubernetes|CI/CD', 'DevOps и инфраструктура - автоматизация и развертывание')
ON CONFLICT (name) DO NOTHING;

-- Примеры компетенций для Frontend
-- Сначала нужно создать компетенции (если их еще нет)
-- Затем связать их с направлениями через direction_competencies

-- Пример SQL для добавления компетенций к направлению Frontend:
-- 1. Найти ID направления
-- SELECT id FROM directions WHERE name = 'frontend';

-- 2. Найти или создать компетенции
-- INSERT INTO competencies (name, description, category) VALUES
-- ('JavaScript', 'Знание JavaScript ES6+', 'Языки программирования'),
-- ('React', 'Библиотека React для создания UI', 'Фреймворки'),
-- ('CSS/HTML', 'Верстка и стилизация', 'Верстка'),
-- ('State Management', 'Управление состоянием (Redux, MobX)', 'Архитектура'),
-- ('Testing', 'Тестирование фронтенд приложений', 'Тестирование')
-- ON CONFLICT DO NOTHING;

-- 3. Связать компетенции с направлением
-- INSERT INTO direction_competencies (direction_id, competency_id, order_index)
-- SELECT 
--   d.id as direction_id,
--   c.id as competency_id,
--   row_number() OVER () as order_index
-- FROM directions d
-- CROSS JOIN competencies c
-- WHERE d.name = 'frontend' 
--   AND c.name IN ('JavaScript', 'React', 'CSS/HTML', 'State Management', 'Testing')
-- ON CONFLICT DO NOTHING;

-- Аналогично для других направлений...
