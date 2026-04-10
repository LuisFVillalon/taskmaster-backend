"""
Availability Preferences — recurring weekly blackout windows for Smart Scheduling.

GET    /availability-preferences          list the user's preferences
POST   /availability-preferences          create a new blackout window
DELETE /availability-preferences/{id}     remove a blackout window
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import UserInfo, get_current_user
from app.crud.availability_preference_crud import (
    create_preference,
    delete_preference,
    list_preferences,
)
from app.database.database import get_db
from app.schemas.availability_preference_schema import (
    AvailabilityPreferenceCreate,
    AvailabilityPreferenceOut,
)

router = APIRouter(prefix="/availability-preferences", tags=["availability-preferences"])


@router.get("", response_model=list[AvailabilityPreferenceOut])
def get_preferences(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all recurring blackout windows for the authenticated user."""
    return list_preferences(db, current_user.id)


@router.post("", response_model=AvailabilityPreferenceOut, status_code=status.HTTP_201_CREATED)
def add_preference(
    data: AvailabilityPreferenceCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new recurring blackout window."""
    return create_preference(db, data, current_user.id)


@router.delete("/{pref_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_preference(
    pref_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a blackout window. Returns 404 if not found or not owned."""
    deleted = delete_preference(db, pref_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability preference not found",
        )
