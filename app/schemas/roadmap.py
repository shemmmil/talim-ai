from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID


class LearningMaterialResponse(BaseModel):
    id: UUID
    type: str
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty: Optional[str] = None
    language: Optional[str] = None
    is_free: bool = True
    order_index: Optional[int] = None
    rating: Optional[float] = None


class PracticeTaskResponse(BaseModel):
    id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: str
    difficulty: Optional[int] = None
    estimated_time_minutes: Optional[int] = None
    requirements: Optional[Dict[str, Any]] = None
    hints: Optional[Dict[str, Any]] = None
    order_index: Optional[int] = None


class SelfCheckQuestionResponse(BaseModel):
    id: UUID
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    difficulty: Optional[int] = None
    order_index: Optional[int] = None


class RoadmapSectionResponse(BaseModel):
    id: UUID
    competency_id: Optional[UUID] = None
    competency_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    estimated_duration_hours: Optional[int] = None
    status: str
    completed_at: Optional[datetime] = None
    learning_materials: List[LearningMaterialResponse] = []
    practice_tasks: List[PracticeTaskResponse] = []
    self_check_questions: List[SelfCheckQuestionResponse] = []


class RoadmapResponse(BaseModel):
    id: UUID
    assessment_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_duration_weeks: Optional[int] = None
    difficulty_level: Optional[int] = None
    generated_at: datetime
    updated_at: datetime
    status: str
    sections: List[RoadmapSectionResponse] = []


class RoadmapDetailResponse(RoadmapResponse):
    """Полный ответ со всеми деталями roadmap"""
    pass
