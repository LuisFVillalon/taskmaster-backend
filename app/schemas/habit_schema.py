from decimal import Decimal
from pydantic import BaseModel, field_validator
from app.schemas.tag_schema import Tag


class HabitBase(BaseModel):
    title: str
    tags: list[Tag] = []
    estimated_time: float | None = None

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
    # Caller's local calendar date ("YYYY-MM-DD"). Used for the streak
    # grace-period ("logged today or yesterday?") calc so a server/client
    # timezone gap can't roll "today" over early. Optional; the server falls
    # back to its own date.today() when absent.
    local_date: str | None = None
