from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class Role(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
