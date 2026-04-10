from sqlalchemy.orm import Session

from app.models.availability_preference_model import AvailabilityPreference
from app.schemas.availability_preference_schema import AvailabilityPreferenceCreate


def list_preferences(db: Session, user_id: str) -> list[AvailabilityPreference]:
    return (
        db.query(AvailabilityPreference)
        .filter(AvailabilityPreference.user_id == user_id)
        .order_by(AvailabilityPreference.day_of_week, AvailabilityPreference.start_time)
        .all()
    )


def create_preference(
    db: Session, data: AvailabilityPreferenceCreate, user_id: str
) -> AvailabilityPreference:
    pref = AvailabilityPreference(
        user_id     = user_id,
        day_of_week = data.day_of_week,
        start_time  = data.start_time,
        end_time    = data.end_time,
        label       = data.label,
    )
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref


def delete_preference(
    db: Session, pref_id: int, user_id: str
) -> bool:
    """Delete the preference and return True, or return False if not found / not owned."""
    pref = (
        db.query(AvailabilityPreference)
        .filter(
            AvailabilityPreference.id == pref_id,
            AvailabilityPreference.user_id == user_id,
        )
        .first()
    )
    if not pref:
        return False
    db.delete(pref)
    db.commit()
    return True
