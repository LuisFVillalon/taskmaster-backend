from datetime import date
from sqlalchemy.orm import Session
from app.models.calendar_settings_model import CalendarSettings as CalendarSettingsModel


def get_calendar_settings(db: Session, user_id: str) -> CalendarSettingsModel | None:
    return (
        db.query(CalendarSettingsModel)
        .filter(CalendarSettingsModel.user_id == user_id)
        .first()
    )


def upsert_calendar_settings(
    db: Session, user_id: str, changes: dict
) -> CalendarSettingsModel:
    row = get_calendar_settings(db, user_id)
    if row is None:
        row = CalendarSettingsModel(
            user_id=user_id,
            title=changes.get("title", "Big Picture Calendar"),
            sub_header=changes.get("sub_header", "First Quarter"),
            start_date=changes.get("start_date", date(2026, 1, 1)),
            end_date=changes.get("end_date", date(2026, 3, 31)),
        )
        db.add(row)
    else:
        for key, val in changes.items():
            setattr(row, key, val)
    db.commit()
    db.refresh(row)
    return row
