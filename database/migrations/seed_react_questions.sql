-- Скрипт для добавления вопросов по React компетенциям
-- Выполните после seed_angular_competencies.sql или после создания React компетенций

-- ============================================
-- ВОПРОСЫ ДЛЯ REACT BASICS
-- ============================================

INSERT INTO questions (competency_id, question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
SELECT 
  c.id,
  v.question_text,
  v.difficulty,
  v.question_number,
  v.expected_key_points::jsonb,
  v.estimated_answer_time
FROM (VALUES
  -- Difficulty 1 (Базовый уровень)
  ('Что такое React и для чего он используется?', 1, 1, 
   '["Библиотека для создания пользовательских интерфейсов", "Компонентный подход", "Virtual DOM", "Декларативное программирование"]'::text,
   '1-2 минуты'),
  
  ('Что такое JSX в React?', 1, 2,
   '["Синтаксическое расширение JavaScript", "Позволяет писать HTML в JavaScript", "Компилируется в React.createElement", "Улучшает читаемость кода"]'::text,
   '1-2 минуты'),
  
  -- Difficulty 2
  ('Объясните разницу между props и state в React', 2, 1,
   '["Props - данные от родителя", "State - внутреннее состояние", "Props неизменяемы", "State можно обновлять", "Оба вызывают re-render"]'::text,
   '2-3 минуты'),
  
  ('Что такое компоненты в React и какие типы компонентов существуют?', 2, 2,
   '["Функциональные компоненты", "Классовые компоненты", "Переиспользуемые блоки UI", "Современный подход - функциональные"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 3
  ('Как работает Virtual DOM в React?', 3, 1,
   '["Виртуальное представление DOM", "Diffing algorithm", "Reconciliation", "Обновление только измененных элементов", "Оптимизация производительности"]'::text,
   '2-3 минуты'),
  
  ('Объясните lifecycle методы компонента в React', 3, 2,
   '["componentDidMount", "componentDidUpdate", "componentWillUnmount", "В функциональных - useEffect", "Порядок вызова"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 4
  ('Что такое reconciliation в React и как он работает?', 4, 1,
   '["Процесс сравнения Virtual DOM", "Алгоритм diffing", "Keys для оптимизации", "Batch updates", "Fiber architecture"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 5
  ('Объясните архитектуру Fiber в React', 5, 1,
   '["Переработанный reconciliation engine", "Приоритизация обновлений", "Incremental rendering", "Concurrent mode", "Time slicing"]'::text,
   '4-5 минут')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'React Basics'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ REACT HOOKS
-- ============================================

INSERT INTO questions (competency_id, question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
SELECT 
  c.id,
  v.question_text,
  v.difficulty,
  v.question_number,
  v.expected_key_points::jsonb,
  v.estimated_answer_time
FROM (VALUES
  -- Difficulty 1
  ('Что такое React Hooks и зачем они нужны?', 1, 1,
   '["Функции для использования state и lifecycle в функциональных компонентах", "Альтернатива классам", "Переиспользование логики", "Введены в React 16.8"]'::text,
   '1-2 минуты'),
  
  -- Difficulty 2
  ('Объясните как работает useState hook', 2, 1,
   '["Хук для управления состоянием", "Возвращает [значение, функцию обновления]", "Асинхронные обновления", "Functional updates", "Не мержит объекты автоматически"]'::text,
   '2-3 минуты'),
  
  ('Что делает useEffect и когда он выполняется?', 2, 2,
   '["Хук для side effects", "Выполняется после render", "Dependency array", "Cleanup function", "Замена lifecycle методов"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 3
  ('Объясните разницу между useMemo и useCallback', 3, 1,
   '["useMemo мемоизирует значение", "useCallback мемоизирует функцию", "Оптимизация производительности", "Зависимости", "Когда использовать каждый"]'::text,
   '3-4 минуты'),
  
  ('Как работает useContext и когда его использовать?', 3, 2,
   '["Доступ к Context", "Альтернатива prop drilling", "Подписка на изменения", "Потенциальные проблемы с производительностью", "Комбинирование с useMemo"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 4
  ('Объясните как создать custom hook и приведите пример', 4, 1,
   '["Функция начинающаяся с use", "Переиспользование логики", "Может использовать другие хуки", "Правила хуков", "Примеры использования"]'::text,
   '3-4 минуты'),
  
  ('Как работает useReducer и когда его предпочесть useState?', 4, 2,
   '["Альтернатива useState для сложного state", "Работает как Redux reducer", "Action и dispatch", "Предсказуемые обновления", "Когда state зависит от предыдущего"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 5
  ('Объясните правила хуков и почему они важны', 5, 1,
   '["Только на верхнем уровне", "Только в React функциях", "Причины ограничений", "Как React отслеживает хуки", "ESLint плагин"]'::text,
   '3-4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'React Hooks'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ REACT ROUTER
-- ============================================

INSERT INTO questions (competency_id, question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
SELECT 
  c.id,
  v.question_text,
  v.difficulty,
  v.question_number,
  v.expected_key_points::jsonb,
  v.estimated_answer_time
FROM (VALUES
  -- Difficulty 1
  ('Что такое React Router и для чего он используется?', 1, 1,
   '["Библиотека для маршрутизации в SPA", "Навигация без перезагрузки страницы", "Динамические роуты", "История браузера"]'::text,
   '1-2 минуты'),
  
  -- Difficulty 2
  ('Объясните основные компоненты React Router', 2, 1,
   '["BrowserRouter", "Route", "Link", "Switch/Routes", "useNavigate/useHistory"]'::text,
   '2-3 минуты'),
  
  ('Как передавать параметры через URL в React Router?', 2, 2,
   '["URL params (:id)", "Query params (?key=value)", "useParams hook", "useSearchParams hook", "Динамические сегменты"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 3
  ('Что такое nested routes и как их настроить?', 3, 1,
   '["Роуты внутри роутов", "Outlet компонент", "Relative paths", "Layout routes", "Index routes"]'::text,
   '2-3 минуты'),
  
  ('Объясните программную навигацию в React Router', 3, 2,
   '["useNavigate hook", "navigate функция", "replace vs push", "state передача", "Навигация с условиями"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 4
  ('Как реализовать защищенные роуты (Protected Routes)?', 4, 1,
   '["Проверка аутентификации", "Redirect на login", "Higher Order Component", "Custom Route компонент", "Loader функции"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 5
  ('Объясните data loading в React Router v6+', 5, 1,
   '["Loader functions", "useLoaderData", "Defer для streaming", "Error boundaries", "Оптимистичный UI"]'::text,
   '3-4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'React Router'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ STATE MANAGEMENT
-- ============================================

INSERT INTO questions (competency_id, question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
SELECT 
  c.id,
  v.question_text,
  v.difficulty,
  v.question_number,
  v.expected_key_points::jsonb,
  v.estimated_answer_time
FROM (VALUES
  -- Difficulty 1
  ('Что такое управление состоянием в React приложениях?', 1, 1,
   '["Хранение и синхронизация данных", "Local vs global state", "Prop drilling проблема", "Необходимость для больших приложений"]'::text,
   '2 минуты'),
  
  -- Difficulty 2
  ('Объясните Context API и когда его использовать', 2, 1,
   '["Встроенное решение для глобального state", "Provider и Consumer", "useContext hook", "Когда достаточно Context", "Проблемы с производительностью"]'::text,
   '2-3 минуты'),
  
  ('Что такое Redux и его основные концепции?', 2, 2,
   '["Предсказуемый контейнер состояния", "Store, Actions, Reducers", "Immutability", "Unidirectional data flow", "Redux DevTools"]'::text,
   '3 минуты'),
  
  -- Difficulty 3
  ('Объясните разницу между Redux и Zustand', 3, 1,
   '["Boilerplate", "API простота", "Размер бандла", "Middleware", "DevTools", "Когда использовать каждый"]'::text,
   '3-4 минуты'),
  
  ('Как работает Redux Toolkit и его преимущества?', 3, 2,
   '["Официальный recommended way", "createSlice", "Immer integration", "createAsyncThunk", "Меньше boilerplate"]'::text,
   '3 минуты'),
  
  -- Difficulty 4
  ('Объясните паттерны работы с асинхронными действиями в Redux', 4, 1,
   '["Redux Thunk", "Redux Saga", "createAsyncThunk", "Pending/fulfilled/rejected", "Error handling", "Cancellation"]'::text,
   '4 минуты'),
  
  -- Difficulty 5
  ('Сравните различные подходы к state management: Redux, Zustand, Jotai, Recoil', 5, 1,
   '["Архитектурные различия", "Производительность", "Boilerplate", "Learning curve", "Use cases для каждого", "Atomic state"]'::text,
   '4-5 минут')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'State Management'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ REACT PERFORMANCE
-- ============================================

INSERT INTO questions (competency_id, question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
SELECT 
  c.id,
  v.question_text,
  v.difficulty,
  v.question_number,
  v.expected_key_points::jsonb,
  v.estimated_answer_time
FROM (VALUES
  -- Difficulty 2
  ('Какие основные проблемы производительности в React приложениях?', 2, 1,
   '["Лишние re-renders", "Большие бандлы", "Медленные компоненты", "Memory leaks", "Неоптимальный state"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 3
  ('Как React.memo помогает оптимизировать производительность?', 3, 1,
   '["Мемоизация компонента", "Shallow comparison props", "Когда использовать", "Custom comparison", "Ограничения"]'::text,
   '2-3 минуты'),
  
  ('Объясните code splitting и lazy loading в React', 3, 2,
   '["React.lazy", "Suspense", "Dynamic imports", "Route-based splitting", "Уменьшение initial bundle"]'::text,
   '3 минуты'),
  
  -- Difficulty 4
  ('Как измерить и профилировать производительность React приложения?', 4, 1,
   '["React DevTools Profiler", "Chrome DevTools", "Web Vitals", "React.Profiler API", "Lighthouse", "Bundle analyzer"]'::text,
   '3-4 минуты'),
  
  ('Объясните виртуализацию списков и когда ее применять', 4, 2,
   '["Рендер только видимых элементов", "react-window/react-virtualized", "Проблемы с большими списками", "Scroll performance", "Trade-offs"]'::text,
   '3 минуты'),
  
  -- Difficulty 5
  ('Опишите стратегии оптимизации для больших React приложений', 5, 1,
   '["Code splitting", "Lazy loading", "Memoization стратегии", "State structure", "Virtualization", "Concurrent features", "Server Components"]'::text,
   '4-5 минут')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'React Performance'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ TESTING REACT
-- ============================================

INSERT INTO questions (competency_id, question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
SELECT 
  c.id,
  v.question_text,
  v.difficulty,
  v.question_number,
  v.expected_key_points::jsonb,
  v.estimated_answer_time
FROM (VALUES
  -- Difficulty 1
  ('Какие виды тестирования используются для React приложений?', 1, 1,
   '["Unit тесты", "Integration тесты", "E2E тесты", "Snapshot тесты", "Visual regression"]'::text,
   '2 минуты'),
  
  -- Difficulty 2
  ('Что такое React Testing Library и ее философия?', 2, 1,
   '["Тестирование как пользователь", "Queries по доступности", "Не тестировать implementation details", "user-event", "Замена Enzyme"]'::text,
   '2-3 минуты'),
  
  ('Как тестировать компоненты с hooks?', 2, 2,
   '["renderHook", "waitFor", "act", "Мокирование context", "Testing async hooks"]'::text,
   '3 минуты'),
  
  -- Difficulty 3
  ('Объясните как тестировать асинхронное поведение в React', 3, 1,
   '["waitFor", "findBy queries", "act warnings", "Mock API calls", "MSW для моков", "Handling promises"]'::text,
   '3-4 минуты'),
  
  ('Как правильно мокировать зависимости в тестах?', 3, 2,
   '["jest.mock", "jest.spyOn", "Manual mocks", "Mocking modules", "Mocking context/providers", "MSW"]'::text,
   '3 минуты'),
  
  -- Difficulty 4
  ('Объясните snapshot testing и его плюсы/минусы', 4, 1,
   '["Сохранение output компонента", "Детектирование неожиданных изменений", "Jest snapshots", "Когда полезно", "Проблемы и ограничения", "Поддержка снапшотов"]'::text,
   '3 минуты'),
  
  -- Difficulty 5
  ('Опишите стратегию тестирования для большого React приложения', 5, 1,
   '["Пирамида тестирования", "Test coverage цели", "CI/CD интеграция", "E2E vs Integration vs Unit", "Приоритизация тестов", "Test utilities"]'::text,
   '4-5 минут')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'Testing React'
ON CONFLICT DO NOTHING;

-- Проверка: сколько вопросов добавлено
SELECT 
  c.name as competency,
  COUNT(q.id) as questions_count
FROM competencies c
LEFT JOIN questions q ON q.competency_id = c.id
WHERE c.name IN ('React Basics', 'React Hooks', 'React Router', 'State Management', 'React Performance', 'Testing React')
GROUP BY c.name
ORDER BY c.name;
