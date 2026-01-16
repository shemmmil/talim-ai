# Swagger/OpenAPI Документация

## Доступ к документации

После запуска приложения документация API доступна по следующим адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Использование для фронтенда

### Экспорт схемы

#### Вариант 1: Через endpoint

Получите схему напрямую из API:
```bash
curl http://localhost:8000/openapi.json -o openapi.json
```

#### Вариант 2: Через скрипт

Используйте скрипт для экспорта схемы:
```bash
python scripts/export_openapi.py openapi.json
```

### Генерация TypeScript типов

После получения `openapi.json` можно использовать различные инструменты для генерации TypeScript типов:

#### openapi-typescript

```bash
npx openapi-typescript openapi.json -o src/types/api.ts
```

#### openapi-generator

```bash
npx @openapitools/openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-axios \
  -o src/api
```

#### orval

```bash
npx orval --input openapi.json --output src/api
```

### Генерация API клиента

#### openapi-generator (TypeScript Axios)

```bash
npx @openapitools/openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-axios \
  -o src/api \
  --additional-properties=withInterfaces=true,modelPropertyNaming=camelCase
```

#### swagger-typescript-api

```bash
npx swagger-typescript-api -p openapi.json -o src/api -n api.ts
```

## Структура API

### Роли и компетенции

- `GET /api/roles` - Получить все роли
- `GET /api/roles/{roleId}/competencies` - Получить компетенции роли

### Тестирования (Assessments)

- `POST /api/assessments` - Начать новое тестирование
  
  ```json
  {
    "direction": "backend(golang, sql)"
  }
  ```
  
  - `direction` - текст направления (например "backend(golang, sql)", "frontend(react, typescript)")
  - Система автоматически определит компетенции для тестирования через GPT
  - Направление не хранится в БД, используется только для формирования assessment и roadmap

- `GET /api/assessments/{assessmentId}` - Получить информацию о тестировании
- `POST /api/assessments/{assessmentId}/complete` - Завершить тестирование

### Вопросы

- `POST /api/questions/generate` - Сгенерировать адаптивный вопрос динамически
  
  ```
  Form data:
  - assessment_id: uuid
  - competency_id: uuid
  - question_number: int (1-7)
  - difficulty: int (1-5, опционально)
  ```
  
  - Вопросы генерируются на основе предыдущих ответов и выявленных пробелов в знаниях
  - Вопросы не сохраняются в БД до отправки ответа

- `POST /api/questions/answer` - Отправить голосовой ответ
  
  ```
  Form data:
  - assessment_id: uuid
  - competency_id: uuid
  - question_text: string (текст вопроса, на который отвечает пользователь)
  - difficulty: int (1-5)
  - audio: file (webm, mp3, wav, m4a, ogg, максимум 25MB)
  ```
  
  - Вопрос и ответ сохраняются в БД только после отправки ответа
  - Аудио транскрибируется через Whisper API
  - Ответ оценивается через GPT-4

### Roadmaps

- `GET /api/roadmaps/{assessmentId}` - Получить roadmap по assessment
- `GET /api/roadmaps/{roadmapId}/sections` - Получить детальные секции roadmap

## Аутентификация

Аутентификация выполняется через JWT токен, передаваемый в заголовке `Authorization`.

### Формат заголовка

JWT токен передается в формате:
- `Authorization: Bearer {jwt_token}` (рекомендуется)
- `Authorization: {jwt_token}` (без префикса Bearer)

### Извлечение User ID

User ID извлекается из поля `sub` в декодированном JWT токене. Email извлекается из поля `email` (если доступно).

### Примеры

```bash
# С префиксом Bearer (рекомендуется)
curl -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3bGJDLXFSOUpmcDFYQS1YSlJVUmV1NHJsVEZhekY2Q2ZRTDlwTi0tc2FjIn0..." \
  http://localhost:8000/api/assessments

# Без префикса Bearer
curl -H "Authorization: eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3bGJDLXFSOUpmcDFYQS1YSlJVUmV1NHJsVEZhekY2Q2ZRTDlwTi0tc2FjIn0..." \
  http://localhost:8000/api/assessments
```

### Использование в Swagger UI

1. Нажмите кнопку **"Authorize"** (🔒) в правом верхнем углу
2. В поле "Value" введите ваш JWT токен:
   - С префиксом: `Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3bGJDLXFSOUpmcDFYQS1YSlJVUmV1NHJsVEZhekY2Q2ZRTDlwTi0tc2FjIn0...`
   - Или без: `eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3bGJDLXFSOUpmcDFYQS1YSlJVUmV1NHJsVEZhekY2Q2ZRTDlwTi0tc2FjIn0...`
3. Нажмите "Authorize"
4. Теперь все запросы будут использовать этот JWT токен

### Важно

- Заголовок `Authorization` **обязателен** для всех защищенных endpoints
- JWT токен должен содержать поле `sub` с user_id
- User автоматически создается в БД, если его еще нет (на основе `sub` и `email` из JWT)
- Все endpoints проверяют, что запрашиваемые ресурсы принадлежат указанному user_id

## Примеры запросов

Все примеры запросов доступны в Swagger UI. Каждый endpoint содержит:
- Описание функциональности
- Параметры запроса с описаниями
- Примеры запросов и ответов
- Коды ошибок

## Обновление схемы

При изменении API endpoints, схем или моделей:

1. Перезапустите приложение
2. Схема автоматически обновится в `/openapi.json`
3. Экспортируйте новую схему для фронтенда
4. Перегенерируйте типы/клиенты
