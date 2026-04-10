from sqlalchemy import Column, Integer, SmallInteger, String, Text

from app.database.database import Base


class AvailabilityPreference(Base):
    """Recurring weekly blackout window — times when the user is not available
    for AI-scheduled work blocks.

    day_of_week follows the JS Date.getDay() convention: 0 = Sunday … 6 = Saturday.
    start_time / end_time are "HH:MM" strings in UTC (matching the working-hour
    window used by the gap-finder, which also operates in UTC).
    """

    __tablename__ = "availability_preferences"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(String(36), nullable=False, index=True)
    day_of_week = Column(SmallInteger, nullable=False)   # 0 Sun … 6 Sat
    start_time  = Column(String(5), nullable=False)      # "HH:MM"
    end_time    = Column(String(5), nullable=False)      # "HH:MM"
    label       = Column(Text, nullable=True)            # e.g. "Gym", "Class"
