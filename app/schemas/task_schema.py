from decimal import Decimal
from datetime import date, time, datetime
from pydantic import BaseModel, field_validator
from typing import List, Optional
from app.schemas.tag_schema import Tag


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    completed: bool = False
    urgent: bool = False

    due_date: Optional[date] = None
    due_time: Optional[time] = None

    completed_date: Optional[datetime] = None

    estimated_time: Optional[float] = None
    complexity: Optional[int] = None
    parent_task_id: Optional[int] = None

    tags: List[Tag] = []

    @field_validator("due_date", "due_time", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

    @field_validator("estimated_time", mode="before")
    @classmethod
    def validate_estimated_time(cls, v):
        if v is None:
            return v
        if isinstance(v, Decimal):
            v = float(v)
        if v < 0:
            raise ValueError("Estimated time must be non-negative")
        return v

    @field_validator("complexity", mode="before")
    @classmethod
    def validate_complexity(cls, v):
        if v == 0:
            return None
        if v is None:
            return v
        if not isinstance(v, int) or v < 1 or v > 5:
            raise ValueError("Complexity must be 1-5")
        return v


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    created_date: datetime
    # user_id is set server-side from the JWT — exposed in responses but never
    # accepted from the client in TaskCreate/TaskBase.
    user_id: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
