from datetime import datetime
from pydantic import BaseModel
from app.schemas.tag_schema import Tag


class NoteBase(BaseModel):
    title: str = "Untitled Note"
    content: str = ""
    tags: list[Tag] = []


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[Tag] | None = None


class Note(NoteBase):
    id: int
    created_date: datetime
    updated_date: datetime
    # user_id set server-side from JWT; exposed in responses, never in requests.
    user_id: str | None = None

    model_config = {"from_attributes": True}
