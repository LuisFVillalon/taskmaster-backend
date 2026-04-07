from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.tag_schema import Tag


class NoteBase(BaseModel):
    title: str = "Untitled Note"
    content: str = ""
    tags: List[Tag] = []


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[Tag]] = None


class Note(NoteBase):
    id: int
    created_date: datetime
    updated_date: datetime
    # user_id set server-side from JWT; exposed in responses, never in requests.
    user_id: Optional[str] = None

    model_config = {"from_attributes": True}
