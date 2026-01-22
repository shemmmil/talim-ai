# Админские API для управления направлениями и технологиями

## Обзор

Админские endpoints для создания и управления направлениями, технологиями и их связями.

**Базовый путь:** `/api/admin`

---

## Endpoints

### 1. Создать направление

**POST** `/api/admin/directions`

**Тело запроса:**
```json
{
  "name": "frontend",
  "display_name": "Frontend",
  "technologies": "React|Vue|Angular",
  "description": "Frontend разработка"
}
```

**Ответ:**
```json
{
  "direction": {
    "id": "uuid",
    "name": "frontend",
    "display_name": "Frontend",
    "technologies": "React|Vue|Angular",
    "description": "Frontend разработка",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Direction created successfully"
}
```

---

### 2. Создать технологию

**POST** `/api/admin/technologies`

**Тело запроса:**
```json
{
  "name": "react",
  "description": "React библиотека для создания UI"
}
```

**Ответ:**
```json
{
  "technology": {
    "id": "uuid",
    "name": "react",
    "description": "React библиотека для создания UI",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Technology created successfully"
}
```

---

### 3. Связать технологию с направлением

**POST** `/api/admin/directions/{direction_id}/technologies/{technology_id}`

**Параметры:**
- `direction_id` (UUID) - ID направления
- `technology_id` (UUID) - ID технологии
- `order_index` (опционально, query param) - порядок отображения

**Пример:**
```bash
POST /api/admin/directions/{direction_id}/technologies/{technology_id}?order_index=1
```

**Ответ:**
```json
{
  "link": {
    "direction_id": "uuid",
    "technology_id": "uuid",
    "order_index": 1
  },
  "message": "Technology 'react' linked to direction 'frontend'"
}
```

---

### 4. Связать компетенцию с технологией

**POST** `/api/admin/technologies/{technology_id}/competencies/{competency_id}`

**Параметры:**
- `technology_id` (UUID) - ID технологии
- `competency_id` (UUID) - ID компетенции
- `order_index` (опционально, query param) - порядок отображения

**Ответ:**
```json
{
  "link": {
    "technology_id": "uuid",
    "competency_id": "uuid",
    "order_index": 1
  },
  "message": "Competency linked to technology 'react'"
}
```

---

### 5. Связать компетенцию с направлением

**POST** `/api/admin/directions/{direction_id}/competencies/{competency_id}`

**Параметры:**
- `direction_id` (UUID) - ID направления
- `competency_id` (UUID) - ID компетенции
- `order_index` (опционально, query param) - порядок отображения

**Ответ:**
```json
{
  "link": {
    "direction_id": "uuid",
    "competency_id": "uuid",
    "order_index": 1
  },
  "message": "Competency linked to direction 'frontend'"
}
```

---

### 6. Массовое добавление технологий к направлению

**POST** `/api/admin/directions/{direction_id}/technologies/batch`

**Тело запроса:**
```json
{
  "technology_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Ответ:**
```json
{
  "links": [
    {"direction_id": "uuid", "technology_id": "uuid1", "order_index": 1},
    {"direction_id": "uuid", "technology_id": "uuid2", "order_index": 2},
    {"direction_id": "uuid", "technology_id": "uuid3", "order_index": 3}
  ],
  "message": "Linked 3 technologies to direction 'frontend'"
}
```

---

## Примеры использования

### Создание Frontend направления с технологиями

```javascript
// 1. Создать направление
const direction = await fetch('/api/admin/directions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userId}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'frontend',
    display_name: 'Frontend',
    description: 'Frontend разработка'
  })
}).then(r => r.json());

const directionId = direction.direction.id;

// 2. Создать технологии
const react = await fetch('/api/admin/technologies', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userId}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'react',
    description: 'React библиотека'
  })
}).then(r => r.json());

const vue = await fetch('/api/admin/technologies', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userId}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'vue',
    description: 'Vue.js фреймворк'
  })
}).then(r => r.json());

// 3. Связать технологии с направлением
await fetch(
  `/api/admin/directions/${directionId}/technologies/${react.technology.id}?order_index=1`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${userId}`
    }
  }
);

await fetch(
  `/api/admin/directions/${directionId}/technologies/${vue.technology.id}?order_index=2`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${userId}`
    }
  }
);
```

### Использование batch endpoint

```javascript
const directionId = '...';
const technologyIds = ['uuid1', 'uuid2', 'uuid3'];

await fetch(
  `/api/admin/directions/${directionId}/technologies/batch`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${userId}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      technology_ids: technologyIds
    })
  }
);
```

---

## Порядок заполнения данных

1. **Создать направления** (если еще нет)
   ```bash
   POST /api/admin/directions
   ```

2. **Создать технологии** (если еще нет)
   ```bash
   POST /api/admin/technologies
   ```

3. **Связать технологии с направлениями**
   ```bash
   POST /api/admin/directions/{direction_id}/technologies/{technology_id}
   ```

4. **Создать компетенции** (через существующие endpoints или напрямую в БД)

5. **Связать компетенции с технологиями** (для специфичных компетенций)
   ```bash
   POST /api/admin/technologies/{technology_id}/competencies/{competency_id}
   ```

6. **Связать компетенции с направлениями** (для общих компетенций)
   ```bash
   POST /api/admin/directions/{direction_id}/competencies/{competency_id}
   ```

---

## Примечания

- Все endpoints требуют авторизации через заголовок `Authorization: Bearer {user_id}`
- Если направление/технология уже существует, метод `find_or_create` вернет существующую запись
- При попытке создать дублирующую связь будет ошибка (уникальный ключ)
- `order_index` используется для сортировки при отображении

---

## Быстрое заполнение для Frontend

```bash
# 1. Создать направление Frontend
curl -X POST http://localhost:8000/api/admin/directions \
  -H "Authorization: Bearer {user_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "frontend",
    "display_name": "Frontend",
    "description": "Frontend разработка"
  }'

# 2. Создать технологии
curl -X POST http://localhost:8000/api/admin/technologies \
  -H "Authorization: Bearer {user_id}" \
  -H "Content-Type: application/json" \
  -d '{"name": "react", "description": "React"}'

curl -X POST http://localhost:8000/api/admin/technologies \
  -H "Authorization: Bearer {user_id}" \
  -H "Content-Type: application/json" \
  -d '{"name": "vue", "description": "Vue.js"}'

# 3. Связать технологии с направлением (используйте ID из ответов выше)
curl -X POST "http://localhost:8000/api/admin/directions/{direction_id}/technologies/{react_id}?order_index=1" \
  -H "Authorization: Bearer {user_id}"

curl -X POST "http://localhost:8000/api/admin/directions/{direction_id}/technologies/{vue_id}?order_index=2" \
  -H "Authorization: Bearer {user_id}"
```
