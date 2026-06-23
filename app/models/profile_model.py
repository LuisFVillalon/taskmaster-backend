from sqlalchemy import Column, String, DateTime, func
from app.database.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    user_id = Column(String(36), primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    shutoff_time = Column(String(5), nullable=True)
