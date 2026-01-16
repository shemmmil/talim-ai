# Интеграция Frontend с Backend API для AI Тестирования

## Быстрый старт

```typescript
// 1. Создать assessment с направлением
const response = await fetch("/api/assessments", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${userId}`,
  },
  body: JSON.stringify({
    direction: "backend(golang, sql)", // Просто текст!
  }),
});

const { assessment_id, competencies } = await response.json();

// 2. Сгенерировать первый вопрос (динамически, на основе предыдущих ответов)
const questionFormData = new FormData();
questionFormData.append("assessment_id", assessment_id);
questionFormData.append("competency_id", competencies[0].id);
questionFormData.append("question_number", "1");

const { questionText, difficulty, questionId } = await fetch(
  "/api/questions/generate",
  {
    method: "POST",
    headers: { Authorization: `Bearer ${userId}` },
    body: questionFormData,
  }
).then((r) => r.json());

// 3. Отправить ответ (вопрос сохраняется в БД только после ответа)
const answerFormData = new FormData();
answerFormData.append("assessment_id", assessment_id);
answerFormData.append("competency_id", competencies[0].id);
answerFormData.append("question_text", questionText);
answerFormData.append("difficulty", difficulty.toString());
answerFormData.append("audio", audioBlob);

const { transcript, evaluation } = await fetch("/api/questions/answer", {
  method: "POST",
  headers: { Authorization: `Bearer ${userId}` },
  body: answerFormData,
}).then((r) => r.json());

// 4. Сгенерировать следующий вопрос на основе оценки (evaluation.nextDifficulty)
// Повторять до завершения всех компетенций

