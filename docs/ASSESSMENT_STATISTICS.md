# Статистика и результаты Assessment

## Обзор

После завершения assessment доступны следующие endpoints для получения статистики и результатов.

## Endpoints

### 1. Завершить Assessment

**POST** `/api/assessments/{assessment_id}/complete`

Завершает тестирование, вычисляет общий балл и устанавливает статус `completed`.

**Параметры:**
- `assessment_id` (path) - UUID assessment

**Ответ:**
```json
{
  "message": "Assessment completed",
  "assessment": {
    "id": "uuid",
    "user_id": "uuid",
    "status": "completed",
    "overall_score": 3.5,
    "started_at": "2024-01-01T10:00:00",
    "completed_at": "2024-01-01T11:30:00"
  }
}
```

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/assessments/{assessment_id}/complete" \
  -H "Authorization: Bearer {token}"
```

---

### 2. Получить детальную информацию о Assessment

**GET** `/api/assessments/{assessment_id}`

Возвращает полную информацию о assessment, включая оценки по всем компетенциям и статистику.

**Параметры:**
- `assessment_id` (path) - UUID assessment

**Ответ:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "role_id": "uuid",
  "role_name": "Backend Developer",
  "status": "completed",
  "overall_score": 3.5,
  "started_at": "2024-01-01T10:00:00",
  "completed_at": "2024-01-01T11:30:00",
  "competency_assessments": [
    {
      "id": "uuid",
      "competency_id": "uuid",
      "competency_name": "Go Basics",
      "ai_assessed_score": 4,
      "confidence_level": "high",
      "gap_analysis": {
        "knowledgeGaps": ["Concurrency patterns", "Error handling"],
        "strengths": ["Basic syntax", "Functions"]
      },
      "completed_at": "2024-01-01T11:00:00"
    },
    {
      "id": "uuid",
      "competency_id": "uuid",
      "competency_name": "Go Concurrency",
      "ai_assessed_score": 3,
      "confidence_level": "medium",
      "gap_analysis": {
        "knowledgeGaps": ["Channel patterns", "Context usage"],
        "strengths": ["Goroutines basics"]
      },
      "completed_at": "2024-01-01T11:15:00"
    }
  ]
}
```

**Поля ответа:**
- `overall_score` - общий балл (1-5), вычисляется с учетом весов компетенций
- `competency_assessments` - массив оценок по каждой компетенции:
  - `ai_assessed_score` - оценка AI (1-5)
  - `confidence_level` - уровень уверенности (`low`, `medium`, `high`)
  - `gap_analysis` - анализ пробелов в знаниях:
    - `knowledgeGaps` - список пробелов
    - `strengths` - сильные стороны (если есть)

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/api/assessments/{assessment_id}" \
  -H "Authorization: Bearer {token}"
```

---

### 3. Получить Roadmap (после завершения)

**GET** `/api/roadmaps/{assessment_id}`

Генерирует и возвращает персональный roadmap на основе результатов assessment.

**Требования:**
- Assessment должен быть в статусе `completed`

**Ответ:**
```json
{
  "id": "uuid",
  "assessment_id": "uuid",
  "title": "Personalized Learning Roadmap",
  "description": "Roadmap based on your assessment results",
  "sections": [
    {
      "id": "uuid",
      "title": "Go Concurrency",
      "description": "Improve your understanding of goroutines and channels",
      "order_index": 1,
      "completed": false
    }
  ],
  "created_at": "2024-01-01T11:30:00"
}
```

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/api/roadmaps/{assessment_id}" \
  -H "Authorization: Bearer {token}"
```

---

## Типичный workflow

### 1. Завершение Assessment

После того, как пользователь ответил на все вопросы:

```javascript
// Завершаем assessment
const response = await fetch(`/api/assessments/${assessmentId}/complete`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const { assessment } = await response.json();
console.log('Assessment completed:', assessment.overall_score);
```

### 2. Получение статистики

Сразу после завершения или в любой момент:

