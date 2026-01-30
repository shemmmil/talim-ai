-- Скрипт для добавления вопросов по Angular компетенциям
-- Выполните после seed_angular_competencies.sql

-- ============================================
-- ВОПРОСЫ ДЛЯ ANGULAR BASICS
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
  ('Что такое Angular и в чем его основные отличия от других фреймворков?', 1, 1,
   '["Full-featured фреймворк", "TypeScript из коробки", "Two-way data binding", "Dependency Injection", "Модульная архитектура"]'::text,
   '2 минуты'),
  
  ('Объясните структуру Angular приложения', 1, 2,
   '["Modules", "Components", "Services", "Directives", "Pipes", "Главный модуль AppModule"]'::text,
   '2 минуты'),
  
  -- Difficulty 2
  ('Что такое декораторы в Angular и для чего они используются?', 2, 1,
   '["@Component", "@Injectable", "@NgModule", "@Input/@Output", "Metadata для классов", "TypeScript decorators"]'::text,
   '2-3 минуты'),
  
  ('Объясните концепцию модулей (NgModule) в Angular', 2, 2,
   '["Организация кода", "declarations, imports, providers, bootstrap", "Feature modules", "Shared modules", "Lazy loading"]'::text,
   '3 минуты'),
  
  -- Difficulty 3
  ('Как работает Change Detection в Angular?', 3, 1,
   '["Zone.js", "Проверка изменений в дереве компонентов", "Default vs OnPush стратегии", "Triggering CD", "Performance implications"]'::text,
   '3-4 минуты'),
  
  ('Объясните разницу между ngOnInit и constructor', 3, 2,
   '["Constructor для DI", "ngOnInit для инициализации", "Порядок выполнения", "Когда использовать каждый", "Lifecycle hooks"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 4
  ('Что такое ViewChild и ContentChild и в чем их различие?', 4, 1,
   '["ViewChild для view queries", "ContentChild для content projection", "ng-content", "Timing и static flag", "AfterViewInit vs AfterContentInit"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 5
  ('Объясните архитектуру Angular: Ivy compiler и его преимущества', 5, 1,
   '["New rendering engine", "Smaller bundles", "Faster compilation", "Better debugging", "Locality principle", "Tree-shaking improvement"]'::text,
   '4-5 минут')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'Angular Basics'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ TYPESCRIPT
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
  ('Что такое TypeScript и зачем он нужен в Angular?', 1, 1,
   '["Typed superset JavaScript", "Static typing", "Compile-time errors", "Better IDE support", "Обязателен для Angular"]'::text,
   '2 минуты'),
  
  -- Difficulty 2
  ('Объясните основные типы данных в TypeScript', 2, 1,
   '["string, number, boolean", "array, tuple", "enum", "any, unknown, never", "void", "union и intersection types"]'::text,
   '2-3 минуты'),
  
  ('Что такое интерфейсы в TypeScript и как их использовать?', 2, 2,
   '["Contracts для объектов", "Optional properties", "Readonly", "Extends", "vs Type aliases"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 3
  ('Объясните Generics в TypeScript', 3, 1,
   '["Параметризованные типы", "Type safety", "Reusability", "Generic functions и classes", "Constraints", "Default types"]'::text,
   '3-4 минуты'),
  
  ('Что такое декораторы в TypeScript?', 3, 2,
   '["Метапрограммирование", "Class, method, property decorators", "Experimental feature", "Использование в Angular", "Decorator factories"]'::text,
   '3 минуты'),
  
  -- Difficulty 4
  ('Объясните advanced types: Union, Intersection, Conditional', 4, 1,
   '["Union types (|)", "Intersection types (&)", "Conditional types", "Mapped types", "Type guards", "Use cases"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 5
  ('Как работает Type Inference и Type Narrowing в TypeScript?', 5, 1,
   '["Автоматический вывод типов", "Control flow analysis", "Type guards", "Discriminated unions", "Type predicates", "as const"]'::text,
   '4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'TypeScript'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ ANGULAR COMPONENTS
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
  ('Что такое компонент в Angular?', 1, 1,
   '["Building block приложения", "@Component decorator", "Template, styles, logic", "Selector", "Переиспользуемый"]'::text,
   '1-2 минуты'),
  
  -- Difficulty 2
  ('Объясните lifecycle hooks компонента', 2, 1,
   '["ngOnInit, ngOnDestroy", "ngOnChanges", "ngAfterViewInit", "ngAfterContentInit", "Порядок выполнения", "Когда использовать"]'::text,
   '3 минуты'),
  
  ('Что такое @Input и @Output декораторы?', 2, 2,
   '["@Input для получения данных от родителя", "@Output для событий", "EventEmitter", "Property binding", "Event binding", "Two-way binding"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 3
  ('Объясните ViewChild и ViewChildren', 3, 1,
   '["Доступ к child элементам", "Template reference", "Timing и static", "Query селекторы", "read option", "QueryList"]'::text,
   '3 минуты'),
  
  ('Что такое Content Projection (ng-content)?', 3, 2,
   '["Slot для контента", "Single vs multi-slot", "select attribute", "Flexible components", "ContentChild/ContentChildren"]'::text,
   '3 минуты'),
  
  -- Difficulty 4
  ('Объясните стратегии Change Detection: Default vs OnPush', 4, 1,
   '["Default проверяет всё", "OnPush оптимизация", "Immutability", "markForCheck", "detach/reattach", "Performance benefits"]'::text,
   '3-4 минуты'),
  
  ('Как создать динамические компоненты в Angular?', 4, 2,
   '["ComponentFactoryResolver", "ViewContainerRef", "createComponent", "Injector", "Use cases", "Destroy handling"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 5
  ('Объясните Host и HostBinding/HostListener', 5, 1,
   '["Host element", "@HostBinding для свойств", "@HostListener для событий", "Host context", "Use cases в directives"]'::text,
   '3-4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'Angular Components'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ ANGULAR SERVICES & DI
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
  ('Что такое сервисы в Angular и зачем они нужны?', 1, 1,
   '["Переиспользуемая бизнес-логика", "Singleton по умолчанию", "@Injectable decorator", "Разделение concerns", "Shared state"]'::text,
   '2 минуты'),
  
  -- Difficulty 2
  ('Объясните Dependency Injection в Angular', 2, 1,
   '["Design pattern", "Injector hierarchy", "providers", "Декларация зависимостей через constructor", "Testability"]'::text,
   '3 минуты'),
  
  ('Что такое providedIn и какие значения он может принимать?', 2, 2,
   '["providedIn: root", "providedIn: any", "providedIn: Module", "Tree-shakeable providers", "Singleton vs instance per module"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 3
  ('Объясните разницу между useClass, useValue, useFactory', 3, 1,
   '["useClass для классов", "useValue для констант", "useFactory для фабрик", "useExisting для алиасов", "When to use each", "InjectionToken"]'::text,
   '3-4 минуты'),
  
  ('Что такое InjectionToken и когда его использовать?', 3, 2,
   '["Type-safe DI token", "Для non-class dependencies", "String tokens vs InjectionToken", "Tree-shakeable", "Configuration objects"]'::text,
   '3 минуты'),
  
  -- Difficulty 4
  ('Объясните иерархию инжекторов в Angular', 4, 1,
   '["Root injector", "Module injectors", "Element injectors", "Resolution rules", "Shadowing", "@Self, @SkipSelf, @Optional"]'::text,
   '4 минуты'),
  
  -- Difficulty 5
  ('Как реализовать multi-providers в Angular?', 5, 1,
   '["multi: true", "Массив providers", "Use cases (interceptors, validators)", "Order matters", "Extending functionality"]'::text,
   '3-4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'Angular Services & DI'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ ANGULAR ROUTING
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
  ('Объясните основы маршрутизации в Angular', 2, 1,
   '["RouterModule", "Routes configuration", "RouterOutlet", "routerLink", "Router service", "Navigation"]'::text,
   '2-3 минуты'),
  
  ('Как передавать параметры через маршруты?', 2, 2,
   '["Route params (:id)", "Query params", "ActivatedRoute", "paramMap", "queryParamMap", "snapshot vs observable"]'::text,
   '3 минуты'),
  
  -- Difficulty 3
  ('Что такое Guards и какие типы существуют?', 3, 1,
   '["CanActivate", "CanDeactivate", "CanLoad", "CanActivateChild", "Resolve", "Authorization и защита роутов"]'::text,
   '3 минуты'),
  
  ('Объясните Lazy Loading модулей', 3, 2,
   '["loadChildren", "Отдельные бандлы", "Preloading strategies", "Performance benefit", "Module isolation"]'::text,
   '3 минуты'),
  
  -- Difficulty 4
  ('Что такое Resolvers и когда их использовать?', 4, 1,
   '["Pre-fetch данных", "Resolve interface", "Blocking navigation", "Error handling", "vs ngOnInit fetch"]'::text,
   '3 минуты'),
  
  ('Объясните стратегии preloading в Angular Router', 4, 2,
   '["PreloadAllModules", "NoPreloading", "Custom strategies", "Network-aware preloading", "Balance performance"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 5
  ('Как реализовать вложенную маршрутизацию и child routes?', 5, 1,
   '["Children routes", "Nested RouterOutlet", "Relative navigation", "Route hierarchy", "Parent-child data sharing"]'::text,
   '4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'Angular Routing'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ RXJS
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
  ('Что такое RxJS и Observable?', 2, 1,
   '["Reactive Extensions", "Observable stream", "Push-based", "Lazy evaluation", "Multiple values over time", "vs Promise"]'::text,
   '2-3 минуты'),
  
  ('Объясните разницу между Observable, Subject, BehaviorSubject', 2, 2,
   '["Observable unicast", "Subject multicast", "BehaviorSubject с initial value", "ReplaySubject", "AsyncSubject"]'::text,
   '3 минуты'),
  
  -- Difficulty 3
  ('Что делают операторы map, filter, switchMap?', 3, 1,
   '["map трансформирует значения", "filter фильтрует", "switchMap переключает на новый Observable", "Cancellation", "Common operators"]'::text,
   '3 минуты'),
  
  ('Объясните разницу между switchMap, mergeMap, concatMap', 3, 2,
   '["switchMap отменяет предыдущие", "mergeMap параллельно", "concatMap последовательно", "exhaustMap игнорирует новые", "Use cases"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 4
  ('Как правильно отписываться от Observable?', 4, 1,
   '["unsubscribe()", "takeUntil", "take(1)", "async pipe", "Memory leaks", "Best practices", "takeUntilDestroyed"]'::text,
   '3-4 минуты'),
  
  ('Объясните операторы combineLatest, forkJoin, zip', 4, 2,
   '["combineLatest эмитит при любом изменении", "forkJoin ждет всех завершения", "zip попарно", "Use cases", "Completion logic"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 5
  ('Что такое Higher-order Observables и flattening операторы?', 5, 1,
   '["Observable of Observables", "Flattening strategies", "mergeMap, switchMap, concatMap, exhaustMap", "Inner vs outer", "Error handling"]'::text,
   '4-5 минут'),
  
  ('Объясните cold vs hot Observables', 5, 2,
   '["Cold начинает при subscribe", "Hot активны всегда", "share, shareReplay", "Multicasting", "Connectable Observables"]'::text,
   '3-4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'RxJS'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ ANGULAR FORMS
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
  ('Объясните разницу между Template-driven и Reactive Forms', 2, 1,
   '["Template-driven проще", "Reactive больше контроля", "FormsModule vs ReactiveFormsModule", "Two-way binding vs FormControl", "Когда использовать"]'::text,
   '3 минуты'),
  
  ('Что такое FormControl, FormGroup, FormArray?', 2, 2,
   '["FormControl для одного поля", "FormGroup для группы", "FormArray для динамических списков", "Nested forms", "Value и status"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 3
  ('Как работает валидация форм в Angular?', 3, 1,
   '["Built-in validators", "Custom validators", "Async validators", "Validation errors", "touched, dirty, pristine", "Error messages"]'::text,
   '3-4 минуты'),
  
  ('Объясните FormBuilder и зачем он нужен', 3, 2,
   '["Упрощение создания форм", "Shorter syntax", "Группировка", "Validators setup", "vs new FormControl"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 4
  ('Как создать custom validator в Angular?', 4, 1,
   '["ValidatorFn", "ValidationErrors", "FormControl argument", "Sync vs async", "Reusable validators", "NG_VALIDATORS"]'::text,
   '3-4 минуты'),
  
  ('Как реализовать dynamic forms (FormArray)?', 4, 2,
   '["FormArray methods", "push, removeAt, at", "Dynamic validation", "Nested FormGroups", "Use cases"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 5
  ('Объясните cross-field validation в Reactive Forms', 5, 1,
   '["Group-level validators", "Multiple field validation", "Password confirmation example", "Custom error keys", "markAsTouched propagation"]'::text,
   '3-4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'Angular Forms'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ ANGULAR HTTP
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
  ('Как работает HttpClient в Angular?', 2, 1,
   '["HttpClientModule", "Observable-based", "Type-safe", "Automatic JSON parsing", "HTTP methods (get, post, put, delete)"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 3
  ('Что такое HTTP Interceptors и как их использовать?', 3, 1,
   '["Middleware для HTTP", "HttpInterceptor interface", "intercept method", "Request/Response modification", "Use cases (auth, logging, errors)"]'::text,
   '3 минуты'),
  
  ('Как обрабатывать ошибки HTTP запросов?', 3, 2,
   '["catchError operator", "HttpErrorResponse", "Retry logic", "Global error handler", "User feedback"]'::text,
   '3 минуты'),
  
  -- Difficulty 4
  ('Как реализовать retry logic для HTTP запросов?', 4, 1,
   '["retry operator", "retryWhen", "Exponential backoff", "Conditional retry", "Error handling", "Max attempts"]'::text,
   '3-4 минуты'),
  
  ('Объясните HttpParams и HttpHeaders', 4, 2,
   '["Immutable objects", "set, append methods", "Query parameters", "Custom headers", "Authorization header", "Content-Type"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 5
  ('Как реализовать multiple interceptors и их порядок выполнения?', 5, 1,
   '["Порядок в providers", "Chain of responsibility", "next.handle()", "Request и Response flow", "Conditional execution"]'::text,
   '3-4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'Angular HTTP'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ ANGULAR STATE MANAGEMENT
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
  -- Difficulty 3
  ('Какие подходы к state management есть в Angular?', 3, 1,
   '["Services с BehaviorSubject", "NgRx", "Akita", "NGXS", "Когда нужен state management", "Pros/cons каждого"]'::text,
   '3-4 минуты'),
  
  ('Что такое NgRx и его основные концепции?', 3, 2,
   '["Redux pattern", "Store, Actions, Reducers", "Effects", "Selectors", "Immutability", "DevTools"]'::text,
   '3 минуты'),
  
  -- Difficulty 4
  ('Объясните как работают Effects в NgRx', 4, 1,
   '["Side effects handling", "@Effect decorator", "ofType operator", "Actions stream", "Dispatch новых actions", "Error handling"]'::text,
   '3-4 минуты'),
  
  ('Что такое Selectors в NgRx и зачем они нужны?', 4, 2,
   '["Queries для state", "createSelector", "Memoization", "Composition", "Performance optimization", "Reusability"]'::text,
   '3 минуты'),
  
  -- Difficulty 5
  ('Сравните NgRx, Akita и простые Services для state management', 5, 1,
   '["Boilerplate", "Learning curve", "Devtools", "Performance", "Когда использовать каждый", "Entity management"]'::text,
   '4-5 минут'),
  
  ('Объясните Entity pattern в NgRx (EntityAdapter)', 5, 2,
   '["CRUD operations", "EntityAdapter methods", "Normalized state", "selectId", "sortComparer", "Performance benefits"]'::text,
   '3-4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'Angular State Management'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ ANGULAR TESTING
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
  ('Какие инструменты используются для тестирования Angular?', 2, 1,
   '["Jasmine", "Karma", "TestBed", "Protractor/Cypress для E2E", "Jest альтернатива"]'::text,
   '2 минуты'),
  
  -- Difficulty 3
  ('Что такое TestBed и как его использовать?', 3, 1,
   '["Testing utility", "configureTestingModule", "Mock dependencies", "Create components", "Dependency Injection", "Providers override"]'::text,
   '3 минуты'),
  
  ('Как тестировать компоненты с зависимостями?', 3, 2,
   '["Mock services", "Spy objects", "provideMockStore", "HttpClientTestingModule", "Stub components", "NO_ERRORS_SCHEMA"]'::text,
   '3-4 минуты'),
  
  -- Difficulty 4
  ('Объясните как тестировать асинхронный код в Angular', 4, 1,
   '["fakeAsync", "tick", "flush", "async/await", "done callback", "Testing Observables", "marble testing"]'::text,
   '3-4 минуты'),
  
  ('Как тестировать формы в Angular?', 4, 2,
   '["setValue, patchValue", "Validation testing", "Submit events", "Error messages", "Async validators", "FormBuilder mocking"]'::text,
   '3 минуты'),
  
  -- Difficulty 5
  ('Объясните marble testing для RxJS', 5, 1,
   '["Тестирование Observable streams", "Marble diagram syntax", "TestScheduler", "Time progression", "jasmine-marbles"]'::text,
   '4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'Angular Testing'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ ANGULAR PERFORMANCE
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
  -- Difficulty 3
  ('Какие основные проблемы производительности в Angular?', 3, 1,
   '["Частые Change Detection", "Большие модули", "Heavy computations", "Memory leaks", "Bundle size"]'::text,
   '3 минуты'),
  
  ('Как OnPush Change Detection улучшает производительность?', 3, 2,
   '["Проверка только при изменении @Input", "Immutable data", "markForCheck", "Значительное ускорение", "Trade-offs"]'::text,
   '3 минуты'),
  
  -- Difficulty 4
  ('Объясните стратегии оптимизации bundle size', 4, 1,
   '["Lazy loading modules", "Tree shaking", "Production build", "Differential loading", "Remove unused code", "Bundle analyzer"]'::text,
   '3-4 минуты'),
  
  ('Как оптимизировать Change Detection в больших приложениях?', 4, 2,
   '["OnPush стратегия", "detach/reattach", "runOutsideAngular", "trackBy для ngFor", "Pure pipes", "Avoid function calls in templates"]'::text,
   '4 минуты'),
  
  -- Difficulty 5
  ('Объясните как работает Ahead-of-Time (AOT) compilation', 5, 1,
   '["Компиляция на этапе build", "vs JIT", "Smaller bundles", "Faster rendering", "Template errors at build time", "Tree-shaking benefits"]'::text,
   '3-4 минуты'),
  
  ('Опишите полную стратегию оптимизации для большого Angular приложения', 5, 2,
   '["Lazy loading", "OnPush CD", "TrackBy", "Virtual scrolling", "Web workers", "Preloading strategies", "Bundle optimization", "Monitoring"]'::text,
   '4-5 минут')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'Angular Performance'
ON CONFLICT DO NOTHING;

-- ============================================
-- ВОПРОСЫ ДЛЯ ANGULAR CLI
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
  ('Что такое Angular CLI и его основные команды?', 2, 1,
   '["ng new", "ng generate", "ng serve", "ng build", "ng test", "Scaffolding tool", "Webpack под капотом"]'::text,
   '2 минуты'),
  
  ('Как генерировать компоненты, сервисы через CLI?', 2, 2,
   '["ng generate component", "ng g service", "ng g module", "Flags (--skip-tests)", "Path specification", "Automatic imports"]'::text,
   '2-3 минуты'),
  
  -- Difficulty 3
  ('Объясните разницу между ng build и ng build --prod', 3, 1,
   '["Development vs Production", "AOT compilation", "Optimization", "Minification", "Tree-shaking", "Source maps", "Bundle sizes"]'::text,
   '3 минуты'),
  
  ('Что такое schematics в Angular CLI?', 3, 2,
   '["Code generation templates", "Custom schematics", "ng add", "Workspace schematics", "Automation", "Migration schematics"]'::text,
   '3 минуты'),
  
  -- Difficulty 4
  ('Как настроить environments в Angular?', 4, 1,
   '["environment.ts files", "fileReplacements", "Different configs", "Build configurations", "Angular.json", "Environment variables"]'::text,
   '3 минуты'),
  
  -- Difficulty 5
  ('Объясните angular.json и его основные секции', 5, 1,
   '["Workspace configuration", "projects", "architect", "build/serve/test options", "assets, styles, scripts", "Budgets", "Configurations"]'::text,
   '3-4 минуты')
) AS v(question_text, difficulty, question_number, expected_key_points, estimated_answer_time)
CROSS JOIN competencies c
WHERE c.name = 'Angular CLI'
ON CONFLICT DO NOTHING;

-- Проверка: сколько вопросов добавлено
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
