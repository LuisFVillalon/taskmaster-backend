from sqlalchemy import Column, Integer, String, Date, UniqueConstraint
from app.database.database import Base


class CalendarSettings(Base):
    __tablename__ = "calendar_settings"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_calendar_settings_user_id"),
    )

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    sub_header = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    user_id = Column(String(36), nullable=True, index=True)
