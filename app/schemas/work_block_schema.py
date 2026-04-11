from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator


_VALID_STATUSES = {"suggested", "confirmed", "dismissed"}


class WorkBlockCreate(BaseModel):
    task_id:      int
    start_time:   datetime
    end_time:     datetime
    ai_reasoning: Optional[str]   = None
    confidence:   Optional[float] = None
    # AI service always sends 'suggested'; frontend PATCH changes it later.
    status:       str             = "suggested"

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        if v not in _VALID_STATUSES:
            raise ValueError(f"status must be one of {_VALID_STATUSES}")
        return v

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class WorkBlockUpdate(BaseModel):
    """
    Accepts two mutually-exclusive operations via the PATCH endpoint:
      • Status change  — send  { "status": "confirmed" | "dismissed" }
      • Reschedule     — send  { "start_time": "...", "end_time": "..." }
    Mixing both or sending neither is a validation error.
    """
    status:     Optional[str]      = None
    start_time: Optional[datetime] = None
    end_time:   Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        allowed = {"confirmed", "dismissed"}
        if v is not None and v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    @model_validator(mode="after")
    def check_payload(self) -> "WorkBlockUpdate":
        has_status = self.status is not None
        has_times  = self.start_time is not None or self.end_time is not None
        if not has_status and not has_times:
            raise ValueError("Provide 'status' or 'start_time'/'end_time'")
        if has_times:
            if self.start_time is None or self.end_time is None:
                raise ValueError("Both start_time and end_time are required for rescheduling")
            if self.end_time <= self.start_time:
                raise ValueError("end_time must be after start_time")
        return self


class WorkBlockOut(BaseModel):
    id:           int
    task_id:      int
    user_id:      str
    start_time:   datetime
    end_time:     datetime
    status:       str
    ai_reasoning: Optional[str]
    confidence:   Optional[float]
    created_at:   datetime

    model_config = {"from_attributes": True}
