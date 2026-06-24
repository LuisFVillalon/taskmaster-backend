"""
Profile endpoints.

GET  /get-profile   — returns the authenticated user's profile row, or 404
POST /save-profile  — upserts the profile (insert or update)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import UserInfo, get_current_user
from app.core.http_utils import require_found
from app.crud.profile_crud import get_profile, upsert_profile
from app.database.database import get_db
from app.schemas.profile_schema import ProfileOut, ProfileSave

router = APIRouter()


@router.get("/get-profile", response_model=ProfileOut)
def read_profile(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return require_found(get_profile(db, current_user.id), "Profile not found.")


@router.post("/save-profile", response_model=ProfileOut)
def save_profile(
    body: ProfileSave,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return upsert_profile(db, current_user.id, body)
