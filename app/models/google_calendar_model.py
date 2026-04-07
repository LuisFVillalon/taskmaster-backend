from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.database.database import Base


class GoogleCalendarToken(Base):
    """Stores OAuth tokens for the Google Calendar integration (one row per user)."""

    __tablename__ = "google_calendar_tokens"

    user_id = Column(String(36), primary_key=True)
    access_token = Column(String, nullable=False)
    # refresh_token is nullable because the first auth may not return one if the
    # user previously granted access (Google only sends it on the first grant or
    # after explicit revocation).
    refresh_token = Column(String, nullable=True)
    # Stored as a naive UTC datetime to match google.oauth2.credentials.Credentials.expiry.
    expires_at = Column(DateTime, nullable=True)
    # Space-separated OAuth scopes that were granted (e.g. "https://www.googleapis.com/auth/calendar.events.readonly").
    scope = Column(String, nullable=True)
