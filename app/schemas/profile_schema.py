from datetime import datetime
from pydantic import BaseModel


class ProfileSave(BaseModel):
    name: str
    shutoff_time: str | None = None


class ProfileOut(BaseModel):
    user_id: str
    name: str
    created_at: datetime
    shutoff_time: str | None = None

    model_config = {"from_attributes": True}
