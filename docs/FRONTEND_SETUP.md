# Настройка Frontend для AI Тестирования

## Что нужно изменить в вашем компоненте PageAIAssessment

### 1. Изменить загрузку вопросов

**Было (моковые данные):**
```typescript
const mockQuestions: Question[] = [
  { id: "1", index: 1, question: "...", competency: "..." },
  // ...
];
setQuestions(mockQuestions);
```

**Стало (динамическая генерация):**
```typescript
useEffect(() => {
  const loadQuestions = async () => {
    setIsLoading(true);
    try {
      // 1. Создаем assessment для направления
      const assessmentResponse = await fetch("/api/assessments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${jwtToken}`, // JWT токен из Keycloak
        },
        body: JSON.stringify({
          direction: "backend(golang, sql)", // Получайте из другого проекта или пропсов
        }),
      });

      if (!assessmentResponse.ok) {
        throw new Error("Failed to create assessment");
      }

      const { assessment_id, competencies } = await assessmentResponse.json();
      
      // Сохраняем для дальнейшего использования
      setAssessmentId(assessment_id);
      setCompetencies(competencies);

      // 2. Генерируем первый вопрос для первой компетенции
      if (competencies.length > 0) {
        await generateNextQuestion(assessment_id, competencies[0].id, 1);
      }

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
}, [directionText]);
```

### 2. Добавить функцию генерации вопроса

```typescript
const generateNextQuestion = async (
  assessmentId: string,
  competencyId: string,
  questionNumber: number,
  difficulty?: number // Опционально, будет определен автоматически
) => {
  try {
    const formData = new FormData();
    formData.append("assessment_id", assessmentId);
    formData.append("competency_id", competencyId);
    formData.append("question_number", questionNumber.toString());
    if (difficulty) {
      formData.append("difficulty", difficulty.toString());
    }

    const response = await fetch("/api/questions/generate", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${jwtToken}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to generate question");
    }

    const questionData = await response.json();

    // Обновляем текущий вопрос
    setCurrentQuestion({
      id: questionData.questionId,
      index: questionNumber,
      question: questionData.questionText,
      competency: competencies.find(c => c.id === competencyId)?.name || "",
      competencyId: competencyId,
      difficulty: questionData.difficulty,
      estimatedAnswerTime: questionData.estimatedAnswerTime,
    });

    return questionData;
  } catch (err) {
    console.error("Ошибка генерации вопроса:", err);
    throw err;
  }
};
```

### 3. Изменить отправку ответа

**Было:**
```typescript
// Сохраняем только в локальном состоянии
setAnswers((prev) => ({
  ...prev,
  [currentQuestion.id]: {
    questionId: currentQuestion.id,
    audioBlob,
    isAnswered: true,
  },
}));
```

**Стало:**
```typescript
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
        Authorization: `Bearer ${jwtToken}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to submit answer");
    }

    const result = await response.json();

    // Сохраняем результат
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
```

### 4. Обновить обработчик записи

```typescript
const stopRecording = async () => {
  if (mediaRecorderRef.current && isRecording) {
    mediaRecorderRef.current.stop();
    setIsRecording(false);

    // После остановки записи автоматически отправляем ответ
    if (currentQuestion && audioChunksRef.current.length > 0) {
      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
      
      try {
        const result = await submitAnswer(
          assessmentId!,
          currentQuestion.competencyId,
          currentQuestion.question,
          currentQuestion.difficulty,
          audioBlob
        );

        // Генерируем следующий вопрос на основе оценки
        const nextDifficulty = result.evaluation.nextDifficulty;
        const currentCompetency = competencies.find(
          c => c.id === currentQuestion.competencyId
        );
        
        if (currentCompetency) {
          // Определяем номер следующего вопроса
          const answeredCount = Object.keys(answers).length + 1;
          
          // Можно задать лимит вопросов на компетенцию (например, 3-5)
          if (answeredCount < 5) {
            await generateNextQuestion(
              assessmentId!,
              currentQuestion.competencyId,
              answeredCount + 1,
              nextDifficulty
            );
          } else {
            // Переходим к следующей компетенции или завершаем
            handleNext();
          }
        }
      } catch (err) {
        // Ошибка уже обработана в submitAnswer
      }
    }
  }
};
```

