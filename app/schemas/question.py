from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class QuestionGenerateResponse(BaseModel):
    """Ответ на генерацию вопроса"""
    questionId: Optional[UUID] = None
    questionText: Optional[str] = None
    difficulty: Optional[int] = None
    estimatedAnswerTime: Optional[str] = None
    expectedKeyPoints: Optional[List[str]] = None
    noMoreQuestions: bool = False  # True если больше нет доступных вопросов для этой компетенции


class AnswerEvaluation(BaseModel):
    """Оценка ответа"""
    score: int
    understandingDepth: str  # shallow, medium, deep
    isCorrect: bool
    feedback: str
    knowledgeGaps: List[str]
    nextDifficulty: int
    reasoning: Optional[str] = None
    correctAnswer: str  # Эталонный правильный ответ
    expectedKeyPoints: List[str]  # Ключевые моменты, которые должны быть в ответе


class AnswerResponse(BaseModel):
    """Ответ на отправку голосового ответа"""
    transcript: str
    evaluation: AnswerEvaluation


class QuestionListItem(BaseModel):
    """Элемент списка вопросов"""
    id: UUID
    index: int
    question: str
    competency: str
    competency_id: UUID
    difficulty: int
    estimatedAnswerTime: str


class QuestionsListResponse(BaseModel):
    """Ответ со списком всех вопросов для тестирования"""
    questions: List[QuestionListItem]