// 5. Завершить тестирование
await fetch(`/api/assessments/${assessment_id}/complete`, {
  method: "POST",
  headers: { Authorization: `Bearer ${userId}` },
});
```

## Обзор

Ваш бэкенд использует **адаптивное тестирование**, где вопросы генерируются динамически на основе предыдущих ответов. Это более продвинутый подход, чем статический список вопросов.

**Ключевые особенности:**

- ✅ Направление передается как **текст** (не нужен UUID)
- ✅ Компетенции определяются **автоматически** через GPT
- ✅ Направление **не хранится** в БД
- ✅ Roadmap формируется **автоматически** после тестирования

### О направлениях (Directions)

В системе используется концепция **"направлений"** (directions) - это области развития, по которым пользователь проходит тестирование.

- Направление передается как **текст** (например: "backend(golang, sql)", "frontend(react, typescript)")
- Система автоматически определяет компетенции для тестирования через GPT на основе текста направления
- Направление **не хранится в БД** - используется только для формирования assessment и roadmap
- По результатам тестирования формируется персональный roadmap

## Текущая архитектура бэкенда

1. **Создание assessment** → получаем список компетенций
2. **Динамическая генерация вопросов** → по одному вопросу за раз, на основе предыдущих ответов
   - Вопросы **НЕ сохраняются** в БД при генерации
   - Каждый следующий вопрос адаптируется под уровень пользователя
3. **Отправка ответов** → аудио файл + транскрипция + оценка
   - Вопрос и ответ сохраняются в БД **только после отправки ответа**
4. **Завершение assessment** → вычисление общего балла
5. **Генерация roadmap** → после завершения тестирования

## Необходимые API Endpoints

### 1. Создание тестирования (Assessment)

**Endpoint:** `POST /api/assessments`

**Запрос:**

```typescript
{
  direction: string; // Текст направления, например "backend(golang, sql)"
}
```

**Пример:**

```typescript
{
  direction: "backend(golang, sql)";
}
// или
{
  direction: "frontend(react, typescript)";
}
```

**Ответ:**

```typescript
{
  assessment_id: string; // UUID
  competencies: Array<{
    id: string;
    name: string;
    description?: string;
    category?: string;
    importance_weight?: number;
    order_index?: number;
  }>;
  status: "in_progress";
}
```

**Использование:**

- Вызывается при загрузке страницы тестирования
- Передайте `direction` (текст направления) в body запроса
- Система автоматически определит компетенции для тестирования через GPT
- Сохраните `assessment_id` для последующих запросов
- Используйте `competencies` для навигации по компетенциям
- По завершении тестирования будет автоматически сформирован roadmap
- **Направление не хранится в БД** - используется только для формирования assessment и roadmap

---

### 2. Генерация вопроса (динамическая)

**Endpoint:** `POST /api/questions/generate`

**Запрос (Form Data):**

```
assessment_id: UUID
competency_id: UUID
question_number: int (1-7)
difficulty?: int (1-5, опционально)
```

**Ответ:**

```typescript
{
  questionId: string; // Временный UUID (для идентификации на фронтенде)
  questionText: string;
  difficulty: number; // 1-5
  estimatedAnswerTime: string; // например "1-2 минуты"
  expectedKeyPoints: string[];
}
```

**Использование:**

- ✅ Вопросы генерируются **динамически** на основе предыдущих ответов
- ✅ Вопрос **НЕ сохраняется** в БД при генерации
- ✅ Сложность определяется автоматически на основе предыдущих ответов
- ✅ Каждый следующий вопрос адаптируется под уровень пользователя
- Генерируйте вопросы по одному, после каждого ответа

---

### 3. Отправка голосового ответа

**Endpoint:** `POST /api/questions/answer`

**Запрос (Form Data):**

```
assessment_id: UUID
competency_id: UUID
question_text: string  // Текст вопроса, на который отвечает пользователь
difficulty: int (1-5)  // Сложность вопроса
audio: File (webm, mp3, wav, m4a, ogg)
```

**Ответ:**

```typescript
{
  transcript: string; // Транскрипция аудио
  evaluation: {
    score: number; // 1-5
    understandingDepth: "shallow" | "medium" | "deep";
    isCorrect: boolean;
    feedback: string;
    knowledgeGaps: string[];
    nextDifficulty: number; // 1-5 (для следующего вопроса)
    reasoning?: string;
  };
}
```

**Использование:**

- ✅ Вопрос и ответ сохраняются в БД **только после отправки ответа**
- Отправляйте аудио файл после записи ответа
- Передавайте `question_text` и `difficulty` из сгенерированного вопроса
- Сохраните `transcript` для отображения пользователю
- Используйте `evaluation.nextDifficulty` для следующего вопроса

---

### 4. Завершение тестирования

**Endpoint:** `POST /api/assessments/{assessment_id}/complete`

**Ответ:**

```typescript
{
  message: "Assessment completed";
  assessment: {
    id: string;
    status: "completed";
    overall_score: number;
    completed_at: string;
  }
}
```

**Использование:**

- Вызывается после ответа на все вопросы
- После завершения можно запросить roadmap

---

### 5. Получение Roadmap

**Endpoint:** `GET /api/roadmaps/{assessment_id}`

**Ответ:**

```typescript
{
  id: string;
  assessment_id: string;
  title: string;
  description: string;
  estimated_duration_weeks: number;
  difficulty_level: string;
  sections: Array<{
    id: string;
    competency_id: string;
    competency_name: string;
    title: string;
    description: string;
    learning_materials: Array<{...}>;
    practice_tasks: Array<{...}>;
    self_check_questions: Array<{...}>;
  }>;
}
```

**Использование:**

- Вызывается после завершения тестирования
- Если roadmap еще не создан, он будет автоматически сгенерирован

---

## Аутентификация

Все запросы требуют заголовок `Authorization`:

```typescript
headers: {
  'Authorization': `Bearer ${userId}` // или просто userId
}
```

---

## Пример интеграции для вашего компонента

### Вариант 1: Адаптивное тестирование (рекомендуется)

```typescript
// 1. При загрузке страницы - создаем assessment для направления
const startAssessment = async () => {
  const response = await fetch("/api/assessments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${userId}`,
    },
    body: JSON.stringify({
      direction: "backend(golang, sql)", // Передаем направление как текст
    }),
  });

  const data = await response.json();
  setAssessmentId(data.assessment_id);
  setCompetencies(data.competencies);

  // Генерируем первый вопрос для первой компетенции
  await generateNextQuestion(data.assessment_id, data.competencies[0].id, 1);
};

