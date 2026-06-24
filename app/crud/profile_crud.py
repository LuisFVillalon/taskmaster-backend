from sqlalchemy.orm import Session
from app.models.profile_model import Profile
from app.schemas.profile_schema import ProfileSave


def get_profile(db: Session, user_id: str) -> Profile | None:
    return db.query(Profile).filter(Profile.user_id == user_id).first()


def upsert_profile(db: Session, user_id: str, body: ProfileSave) -> Profile:
    profile = get_profile(db, user_id)
    if profile is None:
        profile = Profile(user_id=user_id, name=body.name, shutoff_time=body.shutoff_time)
        db.add(profile)
    else:
        profile.name = body.name
        profile.shutoff_time = body.shutoff_time
    db.commit()
    db.refresh(profile)
    return profile
