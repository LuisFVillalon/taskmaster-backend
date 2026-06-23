from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProfileSave(BaseModel):
    name: str
    shutoff_time: Optional[str] = None


class ProfileOut(BaseModel):
    user_id: str
    name: str
    created_at: datetime
    shutoff_time: Optional[str] = None

    class Config:
        from_attributes = True
