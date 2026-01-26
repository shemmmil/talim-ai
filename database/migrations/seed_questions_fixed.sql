-- Исправленная версия скрипта для создания вопросов
-- Использует DO блоки для более надежного выполнения

-- ============================================
-- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ВОПРОСА
-- ============================================

CREATE OR REPLACE FUNCTION create_question_if_not_exists(
  p_competency_name TEXT,
  p_question_text TEXT,
  p_difficulty INTEGER,
  p_question_number INTEGER,
  p_expected_key_points JSONB,
  p_estimated_answer_time TEXT
) RETURNS VOID AS $$
DECLARE
  v_competency_id UUID;
BEGIN
  -- Находим компетенцию по имени
  SELECT id INTO v_competency_id 
  FROM competencies 
  WHERE name = p_competency_name 
  LIMIT 1;
  
  IF v_competency_id IS NULL THEN
    RAISE NOTICE 'Competency "%" not found, skipping question', p_competency_name;
    RETURN;
  END IF;
  
  -- Создаем вопрос, если его еще нет
  INSERT INTO questions (
    competency_id, 
    question_text, 
    difficulty, 
    question_number, 
    expected_key_points, 
    estimated_answer_time
  )
  SELECT 
    v_competency_id,
    p_question_text,
    p_difficulty,
    p_question_number,
    p_expected_key_points,
    p_estimated_answer_time
  WHERE NOT EXISTS (
    SELECT 1 FROM questions 
    WHERE competency_id = v_competency_id 
      AND difficulty = p_difficulty 
      AND question_number = p_question_number
  );
  
  RAISE NOTICE 'Question created/checked for % (difficulty=%, number=%)', 
    p_competency_name, p_difficulty, p_question_number;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- СОЗДАНИЕ ВОПРОСОВ ДЛЯ REACT
-- ============================================

-- React Basics
SELECT create_question_if_not_exists(
  'React Basics',
  'Объясните, что такое компоненты в React и как они работают. В чем разница между функциональными и классовыми компонентами?',
  1, 1,
  '["Компоненты как переиспользуемые блоки UI", "Функциональные компоненты с хуками", "Классовые компоненты с lifecycle методами"]'::jsonb,
  '2-3 минуты'
);

SELECT create_question_if_not_exists(
  'React Basics',
  'Что такое JSX и как он преобразуется в JavaScript? Объясните синтаксис JSX и его особенности.',
  2, 2,
  '["JSX как синтаксический сахар", "Трансформация в React.createElement", "Правила именования и атрибутов"]'::jsonb,
  '2-3 минуты'
);

SELECT create_question_if_not_exists(
  'React Basics',
  'Объясните концепцию props и state в React. Когда использовать props, а когда state? Приведите примеры.',
  3, 3,
  '["Props для передачи данных вниз", "State для внутреннего состояния компонента", "Однонаправленный поток данных"]'::jsonb,
  '3-4 минуты'
);

-- React Hooks
SELECT create_question_if_not_exists(
  'React Hooks',
  'Что такое React Hooks и зачем они нужны? Объясните основные правила использования хуков.',
  2, 1,
  '["Хуки для функциональных компонентов", "Правила хуков: только на верхнем уровне", "useState и useEffect как основные хуки"]'::jsonb,
  '2-3 минуты'
);

SELECT create_question_if_not_exists(
  'React Hooks',
  'Объясните разницу между useEffect и useLayoutEffect. Когда использовать каждый из них?',
  4, 2,
  '["useEffect - асинхронный, после рендера", "useLayoutEffect - синхронный, до отрисовки", "Примеры использования"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'React Hooks',
  'Как создать кастомный хук? Приведите пример кастомного хука и объясните его назначение.',
  4, 3,
  '["Правила создания кастомных хуков", "Переиспользование логики", "Пример: useFetch, useLocalStorage"]'::jsonb,
  '3-4 минуты'
);

-- State Management
SELECT create_question_if_not_exists(
  'State Management',
  'Когда использовать глобальное управление состоянием (Redux, Zustand), а когда достаточно локального state?',
  3, 1,
  '["Локальный state для изолированных данных", "Глобальное state для общих данных", "Критерии выбора"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'State Management',
  'Объясните принципы работы Redux: store, actions, reducers. Как организовать структуру Redux в большом приложении?',
  5, 2,
  '["Однонаправленный поток данных", "Immutable updates", "Структура папок: actions, reducers, selectors"]'::jsonb,
  '4-5 минут'
);

