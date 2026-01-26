from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class Assessment(BaseModel):
    id: UUID
    user_id: UUID
    role_id: Optional[UUID] = None
    direction_id: Optional[UUID] = None
    technology_id: Optional[UUID] = None
    status: str  # 'in_progress', 'completed', 'abandoned'
    overall_score: Optional[float] = None
    attempt_number: int = 1
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CompetencyAssessment(BaseModel):
    id: UUID
    assessment_id: UUID
    competency_id: UUID
    ai_assessed_score: Optional[int] = None  # 1-5
    confidence_level: Optional[str] = None  # 'low', 'medium', 'high'
    gap_analysis: Optional[Dict[str, Any]] = None
    test_session_data: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuestionHistory(BaseModel):
    id: UUID
    competency_assessment_id: UUID
    question_text: str
    question_type: Optional[str] = None
    difficulty_level: Optional[int] = None  # 1-5
    user_answer_transcript: Optional[str] = None
    audio_duration_seconds: Optional[int] = None
    transcription_confidence: Optional[float] = None
    is_correct: Optional[bool] = None
    ai_evaluation: Optional[Dict[str, Any]] = None
    time_spent_seconds: Optional[int] = None
    asked_at: datetime
    answered_at: Optional[datetime] = None

    class Config:
        from_attributes = True
