from pydantic import BaseModel
from typing import List, Optional
from app.schemas.tag_schema import Tag


class HabitBase(BaseModel):
    title: str
    tags: List[Tag] = []


class HabitCreate(HabitBase):
    pass


class HabitResponse(HabitBase):
    id: int
    user_id: Optional[str] = None
    current_streak: int = 0
    max_streak: int = 0
    logged_today: bool = False

    model_config = {
        "from_attributes": True
    }


class HabitHistoryEntry(BaseModel):
    date: str
    logged: bool


class HabitToggleDateRequest(BaseModel):
    date: str