```javascript
// Получаем детальную статистику
const response = await fetch(`/api/assessments/${assessmentId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const data = await response.json();

// Общий балл
console.log('Overall Score:', data.overall_score);

// Оценки по компетенциям
data.competency_assessments.forEach(comp => {
  console.log(`${comp.competency_name}: ${comp.ai_assessed_score}/5`);
  console.log('Gaps:', comp.gap_analysis?.knowledgeGaps);
});
```

### 3. Генерация Roadmap

После получения статистики можно сгенерировать roadmap:

```javascript
// Генерируем roadmap
const roadmapResponse = await fetch(`/api/roadmaps/${assessmentId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const roadmap = await roadmapResponse.json();
console.log('Roadmap sections:', roadmap.sections);
```

---

## Примеры использования

### React компонент для отображения статистики

```typescript
import { useState, useEffect } from 'react';

interface CompetencyAssessment {
  id: string;
  competency_name: string;
  ai_assessed_score: number;
  confidence_level: string;
  gap_analysis?: {
    knowledgeGaps: string[];
    strengths?: string[];
  };
}

interface AssessmentStats {
  overall_score: number;
  competency_assessments: CompetencyAssessment[];
  status: string;
}

function AssessmentStatistics({ assessmentId }: { assessmentId: string }) {
  const [stats, setStats] = useState<AssessmentStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await fetch(`/api/assessments/${assessmentId}`, {
          headers: {
            'Authorization': `Bearer ${getToken()}`
          }
        });
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, [assessmentId]);

  if (loading) return <div>Loading...</div>;
  if (!stats) return <div>No data</div>;

  return (
    <div>
      <h2>Assessment Results</h2>
      
      {/* Общий балл */}
      <div className="overall-score">
        <h3>Overall Score: {stats.overall_score}/5</h3>
        <div className="progress-bar">
          <div 
            style={{ width: `${(stats.overall_score / 5) * 100}%` }}
            className="progress-fill"
          />
        </div>
      </div>

      {/* Оценки по компетенциям */}
      <div className="competencies">
        <h3>Competency Scores</h3>
        {stats.competency_assessments.map(comp => (
          <div key={comp.id} className="competency-card">
            <h4>{comp.competency_name}</h4>
            <div className="score">
              Score: {comp.ai_assessed_score}/5
              <span className={`confidence ${comp.confidence_level}`}>
                ({comp.confidence_level})
              </span>
            </div>
            
            {comp.gap_analysis && (
              <div className="gaps">
                <h5>Knowledge Gaps:</h5>
                <ul>
                  {comp.gap_analysis.knowledgeGaps.map((gap, idx) => (
                    <li key={idx}>{gap}</li>
                  ))}
                </ul>
              </div>
            )}

            {comp.gap_analysis?.strengths && (
              <div className="strengths">
                <h5>Strengths:</h5>
                <ul>
                  {comp.gap_analysis.strengths.map((strength, idx) => (
                    <li key={idx}>{strength}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### TypeScript типы

```typescript
// types/assessment.ts

export interface CompetencyAssessmentResponse {
  id: string;
  competency_id: string;
  competency_name: string | null;
  ai_assessed_score: number | null;
  confidence_level: 'low' | 'medium' | 'high' | null;
  gap_analysis: {
    knowledgeGaps: string[];
    strengths?: string[];
  } | null;
  completed_at: string | null;
}

export interface AssessmentResponse {
  id: string;
  user_id: string;
  role_id: string | null;
  role_name: string | null;
  status: 'in_progress' | 'completed' | 'abandoned';
  overall_score: number | null;
  started_at: string;
  completed_at: string | null;
  competency_assessments: CompetencyAssessmentResponse[];
}
```

---

## Интерпретация результатов

### Overall Score (Общий балл)

- **4.5 - 5.0**: Отличный уровень знаний
- **3.5 - 4.4**: Хороший уровень знаний
- **2.5 - 3.4**: Средний уровень знаний
- **1.5 - 2.4**: Базовый уровень знаний
- **1.0 - 1.4**: Начальный уровень знаний

### Confidence Level (Уровень уверенности)

- **high**: AI уверен в оценке (достаточно данных)
- **medium**: Средняя уверенность (некоторые данные отсутствуют)
- **low**: Низкая уверенность (мало данных для оценки)

### Gap Analysis (Анализ пробелов)

Содержит список тем, которые требуют дополнительного изучения на основе ответов пользователя.

---

## Ошибки

### 404 Not Found
Assessment не найден или не принадлежит текущему пользователю.

### 400 Bad Request
Assessment не завершен (статус не `completed`). Для получения roadmap необходимо сначала завершить assessment.

### 403 Forbidden
Нет доступа к данному assessment (принадлежит другому пользователю).