// 2. Генерация вопроса
const generateNextQuestion = async (
  assessmentId: string,
  competencyId: string,
  questionNumber: number
) => {
  const formData = new FormData();
  formData.append("assessment_id", assessmentId);
  formData.append("competency_id", competencyId);
  formData.append("question_number", questionNumber.toString());

  const response = await fetch("/api/questions/generate", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${userId}`,
    },
    body: formData,
  });

  const question = await response.json();
  setCurrentQuestion(question);
};

// 3. Отправка ответа (вопрос сохраняется в БД только после ответа)
const submitAnswer = async (
  assessmentId: string,
  competencyId: string,
  questionText: string,
  difficulty: number,
  audioBlob: Blob
) => {
  const formData = new FormData();
  formData.append("assessment_id", assessmentId);
  formData.append("competency_id", competencyId);
  formData.append("question_text", questionText);
  formData.append("difficulty", difficulty.toString());
  formData.append("audio", audioBlob, "answer.webm");

  const response = await fetch("/api/questions/answer", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${userId}`,
    },
    body: formData,
  });

  const result = await response.json();
  // result.transcript - транскрипция
  // result.evaluation - оценка ответа
  // result.evaluation.nextDifficulty - сложность для следующего вопроса
  return result;
};

// 4. Завершение тестирования
const completeAssessment = async (assessmentId: string) => {
  const response = await fetch(`/api/assessments/${assessmentId}/complete`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${userId}`,
    },
  });

  const result = await response.json();
  return result;
};
```

### Вариант 2: Адаптивное тестирование (рекомендуется)

**Важно:** Вопросы генерируются динамически на основе предыдущих ответов. Не нужно получать все вопросы сразу.

**Flow:**

1. Создать assessment
2. Для каждой компетенции:
   - Генерировать вопрос через `/api/questions/generate`
   - Показать вопрос пользователю
   - Получить ответ (аудио)
   - Отправить ответ через `/api/questions/answer`
   - Сгенерировать следующий вопрос на основе оценки предыдущего
3. Повторять до завершения всех компетенций

---

## Рекомендации

1. **Передавайте направление как текст** - формат: "направление(технология1, технология2)"
   - Примеры: "backend(golang, sql)", "frontend(react, typescript)", "data-science(python, ml)"
2. **Сохраняйте прогресс** - используйте `assessment_id` для сохранения состояния
3. **Обрабатывайте ошибки** - все endpoints могут вернуть ошибки (400, 401, 403, 404, 500)
4. **Показывайте обратную связь** - используйте `evaluation.feedback` для пользователя
5. **Не храните направление в БД** - оно нужно только для создания assessment, дальше работа идет через компетенции

## Формат направления

Направление передается как строка в свободном формате. Рекомендуемый формат:

```
"направление(технология1, технология2, ...)"
```

Примеры:

- `"backend(golang, sql, docker)"`
- `"frontend(react, typescript, nextjs)"`
- `"data-science(python, pandas, ml)"`
- `"devops(kubernetes, terraform, aws)"`

GPT автоматически проанализирует текст и определит релевантные компетенции для тестирования.

---

## Структура данных для фронтенда

```typescript
interface AssessmentState {
  assessmentId: string;
  direction: string; // Текст направления, например "backend(golang, sql)"
  competencies: Competency[];
  currentCompetencyIndex: number;
  currentQuestionNumber: number;
  questions: Map<string, Question[]>; // competency_id -> questions
  answers: Map<string, Answer>; // question_id -> answer
  status: "loading" | "in_progress" | "completed";
}

interface Question {
  id: string;
  questionText: string;
  competencyId: string;
  competencyName: string;
  difficulty: number;
  estimatedAnswerTime: string;
}

interface Answer {
  questionId: string;
  audioBlob?: Blob;
  transcript?: string;
  evaluation?: Evaluation;
  isAnswered: boolean;
}
```

---

## Полный пример интеграции для вашего компонента

```typescript
// Замена моковых данных на реальный API
useEffect(() => {
  const loadQuestions = async () => {
    setIsLoading(true);
    try {
      // 1. Создаем assessment для направления (direction как текст в body)
      const assessmentResponse = await fetch("/api/assessments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${userId}`, // или просто userId
        },
        body: JSON.stringify({
          direction: directionText, // Например "backend(golang, sql)"
        }),
      });

      if (!assessmentResponse.ok) {
        throw new Error("Failed to create assessment");
      }

      const assessmentData = await assessmentResponse.json();
      const assessmentId = assessmentData.assessment_id;

      // 2. Получаем все вопросы
      const questionsResponse = await fetch(
        `/api/assessments/${assessmentId}/questions?questions_per_competency=3`,
        {
          headers: {
            Authorization: `Bearer ${userId}`,
          },
        }
      );

      if (!questionsResponse.ok) {
        throw new Error("Failed to load questions");
      }

      const { questions } = await questionsResponse.json();

      // Преобразуем в формат вашего компонента
      const formattedQuestions: Question[] = questions.map((q: any) => ({
        id: q.id,
        index: q.index,
        question: q.question,
        competency: q.competency,
      }));

      setQuestions(formattedQuestions);
      setAssessmentId(assessmentId); // Сохраняем для отправки ответов
      setError(null);
    } catch (err) {
      setError("Не удалось загрузить вопросы. Пожалуйста, попробуйте позже.");
      console.error("Ошибка загрузки вопросов:", err);
    } finally {
      setIsLoading(false);
    }
  };

  if (directionText) {
    loadQuestions();
  }
}, [directionText, userId]);

