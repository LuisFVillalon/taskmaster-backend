from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, field_validator

_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


def _validate_time(v: str) -> str:
    if not _TIME_RE.match(v):
        raise ValueError("time must be in HH:MM format")
    h, m = map(int, v.split(":"))
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError("time out of range")
    return v


class AvailabilityPreferenceCreate(BaseModel):
    day_of_week: int          # 0 Sun … 6 Sat  (JS Date.getDay() convention)
    start_time:  str          # "HH:MM" UTC
    end_time:    str          # "HH:MM" UTC
    label:       Optional[str] = None

    @field_validator("day_of_week")
    @classmethod
    def dow_in_range(cls, v: int) -> int:
        if not (0 <= v <= 6):
            raise ValueError("day_of_week must be 0 (Sun) – 6 (Sat)")
        return v

    @field_validator("start_time", "end_time")
    @classmethod
    def valid_time(cls, v: str) -> str:
        return _validate_time(v)

    # No end_after_start constraint — end_time < start_time means the window
    # spans midnight (e.g. 22:00 → 06:00 next morning).  Identical times are
    # the only invalid case (zero-length window).
    @field_validator("end_time")
    @classmethod
    def end_not_equal_start(cls, v: str, info) -> str:
        start = info.data.get("start_time")
        if start and v == start:
            raise ValueError("end_time must differ from start_time")
        return v


class AvailabilityPreferenceOut(AvailabilityPreferenceCreate):
    id:      int
    user_id: str

    model_config = {"from_attributes": True}
