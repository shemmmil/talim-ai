# Быстрый старт для фронтенда

## Основные изменения

**Раньше:**

```json
POST /api/assessments
{ "direction": "backend(golang, sql)" }
```

**Теперь:**

```json
POST /api/assessments
{
  "direction": "backend",      // обязательно
  "technology": "go"           // опционально
}
```

## Минимальный пример

```javascript
// 1. Получить направления
const directions = await fetch("/api/assessments/directions", {
  headers: { Authorization: `Bearer ${userId}` },
}).then((r) => r.json());

// 2. Получить технологии для направления (опционально)
const directionId = directions.directions[0].id;
const technologies = await fetch(
  `/api/assessments/directions/${directionId}/technologies`,
  { headers: { Authorization: `Bearer ${userId}` } }
).then((r) => r.json());

// 3. Создать assessment
const assessment = await fetch("/api/assessments", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${userId}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    direction: "backend",
    technology: "go", // можно не указывать
  }),
}).then((r) => r.json());
```

## Endpoints

| Метод | Endpoint                                          | Описание               |
| ----- | ------------------------------------------------- | ---------------------- |
| GET   | `/api/assessments/directions`                     | Список направлений     |
| GET   | `/api/assessments/directions/{id}/technologies`   | Технологии направления |
| GET   | `/api/assessments/technologies/{id}/competencies` | Компетенции технологии |
| POST  | `/api/assessments`                                | Создать тестирование   |

## Важно

- `technology` - **опциональное** поле
- Если не указано - используются общие компетенции направления
- Имена в lowercase: `"backend"`, `"go"`, `"react"`

Подробная документация: [FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md)
