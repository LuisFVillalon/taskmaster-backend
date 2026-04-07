from pydantic import BaseModel
from typing import Optional


class TagBase(BaseModel):
    name: str
    color: Optional[str] = None


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    # user_id exposed in responses so the frontend knows which tags belong to it.
    user_id: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