-- ============================================
-- СОЗДАНИЕ ВОПРОСОВ ДЛЯ GO
-- ============================================

-- Go Basics
SELECT create_question_if_not_exists(
  'Go Basics',
  'Объясните основные особенности языка Go. Чем Go отличается от других языков программирования?',
  2, 1,
  '["Статическая типизация", "Компиляция в один бинарный файл", "Простота и читаемость синтаксиса"]'::jsonb,
  '2-3 минуты'
);

SELECT create_question_if_not_exists(
  'Go Basics',
  'Что такое интерфейсы в Go и как они работают? Приведите пример использования интерфейсов.',
  3, 2,
  '["Неявная реализация интерфейсов", "Duck typing", "Пример: io.Reader, io.Writer"]'::jsonb,
  '3-4 минуты'
);

-- Go Concurrency
SELECT create_question_if_not_exists(
  'Go Concurrency',
  'Объясните концепцию горутин в Go. Как они отличаются от потоков в других языках?',
  3, 1,
  '["Легковесные потоки", "Управление через runtime", "Преимущества перед системными потоками"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'Go Concurrency',
  'Что такое каналы в Go и для чего они используются? Объясните разницу между буферизованными и небуферизованными каналами.',
  4, 2,
  '["Каналы для коммуникации между горутинами", "Буферизованные vs небуферизованные", "Select statement"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'Go Concurrency',
  'Как избежать race conditions в Go? Объясните использование sync пакета: Mutex, RWMutex, WaitGroup.',
  5, 3,
  '["Mutex для эксклюзивного доступа", "RWMutex для множественного чтения", "WaitGroup для синхронизации горутин"]'::jsonb,
  '4-5 минут'
);

-- ============================================
-- СОЗДАНИЕ ВОПРОСОВ ДЛЯ ОБЩИХ КОМПЕТЕНЦИЙ
-- ============================================

-- JavaScript/TypeScript
SELECT create_question_if_not_exists(
  'JavaScript/TypeScript',
  'Объясните разницу между var, let и const в JavaScript. Когда использовать каждый из них?',
  2, 1,
  '["Function scope vs block scope", "Hoisting", "Immutability с const"]'::jsonb,
  '2-3 минуты'
);

SELECT create_question_if_not_exists(
  'JavaScript/TypeScript',
  'Что такое замыкания (closures) в JavaScript? Приведите пример использования замыканий.',
  3, 2,
  '["Доступ к внешним переменным", "Лексическое окружение", "Примеры: модули, приватные переменные"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'JavaScript/TypeScript',
  'Объясните концепцию промисов и async/await в JavaScript. Как обрабатывать ошибки в асинхронном коде?',
  4, 3,
  '["Промисы для асинхронных операций", "Async/await как синтаксический сахар", "Try-catch для обработки ошибок"]'::jsonb,
  '3-4 минуты'
);

-- HTML/CSS
SELECT create_question_if_not_exists(
  'HTML/CSS',
  'Объясните разницу между Flexbox и CSS Grid. Когда использовать каждый из них?',
  3, 1,
  '["Flexbox для одномерной раскладки", "Grid для двумерной раскладки", "Примеры использования"]'::jsonb,
  '3-4 минуты'
);

-- Responsive Design
SELECT create_question_if_not_exists(
  'Responsive Design',
  'Что такое адаптивный дизайн и в чем его основные принципы? Объясните концепцию mobile-first.',
  2, 1,
  '["Адаптация под разные размеры экранов", "Mobile-first подход", "Breakpoints и media queries"]'::jsonb,
  '2-3 минуты'
);

SELECT create_question_if_not_exists(
  'Responsive Design',
  'Объясните разницу между адаптивным (responsive) и адаптируемым (adaptive) дизайном. Когда использовать каждый подход?',
  3, 2,
  '["Responsive - один макет, адаптируется", "Adaptive - несколько фиксированных макетов", "Преимущества и недостатки"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'Responsive Design',
  'Как правильно использовать CSS media queries для создания адаптивного дизайна? Приведите примеры breakpoints.',
  3, 3,
  '["Синтаксис media queries", "Типичные breakpoints (mobile, tablet, desktop)", "Min-width vs max-width"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'Responsive Design',
  'Что такое viewport meta tag и зачем он нужен? Объясните его параметры.',
  2, 4,
  '["Viewport для мобильных устройств", "width=device-width", "initial-scale, user-scalable"]'::jsonb,
  '2-3 минуты'
);

