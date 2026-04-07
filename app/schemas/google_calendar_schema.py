from typing import Optional
from pydantic import BaseModel


class GoogleCalendarConnectRequest(BaseModel):
    """Request body for POST /google-calendar/connect."""
    code: str


class GoogleCalendarStatus(BaseModel):
    """Whether the authenticated user has connected Google Calendar."""
    connected: bool


class GoogleCalendarEventItem(BaseModel):
    """A single Google Calendar event mapped to a serialisable shape."""
    id: str
    title: str
    # ISO date ("YYYY-MM-DD") for all-day events; ISO datetime for timed events.
    start: str
    end: str
    is_all_day: bool
    html_link: str
    description: Optional[str] = None
    location: Optional[str] = None