### 5. Обновить состояние компонента

```typescript
// Добавить новые состояния
const [assessmentId, setAssessmentId] = useState<string | null>(null);
const [competencies, setCompetencies] = useState<Array<{
  id: string;
  name: string;
  description?: string;
}>>([]);
const [currentQuestion, setCurrentQuestion] = useState<{
  id: string;
  index: number;
  question: string;
  competency: string;
  competencyId: string;
  difficulty: number;
  estimatedAnswerTime: string;
} | null>(null);

// Получать JWT токен из контекста/пропсов
const jwtToken = "your-jwt-token"; // Из Keycloak или контекста

// Получать direction из пропсов или другого проекта
const directionText = "backend(golang, sql)"; // Из пропсов
```

### 6. Обновить handleNext и handlePrevious

```typescript
const handleNext = async () => {
  if (!assessmentId || !currentQuestion) return;

  // Если есть неотправленный ответ, отправляем его
  const currentAnswer = answers[currentQuestion.question];
  if (currentAnswer?.audioBlob && !currentAnswer.transcript) {
    await submitAnswer(
      assessmentId,
      currentQuestion.competencyId,
      currentQuestion.question,
      currentQuestion.difficulty,
      currentAnswer.audioBlob
    );
  }

  // Определяем следующую компетенцию или вопрос
  const currentCompetencyIndex = competencies.findIndex(
    c => c.id === currentQuestion.competencyId
  );
  
  if (currentCompetencyIndex < competencies.length - 1) {
    // Переходим к следующей компетенции
    const nextCompetency = competencies[currentCompetencyIndex + 1];
    await generateNextQuestion(assessmentId, nextCompetency.id, 1);
  } else {
    // Все компетенции пройдены, завершаем
    handleComplete();
  }
};

const handlePrevious = async () => {
  // Можно реализовать навигацию по уже отвеченным вопросам
  // или просто запретить возврат назад в адаптивном режиме
  if (currentQuestionIndex > 0) {
    // Логика навигации назад
  }
};
```

### 7. Обновить handleComplete

```typescript
const handleComplete = async () => {
  setIsProcessing(true);
  try {
    if (!assessmentId) {
      throw new Error("Assessment ID not found");
    }

    // Завершаем assessment
    const response = await fetch(`/api/assessments/${assessmentId}/complete`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${jwtToken}`,
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

## Полный пример обновленного компонента

