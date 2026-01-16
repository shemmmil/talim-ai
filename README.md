# Talim AI - Backend для тестирования компетенций

Backend на Python для системы AI-тестирования профессиональных компетенций через голосовое собеседование.

## Описание

Система для объективной оценки профессиональных компетенций через адаптивное голосовое AI-тестирование:

1. Пользователь выбирает роль (например, "Backend Developer", "Аналитик")
2. Проходит адаптивное голосовое тестирование по компетенциям
3. AI анализирует ответы и формирует персональный roadmap развития

## Технологический стек

- **Python 3.11+**
- **FastAPI** - async framework для API
- **Supabase** - PostgreSQL + Auth + Storage
- **OpenAI API** - Whisper (STT) + GPT-4 (генерация вопросов и анализ)
- **Pydantic v2** - валидация данных

## Структура проекта

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI приложение
│   ├── config.py            # Настройки (env variables)
│   ├── database.py          # Supabase connection
│   │
│   ├── models/              # Pydantic модели
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── competency.py
│   │   ├── assessment.py
│   │   └── roadmap.py
│   │
│   ├── schemas/             # Pydantic схемы для API
│   │   ├── user.py
│   │   ├── assessment.py
│   │   └── roadmap.py
│   │
│   ├── api/                 # API endpoints
│   │   ├── deps.py          # Dependencies
│   │   ├── roles.py
│   │   ├── assessments.py
│   │   ├── questions.py
│   │   └── roadmaps.py
│   │
│   ├── services/            # Бизнес-логика
│   │   ├── openai_service.py
│   │   ├── supabase_service.py
│   │   ├── assessment_service.py
│   │   └── roadmap_service.py
│   │
│   └── utils/
│       └── audio.py         # Обработка аудио
│
├── requirements.txt
├── .env.example
└── README.md
```

## Установка и запуск

### 1. Клонирование и установка зависимостей

```bash
# Установить зависимости (используйте python3 -m pip или pip3)
python3 -m pip install -r requirements.txt

# Или если pip3 доступен:
# pip3 install -r requirements.txt
```

**Важно**: Используйте `python3 -m pip` вместо `pip`, чтобы убедиться что используется правильная версия Python (3.11+).

### 2. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_api_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000
```

**Важно: Получение Supabase ключей**

