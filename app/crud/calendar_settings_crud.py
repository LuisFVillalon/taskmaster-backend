from sqlalchemy.orm import Session
from app.models.calendar_settings_model import CalendarSettings as CalendarSettingsModel
from app.schemas.calendar_settings_schema import CalendarSettingsUpdate


def get_settings_or_none(db: Session, user_id: str) -> CalendarSettingsModel | None:
    """Return the settings row for this user, or None if they haven't saved any yet."""
    return (
        db.query(CalendarSettingsModel)
        .filter(CalendarSettingsModel.user_id == user_id)
        .first()
    )


def update_settings(
    db: Session, payload: CalendarSettingsUpdate, user_id: str
) -> CalendarSettingsModel:
    """Persist calendar setting changes for a user.

    On first save the row is created from the payload values.  Subsequent
    saves apply only the fields present in the payload (partial update).
    """
    settings = get_settings_or_none(db, user_id)
    if not settings:
        settings = CalendarSettingsModel(
            title=payload.title or "",
            sub_header=payload.sub_header or "",
            start_date=payload.start_date,
            end_date=payload.end_date,
            user_id=user_id,
        )
        db.add(settings)
    else:
        if payload.title is not None:
            settings.title = payload.title
        if payload.sub_header is not None:
            settings.sub_header = payload.sub_header
        if payload.start_date is not None:
            settings.start_date = payload.start_date
        if payload.end_date is not None:
            settings.end_date = payload.end_date
    db.commit()
    db.refresh(settings)
    return settings
