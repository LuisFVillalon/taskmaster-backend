from decimal import Decimal
from datetime import date, time, datetime
from pydantic import BaseModel, field_validator
from app.schemas.tag_schema import Tag, TagCreate


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    category: str | None = None
    completed: bool = False
    priority: int | None = None

    due_date: date | None = None
    due_time: time | None = None

    completed_date: datetime | None = None

    estimated_time: float | None = None
    parent_task_id: int | None = None

    tags: list[TagCreate] = []

    @field_validator("priority", mode="before")
    @classmethod
    def validate_priority(cls, v):
        if v is None or v == 0:
            return None
        if not isinstance(v, int) or v < 1:
            raise ValueError("Priority must be a positive integer (≥ 1)")
        return v

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


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    created_date: datetime
    # user_id is set server-side from the JWT — exposed in responses but never
    # accepted from the client in TaskCreate/TaskBase.
    user_id: str | None = None
    tags: list[Tag] = []

    model_config = {"from_attributes": True}
