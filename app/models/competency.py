from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class Competency(BaseModel):
    id: UUID
    role_id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    importance_weight: Optional[int] = None
    order_index: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
