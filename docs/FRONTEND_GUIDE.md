# Инструкция для фронтенда - Talim AI API

## Обзор

API поддерживает двухуровневую структуру выбора:
1. **Направление** (обязательно) - например: `backend`, `frontend`, `mobile`
2. **Технология** (опционально) - например: `go`, `php`, `python`, `react`, `vue`

## Основные изменения

### Раньше:
```json
{
  "direction": "backend(golang, sql)"
}
```

### Теперь:
```json
{
  "direction": "backend",
  "technology": "go"  // опционально
}
```

---

## API Endpoints

### 1. Получить список всех направлений

**GET** `/api/assessments/directions`

**Ответ:**
```json
{
  "directions": [
    {
      "id": "uuid",
      "name": "backend",
      "display_name": "Backend",
      "technologies": "Go|PHP|Python|Node.js",
      "description": "Backend разработка",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "name": "frontend",
      "display_name": "Frontend",
      "technologies": "React|Vue|Angular",
      "description": "Frontend разработка",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Пример использования:**
```javascript
const response = await fetch('/api/assessments/directions', {
  headers: {
    'Authorization': `Bearer ${userId}`
  }
});
const data = await response.json();
const directions = data.directions;
```

---

### 2. Получить технологии для направления

**GET** `/api/assessments/directions/{direction_id}/technologies`

**Параметры:**
- `direction_id` (UUID) - ID направления

**Ответ:**
```json
{
  "direction": {
    "id": "uuid",
    "name": "backend",
    "display_name": "Backend"
  },
  "technologies": [
    {
      "id": "uuid",
      "name": "go",
      "description": "Go programming language",
      "order_index": 1
    },
    {
      "id": "uuid",
      "name": "php",
      "description": "PHP programming language",
      "order_index": 2
    },
    {
      "id": "uuid",
      "name": "python",
      "description": "Python programming language",
      "order_index": 3
    }
  ]
}
```

**Пример использования:**
```javascript
const directionId = '...'; // ID выбранного направления
const response = await fetch(
  `/api/assessments/directions/${directionId}/technologies`,
  {
    headers: {
      'Authorization': `Bearer ${userId}`
    }
  }
);
const data = await response.json();
const technologies = data.technologies;
```

---

### 3. Получить компетенции для технологии

**GET** `/api/assessments/technologies/{technology_id}/competencies`

**Параметры:**
- `technology_id` (UUID) - ID технологии

**Ответ:**
```json
{
  "technology": {
    "id": "uuid",
    "name": "go",
    "description": "Go programming language"
  },
  "competencies": [
    {
      "id": "uuid",
      "name": "Go Basics",
      "description": "Основы языка Go",
      "category": "Языки программирования",
      "order_index": 1
    },
    {
      "id": "uuid",
      "name": "Concurrency",
      "description": "Горутины и каналы",
      "category": "Продвинутые темы",
      "order_index": 2
    }
  ]
}
```

**Пример использования:**
```javascript
const technologyId = '...'; // ID выбранной технологии
const response = await fetch(
  `/api/assessments/technologies/${technologyId}/competencies`,
  {
    headers: {
      'Authorization': `Bearer ${userId}`
    }
  }
);
const data = await response.json();
const competencies = data.competencies;
```

---

### 4. Получить общие компетенции для направления

**GET** `/api/assessments/directions/{direction_id}/competencies`

**Параметры:**
- `direction_id` (UUID) - ID направления

**Используйте этот endpoint**, если пользователь не выбрал конкретную технологию.

**Ответ:** Аналогичен ответу из endpoint для технологий.

---

### 5. Создать новое тестирование

**POST** `/api/assessments`

**Заголовки:**
```
Authorization: Bearer {user_id}
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "direction": "backend",        // обязательное поле
  "technology": "go"             // опциональное поле
}
```

**Варианты использования:**

1. **С технологией** (рекомендуется):
```json
{
  "direction": "backend",
  "technology": "go"
}
```
→ Используются компетенции, специфичные для технологии Go

2. **Без технологии**:
```json
{
  "direction": "backend"
}
```
→ Используются общие компетенции для направления Backend

**Ответ:**
```json
{
  "assessment_id": "uuid",
  "competencies": [
    {
      "id": "uuid",
      "name": "Go Basics",
      "description": "Основы языка Go",
      "category": "Языки программирования",
      "importance_weight": 3,
      "order_index": 1
    }
  ],
  "status": "in_progress"
}
```

**Пример использования:**
```javascript
const response = await fetch('/api/assessments', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userId}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    direction: 'backend',
    technology: 'go'  // опционально
  })
});

const data = await response.json();
const assessmentId = data.assessment_id;
const competencies = data.competencies;
```

---

## Рекомендуемый UX Flow

### Вариант 1: Двухэтапный выбор (рекомендуется)

1. **Шаг 1: Выбор направления**
   ```javascript
   // Получаем список направлений
   const directions = await getDirections();
   
   // Пользователь выбирает направление
   const selectedDirection = directions.find(d => d.name === 'backend');
   ```

2. **Шаг 2: Выбор технологии (опционально)**
   ```javascript
   // Получаем технологии для выбранного направления
   const technologies = await getDirectionTechnologies(selectedDirection.id);
   
   // Показываем пользователю список технологий
   // Пользователь может выбрать технологию или пропустить
   const selectedTechnology = technologies.find(t => t.name === 'go');
   ```

3. **Шаг 3: Создание assessment**
   ```javascript
   const assessment = await createAssessment({
     direction: selectedDirection.name,
     technology: selectedTechnology?.name  // опционально
   });
   ```

### Вариант 2: Комбинированный выбор

```javascript
// Показываем все направления с их технологиями
const directions = await getDirections();