// Отправка ответа (вопрос сохраняется в БД только после ответа)
const submitAnswer = async (
  assessmentId: string,
  competencyId: string,
  questionText: string,
  difficulty: number,
  audioBlob: Blob
) => {
  setIsProcessing(true);
  try {
    const formData = new FormData();
    formData.append("assessment_id", assessmentId);
    formData.append("competency_id", competencyId);
    formData.append("question_text", questionText);
    formData.append("difficulty", difficulty.toString());
    formData.append("audio", audioBlob, "answer.webm");

    const response = await fetch("/api/questions/answer", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${userId}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to submit answer");
    }

    const result = await response.json();

    // Обновляем ответ в состоянии
    setAnswers((prev) => ({
      ...prev,
      [questionText]: {
        questionText,
        audioBlob,
        transcript: result.transcript,
        evaluation: result.evaluation,
        isAnswered: true,
      },
    }));

    // Возвращаем результат с nextDifficulty для следующего вопроса
    return result;
  } catch (err) {
    console.error("Ошибка отправки ответа:", err);
    alert("Не удалось отправить ответ. Пожалуйста, попробуйте снова.");
    throw err;
  } finally {
    setIsProcessing(false);
  }
};

// Завершение тестирования
const handleComplete = async () => {
  setIsProcessing(true);
  try {
    if (!assessmentId) {
      throw new Error("Assessment ID not found");
    }

    // Отправляем все ответы, которые еще не отправлены
    for (const [questionId, answer] of Object.entries(answers)) {
      if (answer.isAnswered && answer.audioBlob && !answer.transcript) {
        await submitAnswer(questionId, answer.audioBlob);
      }
    }

    // Завершаем assessment
    const response = await fetch(`/api/assessments/${assessmentId}/complete`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${userId}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to complete assessment");
    }

    setIsCompleted(true);
  } catch (err) {
    console.error("Ошибка завершения тестирования:", err);
    alert("Не удалось завершить тестирование. Пожалуйста, попробуйте снова.");
  } finally {
    setIsProcessing(false);
  }
};
```

## Дополнительные переменные состояния

Добавьте в ваш компонент:

```typescript
const [assessmentId, setAssessmentId] = useState<string | null>(null);
const [directionText, setDirectionText] = useState<string>(""); // Например "backend(golang, sql)"
const userId = "your-user-id"; // Получайте из контекста/хранилища
```

## Полный пример для вашего компонента (PageAIAssessment)

Вот как интегрировать API в ваш существующий компонент:

```typescript
// Замена моковых данных на реальный API
useEffect(() => {
  const loadQuestions = async () => {
    setIsLoading(true);
    try {
      // Получаем направление из пропсов или состояния
      // Например, из другого проекта или из формы выбора
      const direction = "backend(golang, sql)"; // или из props/state

      // 1. Создаем assessment для направления
      const assessmentResponse = await fetch("/api/assessments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${userId}`,
        },
        body: JSON.stringify({ direction }),
      });

      if (!assessmentResponse.ok) {
        throw new Error("Failed to create assessment");
      }

      const assessmentData = await assessmentResponse.json();
      const assessmentId = assessmentData.assessment_id;

      // 2. Получаем все вопросы сразу (упрощенный вариант)
      const questionsResponse = await fetch(
        `/api/assessments/${assessmentId}/questions?questions_per_competency=3`,
        {
          headers: {
            Authorization: `Bearer ${userId}`,
          },
        }
      );

      if (!questionsResponse.ok) {
        throw new Error("Failed to load questions");
      }

      const { questions } = await questionsResponse.json();

      // Преобразуем в формат вашего компонента
      const formattedQuestions: Question[] = questions.map((q: any) => ({
        id: q.id,
        index: q.index,
        question: q.question,
        competency: q.competency,
      }));

      setQuestions(formattedQuestions);
      setAssessmentId(assessmentId);
      setError(null);
    } catch (err) {
      setError("Не удалось загрузить вопросы. Пожалуйста, попробуйте позже.");
      console.error("Ошибка загрузки вопросов:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Запускаем при наличии направления
  if (directionText) {
    loadQuestions();
  }
}, [directionText, userId]);

// Обновленный handleComplete
const handleComplete = async () => {
  setIsProcessing(true);
  try {
    if (!assessmentId) {
      throw new Error("Assessment ID not found");
    }

    // Отправляем все ответы, которые еще не отправлены
    for (const [questionId, answer] of Object.entries(answers)) {
      if (answer.isAnswered && answer.audioBlob && !answer.transcript) {
        await submitAnswer(questionId, answer.audioBlob);
      }
    }

    // Завершаем assessment
    const response = await fetch(`/api/assessments/${assessmentId}/complete`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${userId}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to complete assessment");
    }

    setIsCompleted(true);

    // Опционально: можно сразу получить roadmap
    // const roadmapResponse = await fetch(`/api/roadmaps/${assessmentId}`, {
    //   headers: { Authorization: `Bearer ${userId}` }
    // });
    // const roadmap = await roadmapResponse.json();
  } catch (err) {
    console.error("Ошибка завершения тестирования:", err);
    alert("Не удалось завершить тестирование. Пожалуйста, попробуйте снова.");
  } finally {
    setIsProcessing(false);
  }
};
```

## Важные замечания

1. **Направление передается как текст** - не нужен UUID или ID из БД
2. **Направление не хранится** - вы передаете его только при создании assessment
3. **Компетенции определяются автоматически** - GPT анализирует текст направления и определяет нужные компетенции
4. **Все остальное работает как раньше** - вопросы, ответы, roadmap формируются автоматически
