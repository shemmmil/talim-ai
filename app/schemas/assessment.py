from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID


class AssessmentCreate(BaseModel):
    direction: str  # Название направления, например "backend"
    technology: Optional[str] = None  # Название технологии, например "go" или "php"


class CompetencyInfo(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    importance_weight: Optional[int] = None
    order_index: Optional[int] = None


class AssessmentStartResponse(BaseModel):
    assessment_id: UUID
    competencies: List[CompetencyInfo]
    status: str


class CompetencyAssessmentResponse(BaseModel):
    id: UUID
    competency_id: UUID
    competency_name: Optional[str] = None
    ai_assessed_score: Optional[int] = None
    confidence_level: Optional[str] = None
    gap_analysis: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None


class AssessmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    role_id: Optional[UUID] = None
    role_name: Optional[str] = None
    direction_id: Optional[UUID] = None
    technology_id: Optional[UUID] = None
    status: str
    overall_score: Optional[float] = None
    attempt_number: int = 1
    started_at: datetime
    completed_at: Optional[datetime] = None
    competency_assessments: List[CompetencyAssessmentResponse] = []
