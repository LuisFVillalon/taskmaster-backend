from pydantic import BaseModel
from datetime import date
from typing import Optional


class CalendarSettingsUpdate(BaseModel):
    title: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CalendarSettings(BaseModel):
    id: int
    title: str
    start_date: date
    end_date: date

    model_config = {"from_attributes": True}
