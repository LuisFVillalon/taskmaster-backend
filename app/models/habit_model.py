from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.habit_tag_model import habit_tags


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    color = Column(String, nullable=True)
    user_id = Column(String(36), nullable=True, index=True)
    current_streak = Column(Integer, nullable=False, default=0)
    max_streak = Column(Integer, nullable=False, default=0)

    tags = relationship(
        "Tag",
        secondary=habit_tags,
        back_populates="habits",
    )
