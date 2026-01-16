from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID


class User(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
