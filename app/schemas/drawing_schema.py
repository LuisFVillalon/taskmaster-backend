from datetime import datetime
from pydantic import BaseModel


class DrawingSave(BaseModel):
    image_data_url: str


class DrawingOut(BaseModel):
    user_id: str
    image_data_url: str
    updated_at: datetime

    model_config = {"from_attributes": True}
