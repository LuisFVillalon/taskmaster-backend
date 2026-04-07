from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.database import Base

task_note_links = Table(
    "task_note_links",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
)