1. Откройте [Supabase Dashboard](https://app.supabase.com)
2. Выберите ваш проект
3. Перейдите в **Settings** → **API**
4. В разделе **Project API keys** скопируйте один из ключей:
   - **`sb_publishable_...`** или **`anon` `public`** - для клиентской стороны
   - **`sb_secret_...`** или **`service_role`** - для серверной стороны (рекомендуется для backend, больше прав)

**Форматы ключей:**
- **Новый формат** (рекомендуется): `sb_publishable_...` или `sb_secret_...` - поддерживается в supabase-py >= 2.27.0
- **Старый формат** (JWT): `eyJ...` - JWT токены длиной 200+ символов

**Для серверной стороны (backend)** рекомендуется использовать `sb_secret_...` или `service_role` ключ.

### 3. Настройка базы данных Supabase

Создайте таблицы в Supabase согласно SQL схемам из описания проекта (см. раздел "Структура БД в Supabase").

### 4. Запуск приложения

```bash
# Запуск через uvicorn (рекомендуется)
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Или если uvicorn установлен глобально:
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Или напрямую через Python (запустит uvicorn из кода)
python3 -m app.main
```

Приложение будет доступно по адресу: `http://localhost:8000`

### 5. Доступ к документации API

После запуска приложения доступна документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

Подробная информация о работе со Swagger/OpenAPI для фронтенда: [docs/SWAGGER.md](docs/SWAGGER.md)

## API Endpoints

### Roles & Competencies (Направления)

- `GET /api/roles` - Получить все направления (роли)
- `GET /api/roles/{roleId}/competencies` - Получить компетенции для направления

**Примечание:** В системе "направление" (direction) - это то же самое, что "роль" (role) в базе данных. 
Направление определяет набор компетенций для тестирования и формирования roadmap.

### Assessments

- `POST /api/assessments` - Начать новое тестирование для направления

  ```json
  {
    "direction": "backend(golang, sql)"
  }
  ```
  
  - `direction` - текст направления (например "backend(golang, sql)", "frontend(react, typescript)")
  - Система автоматически определит компетенции для тестирования через GPT
  - Направление не хранится в БД, используется только для формирования assessment и roadmap

- `GET /api/assessments/{assessmentId}` - Получить состояние тестирования

- `POST /api/assessments/{assessmentId}/complete` - Завершить тестирование

### Questions

- `POST /api/questions/generate` - Сгенерировать вопрос динамически

  ```
  Form data:
  - assessment_id: uuid
  - competency_id: uuid
  - question_number: int (1-7)
  - difficulty: int (optional, 1-5)
  ```
  
  **Важно:** Вопрос генерируется на основе предыдущих ответов и **НЕ сохраняется** в БД при генерации.

- `POST /api/questions/answer` - Отправить голосовой ответ
  
  ```
  Form data:
  - assessment_id: uuid
  - competency_id: uuid
  - question_text: string
  - difficulty: int (1-5)
  - audio: File (webm/mp3/wav/m4a/ogg)
  ```
  
  **Важно:** Вопрос и ответ сохраняются в БД **только после отправки ответа**.

### Roadmaps

- `GET /api/roadmaps/{assessmentId}` - Получить roadmap для assessment

- `GET /api/roadmaps/{roadmapId}/sections` - Получить детальные секции roadmap

## Основной flow тестирования

1. **Выбор роли**: Пользователь выбирает роль через `GET /api/roles`

2. **Начало тестирования**: `POST /api/assessments` создает новое тестирование и возвращает список компетенций

3. **Генерация вопросов**: Для каждой компетенции:

   - `POST /api/questions/generate` - генерирует вопрос через GPT-4
   - Пользователь записывает голосовой ответ
   - `POST /api/questions/{questionId}/answer` - отправляет аудио, получает оценку

4. **Адаптивная сложность**: На основе оценки предыдущих ответов система адаптирует сложность следующих вопросов

5. **Завершение**: `POST /api/assessments/{assessmentId}/complete` завершает тестирование

6. **Roadmap**: `GET /api/roadmaps/{assessmentId}` генерирует персональный план развития

## Интеграция с OpenAI

Система использует:

- **Whisper API** для транскрипции голосовых ответов
- **GPT-4** для:
  - Генерации адаптивных вопросов
  - Оценки ответов кандидатов
  - Формирования персональных roadmaps

Промпты для GPT-4 оптимизированы для оценки технических компетенций и выявления пробелов в знаниях.

## Аутентификация

User ID передается с фронтенда в заголовке `Authorization`.

### Форматы:

- `Authorization: Bearer {user_id}` (рекомендуется)
- `Authorization: {user_id}` (простой формат)

### Пример использования:

```javascript
fetch("/api/assessments", {
  headers: {
    Authorization: `Bearer ${userId}`,
  },
});
```

Backend извлекает user_id из заголовка и использует его для проверки доступа к ресурсам.
Все endpoints требуют передачи user_id в заголовке Authorization.

## Обработка аудио

Поддерживаемые форматы:

- `.webm`
- `.mp3`
- `.wav`
- `.m4a`
- `.ogg`

Максимальный размер файла: 25 MB (настраивается в `config.py`)

## Разработка

### Линтинг и форматирование

```bash
# Рекомендуется использовать black и flake8
black app/
flake8 app/
```

### Тестирование

```bash
# TODO: Добавить тесты
pytest tests/
```

## Зависимости

Основные зависимости указаны в `requirements.txt`:

- fastapi
- uvicorn
- supabase
- openai
- pydantic
- python-multipart (для загрузки файлов)

## Лицензия

См. файл LICENSE

## Контакты

Для вопросов и предложений создавайте issues в репозитории.
