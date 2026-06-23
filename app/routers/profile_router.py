"""
Profile endpoints.

GET  /get-profile   — returns the authenticated user's profile row, or 404
POST /save-profile  — upserts the profile (insert or update)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import UserInfo, get_current_user
from app.database.database import get_db
from app.models.profile_model import Profile
from app.schemas.profile_schema import ProfileOut, ProfileSave

router = APIRouter()


@router.get("/get-profile", response_model=ProfileOut)
def get_profile(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    return profile


@router.post("/save-profile", response_model=ProfileOut)
def save_profile(
    body: ProfileSave,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile is None:
        profile = Profile(user_id=current_user.id, name=body.name, shutoff_time=body.shutoff_time)
        db.add(profile)
    else:
        profile.name = body.name
        profile.shutoff_time = body.shutoff_time
    db.commit()
    db.refresh(profile)
    return profile