```typescript
import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
// ... остальные импорты

export function PageAIAssessment() {
  const navigate = useNavigate();
  
  // Получаем JWT токен (из контекста, пропсов или localStorage)
  const jwtToken = "your-jwt-token"; // TODO: получить из Keycloak
  
  // Получаем direction (из пропсов или другого проекта)
  const directionText = "backend(golang, sql)"; // TODO: получить из пропсов
  
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [competencies, setCompetencies] = useState<Array<{
    id: string;
    name: string;
  }>>([]);
  const [currentQuestion, setCurrentQuestion] = useState<{
    id: string;
    index: number;
    question: string;
    competency: string;
    competencyId: string;
    difficulty: number;
  } | null>(null);
  const [answers, setAnswers] = useState<Record<string, {
    questionText: string;
    audioBlob?: Blob;
    transcript?: string;
    evaluation?: any;
    isAnswered: boolean;
  }>>({});
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Загрузка assessment и генерация первого вопроса
  useEffect(() => {
    const loadAssessment = async () => {
      setIsLoading(true);
      try {
        const assessmentResponse = await fetch("/api/assessments", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${jwtToken}`,
          },
          body: JSON.stringify({ direction: directionText }),
        });

        if (!assessmentResponse.ok) {
          throw new Error("Failed to create assessment");
        }

        const { assessment_id, competencies } = await assessmentResponse.json();
        setAssessmentId(assessment_id);
        setCompetencies(competencies);

        // Генерируем первый вопрос
        if (competencies.length > 0) {
          await generateNextQuestion(assessment_id, competencies[0].id, 1);
        }

        setError(null);
      } catch (err) {
        setError("Не удалось загрузить вопросы. Пожалуйста, попробуйте позже.");
        console.error("Ошибка загрузки вопросов:", err);
      } finally {
        setIsLoading(false);
      }
    };

    if (directionText) {
      loadAssessment();
    }
  }, [directionText]);

  // Генерация вопроса
  const generateNextQuestion = async (
    assessmentId: string,
    competencyId: string,
    questionNumber: number,
    difficulty?: number
  ) => {
    try {
      const formData = new FormData();
      formData.append("assessment_id", assessmentId);
      formData.append("competency_id", competencyId);
      formData.append("question_number", questionNumber.toString());
      if (difficulty) {
        formData.append("difficulty", difficulty.toString());
      }

      const response = await fetch("/api/questions/generate", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${jwtToken}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to generate question");
      }

      const questionData = await response.json();
      const competency = competencies.find(c => c.id === competencyId);

      setCurrentQuestion({
        id: questionData.questionId,
        index: questionNumber,
        question: questionData.questionText,
        competency: competency?.name || "",
        competencyId: competencyId,
        difficulty: questionData.difficulty,
      });
    } catch (err) {
      console.error("Ошибка генерации вопроса:", err);
      throw err;
    }
  };

  // Отправка ответа
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
          Authorization: `Bearer ${jwtToken}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to submit answer");
      }

      const result = await response.json();

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

      return result;
    } catch (err) {
      console.error("Ошибка отправки ответа:", err);
      alert("Не удалось отправить ответ. Пожалуйста, попробуйте снова.");
      throw err;
    } finally {
      setIsProcessing(false);
    }
  };

  // Остановка записи с автоматической отправкой
  const stopRecording = async () => {
    if (mediaRecorderRef.current && isRecording && currentQuestion) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
      
      try {
        const result = await submitAnswer(
          assessmentId!,
          currentQuestion.competencyId,
          currentQuestion.question,
          currentQuestion.difficulty,
          audioBlob
        );

        // Генерируем следующий вопрос
        const answeredCount = Object.keys(answers).length + 1;
        const nextDifficulty = result.evaluation.nextDifficulty;
        
        if (answeredCount < 5) { // Лимит вопросов
          await generateNextQuestion(
            assessmentId!,
            currentQuestion.competencyId,
            answeredCount + 1,
            nextDifficulty
          );
        } else {
          handleNext();
        }
      } catch (err) {
        // Ошибка уже обработана
      }
    }
  };

  // ... остальной код компонента
}
```

## Ключевые изменения

1. ✅ **Убрать моковые данные** - использовать реальный API
2. ✅ **Динамическая генерация** - генерировать вопросы по одному
3. ✅ **Новый endpoint ответа** - `/api/questions/answer` вместо `/{question_id}/answer`
4. ✅ **Передавать данные вопроса** - `assessment_id`, `competency_id`, `question_text`, `difficulty`
5. ✅ **Адаптивная сложность** - использовать `evaluation.nextDifficulty` для следующего вопроса
6. ✅ **JWT токен** - использовать токен из Keycloak в заголовке Authorization

## Переменные окружения

Убедитесь, что у вас настроен базовый URL API:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
```

## Получение JWT токена

Если используете Keycloak, получайте токен так:

```typescript
// Пример с Keycloak
import { useKeycloak } from "@react-keycloak/web";

const { keycloak } = useKeycloak();
const jwtToken = keycloak.token;
```

Или из контекста/пропсов вашего приложения.
