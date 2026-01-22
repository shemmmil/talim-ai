-- Скрипт для заполнения направлений и технологий
-- Выполните после применения миграций add_directions_table.sql и add_technologies_table.sql

-- ============================================
-- 1. СОЗДАНИЕ НАПРАВЛЕНИЙ
-- ============================================

INSERT INTO directions (name, display_name, description) VALUES
('frontend', 'Frontend', 'Frontend разработка - создание пользовательских интерфейсов'),
('backend', 'Backend', 'Backend разработка - серверная логика и API'),
('fullstack', 'Fullstack', 'Fullstack разработка - полный цикл разработки'),
('mobile', 'Mobile', 'Мобильная разработка - iOS и Android приложения'),
('devops', 'DevOps', 'DevOps и инфраструктура - автоматизация и развертывание'),
('data', 'Data Science', 'Data Science и аналитика данных'),
('qa', 'QA', 'Тестирование и обеспечение качества')
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- 2. СОЗДАНИЕ ТЕХНОЛОГИЙ
-- ============================================

-- Frontend технологии
INSERT INTO technologies (name, description) VALUES
('react', 'React - библиотека для создания пользовательских интерфейсов'),
('vue', 'Vue.js - прогрессивный JavaScript фреймворк'),
('angular', 'Angular - платформа для разработки мобильных и десктопных веб-приложений'),
('svelte', 'Svelte - компилируемый компонентный фреймворк'),
('nextjs', 'Next.js - React фреймворк для production'),
('nuxtjs', 'Nuxt.js - Vue.js фреймворк для production')
ON CONFLICT (name) DO NOTHING;

-- Backend технологии
INSERT INTO technologies (name, description) VALUES
('go', 'Go (Golang) - язык программирования от Google'),
('php', 'PHP - серверный язык программирования'),
('python', 'Python - высокоуровневый язык программирования'),
('nodejs', 'Node.js - JavaScript runtime для серверной разработки'),
('java', 'Java - объектно-ориентированный язык программирования'),
('csharp', 'C# - язык программирования от Microsoft'),
('rust', 'Rust - системный язык программирования'),
('ruby', 'Ruby - динамический язык программирования')
ON CONFLICT (name) DO NOTHING;

-- Mobile технологии
INSERT INTO technologies (name, description) VALUES
('react-native', 'React Native - фреймворк для разработки мобильных приложений'),
('flutter', 'Flutter - UI toolkit от Google'),
('swift', 'Swift - язык программирования для iOS'),
('kotlin', 'Kotlin - язык программирования для Android'),
('ionic', 'Ionic - фреймворк для гибридных мобильных приложений')
ON CONFLICT (name) DO NOTHING;

-- DevOps технологии
INSERT INTO technologies (name, description) VALUES
('docker', 'Docker - платформа для контейнеризации'),
('kubernetes', 'Kubernetes - оркестрация контейнеров'),
('terraform', 'Terraform - инфраструктура как код'),
('ansible', 'Ansible - автоматизация конфигурации'),
('jenkins', 'Jenkins - CI/CD сервер')
ON CONFLICT (name) DO NOTHING;

-- Data Science технологии
INSERT INTO technologies (name, description) VALUES
('python-ds', 'Python для Data Science'),
('r', 'R - язык программирования для статистики'),
('sql', 'SQL - язык запросов к базам данных'),
('pandas', 'Pandas - библиотека для анализа данных'),
('tensorflow', 'TensorFlow - фреймворк для машинного обучения')
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- 3. СВЯЗЫВАНИЕ ТЕХНОЛОГИЙ С НАПРАВЛЕНИЯМИ
-- ============================================

-- Frontend технологии
INSERT INTO direction_technologies (direction_id, technology_id, order_index)
SELECT 
  d.id as direction_id,
  t.id as technology_id,
  row_number() OVER (ORDER BY t.name) as order_index
FROM directions d
CROSS JOIN technologies t
WHERE d.name = 'frontend' 
  AND t.name IN ('react', 'vue', 'angular', 'svelte', 'nextjs', 'nuxtjs')
ON CONFLICT (direction_id, technology_id) DO NOTHING;

-- Backend технологии
INSERT INTO direction_technologies (direction_id, technology_id, order_index)
SELECT 
  d.id as direction_id,
  t.id as technology_id,
  row_number() OVER (ORDER BY t.name) as order_index
FROM directions d
CROSS JOIN technologies t
WHERE d.name = 'backend' 
  AND t.name IN ('go', 'php', 'python', 'nodejs', 'java', 'csharp', 'rust', 'ruby')
ON CONFLICT (direction_id, technology_id) DO NOTHING;

-- Mobile технологии
INSERT INTO direction_technologies (direction_id, technology_id, order_index)
SELECT 
  d.id as direction_id,
  t.id as technology_id,
  row_number() OVER (ORDER BY t.name) as order_index
FROM directions d
CROSS JOIN technologies t
WHERE d.name = 'mobile' 
  AND t.name IN ('react-native', 'flutter', 'swift', 'kotlin', 'ionic')
ON CONFLICT (direction_id, technology_id) DO NOTHING;

-- DevOps технологии
INSERT INTO direction_technologies (direction_id, technology_id, order_index)
SELECT 
  d.id as direction_id,
  t.id as technology_id,
  row_number() OVER (ORDER BY t.name) as order_index
FROM directions d
CROSS JOIN technologies t
WHERE d.name = 'devops' 
  AND t.name IN ('docker', 'kubernetes', 'terraform', 'ansible', 'jenkins')
ON CONFLICT (direction_id, technology_id) DO NOTHING;

-- Data Science технологии
INSERT INTO direction_technologies (direction_id, technology_id, order_index)
SELECT 
  d.id as direction_id,
  t.id as technology_id,
  row_number() OVER (ORDER BY t.name) as order_index
FROM directions d
CROSS JOIN technologies t
WHERE d.name = 'data' 
  AND t.name IN ('python-ds', 'r', 'sql', 'pandas', 'tensorflow')
ON CONFLICT (direction_id, technology_id) DO NOTHING;

-- ============================================
-- 4. ПРОВЕРКА РЕЗУЛЬТАТОВ
-- ============================================

-- Проверка созданных направлений
SELECT 'Directions created:' as info;
SELECT name, display_name, description FROM directions ORDER BY name;

-- Проверка созданных технологий
SELECT 'Technologies created:' as info;
SELECT name, description FROM technologies ORDER BY name;

-- Проверка связей направлений и технологий
SELECT 'Direction-Technology links:' as info;
SELECT 
  d.name as direction_name,
  d.display_name as direction_display,
  t.name as technology_name,
  dt.order_index
FROM direction_technologies dt
JOIN directions d ON dt.direction_id = d.id
JOIN technologies t ON dt.technology_id = t.id
ORDER BY d.name, dt.order_index;

-- Статистика
SELECT 
  'Summary:' as info,
  (SELECT COUNT(*) FROM directions) as directions_count,
  (SELECT COUNT(*) FROM technologies) as technologies_count,
  (SELECT COUNT(*) FROM direction_technologies) as links_count;
