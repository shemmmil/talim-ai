from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID


class Roadmap(BaseModel):
    id: UUID
    assessment_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_duration_weeks: Optional[int] = None
    difficulty_level: Optional[int] = None
    priority_order: Optional[Dict[str, Any]] = None
    generated_at: datetime
    updated_at: datetime
    status: str  # 'active', 'completed', 'abandoned'

    class Config:
        from_attributes = True


class RoadmapSection(BaseModel):
    id: UUID
    roadmap_id: UUID
    competency_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    estimated_duration_hours: Optional[int] = None
    status: str  # 'not_started', 'in_progress', 'completed'
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningMaterial(BaseModel):
    id: UUID
    roadmap_section_id: UUID
    type: str  # 'article', 'video', 'book', 'course', 'documentation', 'tutorial'
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

    class Config:
        from_attributes = True


class PracticeTask(BaseModel):
    id: UUID
    roadmap_section_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: str  # 'coding', 'quiz', 'project', 'case_study'
    difficulty: Optional[int] = None  # 1-5
    estimated_time_minutes: Optional[int] = None
    requirements: Optional[Dict[str, Any]] = None
    hints: Optional[Dict[str, Any]] = None
    solution_example: Optional[str] = None
    order_index: Optional[int] = None

    class Config:
        from_attributes = True


class SelfCheckQuestion(BaseModel):
    id: UUID
    roadmap_section_id: UUID
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[int] = None  # 1-5
    order_index: Optional[int] = None

    class Config:
        from_attributes = True


class UserProgress(BaseModel):
    id: UUID
    user_id: UUID
    roadmap_section_id: UUID
    status: str  # 'not_started', 'in_progress', 'completed'
    progress_percentage: int  # 0-100
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_activity_at: datetime

    class Config:
        from_attributes = True
