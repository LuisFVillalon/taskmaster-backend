from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.database.database import Base


class NoteSession(Base):
    __tablename__ = "note_sessions"

    id = Column(Integer, primary_key=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    started_at = Column(DateTime, server_default=func.now(), nullable=False)
    ended_at = Column(DateTime, nullable=True)