for (const direction of directions) {
  const technologies = await getDirectionTechnologies(direction.id);
  direction.technologies = technologies;
}

// Пользователь выбирает направление и технологию одновременно
// Затем создаем assessment
```

---

## Примеры компонентов (React)

### Компонент выбора направления

```jsx
import { useState, useEffect } from 'react';

function DirectionSelector({ onSelect }) {
  const [directions, setDirections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/assessments/directions', {
      headers: {
        'Authorization': `Bearer ${userId}`
      }
    })
      .then(res => res.json())
      .then(data => {
        setDirections(data.directions);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Загрузка...</div>;

  return (
    <div>
      <h2>Выберите направление</h2>
      {directions.map(direction => (
        <button
          key={direction.id}
          onClick={() => onSelect(direction)}
        >
          {direction.display_name}
        </button>
      ))}
    </div>
  );
}
```

### Компонент выбора технологии

```jsx
function TechnologySelector({ directionId, onSelect, onSkip }) {
  const [technologies, setTechnologies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!directionId) return;

    fetch(`/api/assessments/directions/${directionId}/technologies`, {
      headers: {
        'Authorization': `Bearer ${userId}`
      }
    })
      .then(res => res.json())
      .then(data => {
        setTechnologies(data.technologies);
        setLoading(false);
      });
  }, [directionId]);

  if (loading) return <div>Загрузка...</div>;

  return (
    <div>
      <h2>Выберите технологию (опционально)</h2>
      {technologies.map(tech => (
        <button
          key={tech.id}
          onClick={() => onSelect(tech)}
        >
          {tech.name}
        </button>
      ))}
      <button onClick={onSkip}>
        Пропустить (общие компетенции)
      </button>
    </div>
  );
}
```

### Компонент создания assessment

```jsx
function CreateAssessment({ direction, technology }) {
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    setLoading(true);
    
    try {
      const response = await fetch('/api/assessments', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userId}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          direction: direction.name,
          technology: technology?.name
        })
      });

      const data = await response.json();
      setAssessment(data);
    } catch (error) {
      console.error('Ошибка создания assessment:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleCreate} disabled={loading}>
        {loading ? 'Создание...' : 'Начать тестирование'}
      </button>
      
      {assessment && (
        <div>
          <p>Assessment ID: {assessment.assessment_id}</p>
          <p>Компетенций: {assessment.competencies.length}</p>
        </div>
      )}
    </div>
  );
}
```

---

## Обработка ошибок

### Ошибка: Направление не найдено
```json
{
  "detail": "Direction not found"
}
```
**Решение:** Проверьте, что направление существует в списке направлений.

### Ошибка: Технология не найдена
```json
{
  "detail": "Technology not found"
}
```
**Решение:** Проверьте, что технология доступна для выбранного направления.

### Ошибка: Нет компетенций
```json
{
  "detail": "No competencies found for technology 'go' in direction 'backend'. Please add competencies to the technology first."
}
```
**Решение:** Это означает, что для выбранной комбинации направления и технологии еще не добавлены компетенции в БД. Используйте общие компетенции направления или выберите другую технологию.

---

## Типы данных (TypeScript)

```typescript
interface Direction {
  id: string;
  name: string;
  display_name: string;
  technologies?: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

interface Technology {
  id: string;
  name: string;
  description?: string;
  order_index?: number;
}

interface Competency {
  id: string;
  name: string;
  description?: string;
  category?: string;
  importance_weight?: number;
  order_index?: number;
}

interface AssessmentCreate {
  direction: string;        // обязательное
  technology?: string;      // опциональное
}

interface AssessmentStartResponse {
  assessment_id: string;
  competencies: Competency[];
  status: string;
}
```

---

## Чеклист для фронтенда

- [ ] Реализован компонент выбора направления
- [ ] Реализован компонент выбора технологии (опционально)
- [ ] Добавлена возможность пропустить выбор технологии
- [ ] Реализована обработка ошибок
- [ ] Добавлены индикаторы загрузки
- [ ] Проверена работа с опциональным полем `technology`
- [ ] Добавлена валидация выбранных значений
- [ ] Реализован переход к тестированию после создания assessment

---

## Дополнительные заметки

1. **Поле `technology` опционально** - если не указано, используются общие компетенции направления
2. **Имена направлений и технологий** чувствительны к регистру - используйте lowercase (`backend`, `go`)
3. **Кэширование** - рекомендуется кэшировать списки направлений и технологий, так как они редко меняются
4. **Порядок отображения** - используйте `order_index` для правильной сортировки

---

## Вопросы и поддержка

При возникновении проблем проверьте:
1. Правильность заголовка `Authorization`
2. Формат данных в запросе (JSON)
3. Существование выбранного направления/технологии в БД
4. Наличие компетенций для выбранной комбинации
