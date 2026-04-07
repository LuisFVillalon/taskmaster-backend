from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth import UserInfo, get_current_user
from app.database.database import get_db
from app.schemas.calendar_settings_schema import CalendarSettings, CalendarSettingsUpdate
from app.crud.calendar_settings_crud import get_settings_or_none, update_settings

router = APIRouter()


@router.get("/get-calendar-settings", response_model=CalendarSettings)
def read_settings(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the user's calendar settings, or 404 if they haven't saved any yet.

    New users receive a 404 with detail="no_settings" so the frontend can
    display its own local defaults without writing a row to the database.
    """
    settings = get_settings_or_none(db, current_user.id)
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no_settings")
    return settings


@router.patch("/update-calendar-settings", response_model=CalendarSettings)
def patch_settings(
    payload: CalendarSettingsUpdate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Persist calendar setting changes; creates the row on first save."""
    return update_settings(db, payload, current_user.id)
