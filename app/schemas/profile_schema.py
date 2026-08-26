from datetime import datetime
from pydantic import BaseModel


class ProfileSave(BaseModel):
    name: str
    shutoff_time: str | None = None
    avatar: str | None = None
    theme_accent: str | None = None
    page_style: str | None = None
    day_start_time: str | None = None
    rest_days: list[int] | None = None
    layout_order: list[str] | None = None
    layout_sizes: dict[str, str] | None = None
    app_mode: str | None = None
    daily_brief_collapsed: bool | None = None
    dashboard_view: str | None = None
    notes_view_mode: str | None = None


class ProfileOut(BaseModel):
    user_id: str
    name: str
    created_at: datetime
    shutoff_time: str | None = None
    avatar: str | None = None
    theme_accent: str | None = None
    page_style: str | None = None
    day_start_time: str | None = None
    rest_days: list[int] | None = None
    layout_order: list[str] | None = None
    layout_sizes: dict[str, str] | None = None
    app_mode: str | None = None
    daily_brief_collapsed: bool | None = None
    dashboard_view: str | None = None
    notes_view_mode: str | None = None

    model_config = {"from_attributes": True}
