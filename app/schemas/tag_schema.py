from pydantic import BaseModel


class TagBase(BaseModel):
    name: str
    color: str | None = None


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    # user_id exposed in responses so the frontend knows which tags belong to it.
    user_id: str | None = None

    model_config = {"from_attributes": True}