SELECT create_question_if_not_exists(
  'Responsive Design',
  'Как оптимизировать изображения для адаптивного дизайна? Объясните использование srcset, sizes и picture element.',
  4, 5,
  '["Responsive images", "srcset для разных разрешений", "picture element для art direction", "WebP и современные форматы"]'::jsonb,
  '4-5 минут'
);

-- RESTful API
SELECT create_question_if_not_exists(
  'RESTful API',
  'Объясните принципы REST API. Какие HTTP методы используются для каких операций?',
  3, 1,
  '["GET, POST, PUT, DELETE методы", "Статус коды", "RESTful ресурсы и URL структура"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'RESTful API',
  'Как правильно проектировать REST API? Объясните best practices для именования endpoints и структуры ответов.',
  4, 2,
  '["RESTful naming conventions", "Версионирование API", "Стандартизация ответов (JSON)"]'::jsonb,
  '4-5 минут'
);

-- SQL
SELECT create_question_if_not_exists(
  'SQL',
  'Объясните разницу между INNER JOIN, LEFT JOIN и RIGHT JOIN. Когда использовать каждый тип?',
  3, 1,
  '["INNER JOIN - только совпадающие записи", "LEFT JOIN - все записи из левой таблицы", "RIGHT JOIN - все записи из правой таблицы"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'SQL',
  'Что такое индексы в базах данных и зачем они нужны? Как правильно создавать индексы?',
  4, 2,
  '["Индексы для ускорения запросов", "B-tree структура", "Когда создавать индексы, когда не стоит"]'::jsonb,
  '3-4 минуты'
);

-- Web Performance
SELECT create_question_if_not_exists(
  'Web Performance',
  'Что такое критический путь рендеринга (Critical Rendering Path) и как его оптимизировать?',
  3, 1,
  '["DOM, CSSOM, Render Tree", "Блокирующие ресурсы", "Оптимизация загрузки CSS и JS"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'Web Performance',
  'Объясните стратегии оптимизации загрузки JavaScript. Что такое code splitting, lazy loading, tree shaking?',
  4, 2,
  '["Code splitting для уменьшения bundle size", "Lazy loading модулей", "Tree shaking для удаления неиспользуемого кода", "Dynamic imports"]'::jsonb,
  '4-5 минут'
);

SELECT create_question_if_not_exists(
  'Web Performance',
  'Как оптимизировать изображения для веб-приложений? Объясните форматы изображений и техники оптимизации.',
  3, 3,
  '["WebP, AVIF современные форматы", "Lazy loading изображений", "Responsive images с srcset", "Сжатие и оптимизация"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'Web Performance',
  'Что такое кэширование в браузере и на сервере? Объясните Cache-Control, ETag, Last-Modified.',
  3, 4,
  '["Browser caching", "HTTP cache headers", "Cache-Control директивы", "ETag для валидации"]'::jsonb,
  '3-4 минуты'
);

SELECT create_question_if_not_exists(
  'Web Performance',
  'Как измерить и улучшить производительность веб-приложения? Объясните метрики Core Web Vitals.',
  4, 5,
  '["LCP (Largest Contentful Paint)", "FID (First Input Delay)", "CLS (Cumulative Layout Shift)", "Инструменты: Lighthouse, WebPageTest"]'::jsonb,
  '4-5 минут'
);

-- ============================================
-- ПРОВЕРКА РЕЗУЛЬТАТОВ
-- ============================================

SELECT 'Summary:' as info;
SELECT 
  c.name as competency,
  COUNT(q.id) as questions_count,
  MIN(q.difficulty) as min_difficulty,
  MAX(q.difficulty) as max_difficulty
FROM competencies c
LEFT JOIN questions q ON c.id = q.competency_id
WHERE c.name IN (
  'React Basics', 'React Hooks', 'State Management',
  'Go Basics', 'Go Concurrency',
  'JavaScript/TypeScript', 'HTML/CSS', 'Responsive Design', 'Web Performance', 'RESTful API', 'SQL'
)
GROUP BY c.name
ORDER BY c.name;

-- Удаляем вспомогательную функцию (опционально)
-- DROP FUNCTION IF EXISTS create_question_if_not_exists(TEXT, TEXT, INTEGER, INTEGER, JSONB, TEXT);
