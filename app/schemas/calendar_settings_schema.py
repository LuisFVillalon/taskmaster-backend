from datetime import date
from typing import Optional
from pydantic import BaseModel


class CalendarSettingsBase(BaseModel):
    title: str
    sub_header: str
    start_date: date
    end_date: date


class CalendarSettingsUpdate(BaseModel):
    title: Optional[str] = None
    sub_header: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CalendarSettings(CalendarSettingsBase):
    id: int
    user_id: Optional[str] = None

    model_config = {"from_attributes": True}
