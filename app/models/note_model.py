from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.note_tag_model import note_tags
from app.models.task_note_model import task_note_links


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, default="Untitled Note")
    content = Column(Text, nullable=False, default="")
    created_date = Column(DateTime, server_default=func.now(), nullable=False)
    updated_date = Column(DateTime, server_default=func.now(), nullable=False)
    user_id = Column(String(36), nullable=True, index=True)

    tags = relationship(
        "Tag",
        secondary=note_tags,
        back_populates="notes",
    )
    linked_tasks = relationship(
        "Task",
        secondary=task_note_links,
        back_populates="linked_notes",
    )
