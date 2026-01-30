# API v2 - Улучшения архитектуры

## Обзор изменений

Версия 1.2.0 вводит улучшенную структуру API с более RESTful подходом и упрощенными флоу для клиентов.

---

## 🆕 Новые endpoints

### 1. Catalog API (Справочники)

Новый модуль для получения справочной информации о направлениях и технологиях.

#### `GET /api/catalog/directions`

Оптимизированный endpoint - возвращает направления с вложенными технологиями одним запросом.

**Query параметры:**
- `include_technologies` (boolean, default: true) - включить список технологий

**Ответ:**
```json
{
  "directions": [
    {
      "id": "uuid",
      "name": "frontend",
      "display_name": "Frontend",
      "description": "Frontend development",
      "technologies": [
        {
          "id": "uuid",
          "name": "react",
          "description": "React library",
          "order_index": 0
        },
        {
          "id": "uuid",
          "name": "angular",
          "description": "Angular framework",
          "order_index": 1
        }
      ]
    }
  ]
}
```

**Преимущества:**
- ✅ Один запрос вместо N+1 (было: 1 запрос directions + N запросов technologies)
- ✅ Меньше латентности
- ✅ Упрощенная логика на клиенте

#### `GET /api/catalog/technologies/{technology_id}`

Получить детали конкретной технологии.

#### `GET /api/catalog/roles` (deprecated)

Старый endpoint для ролей. Оставлен для обратной совместимости, но помечен как deprecated.

---

### 2. Assessment Restart

#### `POST /api/assessments/{assessment_id}/restart`

Перезапустить assessment с теми же параметрами.

**Что делает:**
- Создает новый assessment с теми же direction + technology
- Увеличивает attempt_number (попытка 3 → попытка 4)
- Возвращает те же компетенции
- Новый UUID и статус 'in_progress'

**Пример:**
```bash
POST /api/assessments/3a12daad-abee-46ef-86c6-eb45c41c8e03/restart
Authorization: Bearer user-id

# Ответ: новый assessment с attempt_number = 4
{
  "assessment_id": "новый-uuid",
  "competencies": [...],  // те же компетенции
  "status": "in_progress"
}
```

**Преимущества:**
- ✅ Не нужно помнить параметры старого assessment
- ✅ Автоматическое увеличение attempt_number
- ✅ Сохранение истории всех попыток

---

### 3. Assessment Abandonment

#### `DELETE /api/assessments/{assessment_id}`

Отменить/бросить assessment (soft delete).

**Что делает:**
- Устанавливает статус 'abandoned'
- НЕ удаляет данные физически (для статистики)
- Нельзя отменить уже завершенный assessment

**Пример:**
```bash
DELETE /api/assessments/3a12daad-abee-46ef-86c6-eb45c41c8e03
Authorization: Bearer user-id

# Ответ
{
  "message": "Assessment abandoned",
  "assessment": {
    "id": "...",
    "status": "abandoned",
    ...
  }
}
```

**Use cases:**
- Пользователь начал тестирование, но передумал
- Начали не то направление/технологию
- Хотят начать заново (вместо restart, если еще не ответили ни на один вопрос)

---

### 4. RESTful Question Endpoints

Новые альтернативные пути для работы с вопросами - более RESTful структура.

#### `POST /api/assessments/{assessment_id}/questions`

Получить следующий вопрос (альтернатива `/api/questions/generate`).

**Параметры (FormData):**
- `competency_id` (UUID) - ID компетенции
- `question_number` (int, 1-5) - номер вопроса
- `difficulty` (int, 1-5, optional) - уровень сложности

**Преимущества:**
- ✅ Более RESTful путь: `/assessments/{id}/questions`
- ✅ Логика идентична старому endpoint
- ✅ Обратная совместимость сохранена

#### `POST /api/assessments/{assessment_id}/answers`

Отправить ответ на вопрос (альтернатива `/api/questions/answer`).

**Параметры (FormData):**
- `competency_id` (UUID)
- `question_text` (string)
- `difficulty` (int, 1-5)
- `question_id` (UUID, optional)
- `audio` (file) - аудио файл

**Новая функция: Авто-завершение assessment**

Если это был последний вопрос (все компетенции протестированы), assessment автоматически завершается:

```json
{
  "transcript": "...",
  "evaluation": {...},
  "assessment_auto_completed": true,  // ⭐ Новое поле
  "overall_score": 3.8                 // ⭐ Новое поле
}
```

**Преимущества:**
- ✅ RESTful структура
- ✅ Автоматическое завершение (меньше запросов от клиента)
- ✅ Обратная совместимость

---

## 📊 Сравнение: старый vs новый флоу

### Старый флоу (v1.0)

```
1. GET /api/assessments/directions
   → {directions: [...]}

2. GET /api/assessments/directions/{id}/technologies
   → {technologies: [...]}

3. POST /api/assessments
   Body: {direction: "frontend", technology: "react"}
   → {assessment_id, competencies, status}

4. Для каждого вопроса:
   POST /api/questions/generate
   POST /api/questions/answer

5. POST /api/assessments/{id}/complete
```

**Всего:** 5+ запросов до начала тестирования, +1 в конце

---

### Новый флоу (v1.2)

```
1. GET /api/catalog/directions?include_technologies=true
   → {directions: [{..., technologies: [...]}]}  // Все сразу!

2. POST /api/assessments
   Body: {direction: "frontend", technology: "react"}
   → {assessment_id, competencies, status}

3. Для каждого вопроса:
   POST /api/assessments/{id}/questions
   POST /api/assessments/{id}/answers
   → {..., assessment_auto_completed: true}  // Авто-завершение!

4. (опционально) POST /api/assessments/{id}/complete
   Только если авто-complete не сработал
```

