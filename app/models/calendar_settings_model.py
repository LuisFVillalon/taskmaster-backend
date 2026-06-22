from sqlalchemy import Column, Integer, String, Date
from app.database.database import Base


class CalendarSettings(Base):
    __tablename__ = "calendar_settings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    sub_header = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    user_id = Column(String(36), nullable=True, index=True)
