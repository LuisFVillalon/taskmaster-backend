from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth import UserInfo, get_current_user
from app.database.database import get_db
from app.schemas.calendar_schema import CalendarSettings, CalendarSettingsUpdate
from app.crud.calendar_crud import get_calendar_settings, upsert_calendar_settings

router = APIRouter()


@router.get("/get-calendar-settings", response_model=CalendarSettings)
def read_calendar_settings(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = get_calendar_settings(db, current_user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No calendar settings found")
    return row


@router.patch("/update-calendar-settings", response_model=CalendarSettings)
def update_calendar_settings(
    changes: CalendarSettingsUpdate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return upsert_calendar_settings(db, current_user.id, changes.model_dump(exclude_none=True))
