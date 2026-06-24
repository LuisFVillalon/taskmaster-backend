from pydantic import BaseModel
from app.schemas.tag_schema import Tag


class HabitBase(BaseModel):
    title: str
    tags: list[Tag] = []


class HabitCreate(HabitBase):
    pass


class HabitResponse(HabitBase):
    id: int
    user_id: str | None = None
    current_streak: int = 0
    max_streak: int = 0
    logged_today: bool = False

    model_config = {"from_attributes": True}


class HabitHistoryEntry(BaseModel):
    date: str
    logged: bool


class HabitToggleDateRequest(BaseModel):
    date: str