**Всего:** 2 запроса до начала тестирования, 0 в конце (авто-complete)

**Экономия:** 50% запросов! 🎉

---

### Перезапуск assessment

#### Старый флоу (v1.0)

```
1. GET /api/assessments/{old_id}
   → Получить direction и technology

2. Вручную извлечь имена из ответа

3. POST /api/assessments
   Body: {direction: "frontend", technology: "react"}
   → Создать новый assessment
```

**Проблемы:**
- ❌ Клиент должен помнить параметры
- ❌ Можно ошибиться с именами
- ❌ 2 запроса

#### Новый флоу (v1.2)

```
1. POST /api/assessments/{old_id}/restart
   → {assessment_id, competencies, status}
```

**Преимущества:**
- ✅ Один запрос
- ✅ Автоматическое копирование параметров
- ✅ Гарантированно правильные параметры

---

## 🔄 Обратная совместимость

Все старые endpoints продолжают работать:

| Старый endpoint | Статус | Новый endpoint | Миграция |
|----------------|--------|----------------|----------|
| `GET /api/assessments/directions` | ✅ Работает | `GET /api/catalog/directions` | Рекомендуется |
| `GET /api/assessments/directions/{id}/technologies` | ✅ Работает | `GET /api/catalog/directions?include_technologies=true` | Рекомендуется |
| `GET /api/assessments/technologies/{id}/competencies` | ✅ Работает | - | Оставить как есть |
| `POST /api/questions/generate` | ✅ Работает | `POST /api/assessments/{id}/questions` | Опционально |
| `POST /api/questions/answer` | ✅ Работает | `POST /api/assessments/{id}/answers` | Опционально |
| `GET /api/roles` | ⚠️ Deprecated | `GET /api/catalog/roles` | Перейти на directions |

---

## 📝 Примеры использования

### Пример 1: Получить каталог направлений

```bash
# Новый способ (рекомендуется)
curl http://localhost:8000/api/catalog/directions?include_technologies=true

# Старый способ (работает, но медленнее)
curl http://localhost:8000/api/assessments/directions
curl http://localhost:8000/api/assessments/directions/{id}/technologies
```

### Пример 2: Создать и пройти assessment

```bash
# 1. Получить каталог
curl http://localhost:8000/api/catalog/directions?include_technologies=true

# 2. Создать assessment
curl -X POST http://localhost:8000/api/assessments \
  -H "Authorization: Bearer user-id" \
  -H "Content-Type: application/json" \
  -d '{"direction": "frontend", "technology": "react"}'

# 3. Получить вопрос (новый endpoint)
curl -X POST http://localhost:8000/api/assessments/{assessment_id}/questions \
  -H "Authorization: Bearer user-id" \
  -F "competency_id={competency_id}" \
  -F "question_number=1"

# 4. Отправить ответ (новый endpoint с авто-complete)
curl -X POST http://localhost:8000/api/assessments/{assessment_id}/answers \
  -H "Authorization: Bearer user-id" \
  -F "competency_id={competency_id}" \
  -F "question_text=..." \
  -F "difficulty=3" \
  -F "audio=@answer.webm"
# Ответ: {..., assessment_auto_completed: true, overall_score: 3.8}

# 5. Завершение не нужно! (авто-complete сработал)
```

### Пример 3: Перезапустить assessment

```bash
# Получить старый assessment
curl http://localhost:8000/api/assessments/{old_id} \
  -H "Authorization: Bearer user-id"

# Перезапустить одним запросом
curl -X POST http://localhost:8000/api/assessments/{old_id}/restart \
  -H "Authorization: Bearer user-id"

# Ответ: новый assessment с attempt_number++
```

### Пример 4: Отменить assessment

```bash
# Отменить незавершенный assessment
curl -X DELETE http://localhost:8000/api/assessments/{id} \
  -H "Authorization: Bearer user-id"

# Ответ: {message: "Assessment abandoned", assessment: {..., status: "abandoned"}}
```

---

## 🎯 Рекомендации по миграции

### Для фронтенд разработчиков

1. **Немедленно:** Начать использовать `/api/catalog/directions` вместо старых endpoints
2. **Опционально:** Перейти на новые RESTful пути для вопросов/ответов
3. **Добавить:** Обработку авто-завершения assessment
4. **Добавить:** Кнопку "Начать заново" с `/restart` endpoint

### Для бэкенд разработчиков

1. **Ничего не ломать:** Все старые endpoints работают
2. **Тестировать:** Новые endpoints параллельно со старыми
3. **Мониторить:** Использование deprecated endpoints
4. **Планировать:** Удаление deprecated endpoints в v2.0

---

## 🚀 Roadmap

### v1.2.0 (текущая версия)
- ✅ Catalog API
- ✅ Assessment restart
- ✅ Assessment abandonment
- ✅ RESTful question endpoints
- ✅ Auto-complete для assessments

### v1.3.0 (планируется)
- [ ] Batch question generation (получить 5 вопросов сразу)
- [ ] WebSocket для real-time прогресса
- [ ] Улучшенная аналитика
- [ ] Export результатов (PDF, CSV)

### v2.0.0 (будущее)
- [ ] Удалить deprecated endpoints
- [ ] GraphQL API
- [ ] Versioned API (v1, v2)
- [ ] Breaking changes с миграцией

---

## 📚 Дополнительные ресурсы

- [Основная документация](../README.md)
- [API Docs (Swagger)](http://localhost:8000/docs)
- [Data Optimization](DATA_OPTIMIZATION.md)
- [Changelog](../CHANGELOG.md)
