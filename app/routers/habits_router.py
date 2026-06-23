from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date as date_type
from app.core.auth import UserInfo, get_current_user
from app.core.http_utils import require_found
from app.database.database import get_db
from app.schemas.habit_schema import HabitCreate, HabitResponse, HabitHistoryEntry, HabitToggleDateRequest
from app.crud.habit_crud import (
    get_habits,
    create_habit,
    update_habit,
    delete_habit,
    toggle_habit_log,
    verify_and_reset_streaks,
    get_habit_history,
    toggle_habit_log_date,
)

router = APIRouter()


@router.get("/get-habits", response_model=list[HabitResponse])
def read_habits(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all habits belonging to the authenticated user, with today's completion state."""
    return get_habits(db, current_user.id)


@router.post("/create-habit", response_model=HabitResponse)
def create_new_habit(
    habit: HabitCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new habit for the authenticated user."""
    return create_habit(db, habit, current_user.id)


@router.put("/update-habit/{habit_id}", response_model=HabitResponse)
def update_habit_by_id(
    habit_id: int,
    payload: HabitCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a habit's title, color, and tags."""
    return require_found(update_habit(db, habit_id, payload, current_user.id), "Habit not found")


@router.delete("/del-habit/{habit_id}", response_model=HabitResponse)
def delete_habit_by_id(
    habit_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a habit and all its logs (CASCADE)."""
    return require_found(delete_habit(db, habit_id, current_user.id), "Habit not found")


@router.patch("/toggle-habit/{habit_id}", response_model=HabitResponse)
def toggle_habit_completion(
    habit_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle today's completion for a habit. Updates current_streak and max_streak accordingly."""
    return require_found(toggle_habit_log(db, habit_id, current_user.id), "Habit not found")


@router.post("/verify-streaks", status_code=status.HTTP_200_OK)
def verify_habit_streaks(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reset current_streak to 0 for any habits whose last log is older than yesterday."""
    return verify_and_reset_streaks(db, current_user.id)


@router.get("/habit-history/{habit_id}", response_model=list[HabitHistoryEntry])
def read_habit_history(
    habit_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the logged/not-logged status for the past 30 days for a habit."""
    return require_found(get_habit_history(db, habit_id, current_user.id), "Habit not found")


@router.patch("/toggle-habit-date/{habit_id}", response_model=HabitResponse)
def toggle_habit_completion_date(
    habit_id: int,
    payload: HabitToggleDateRequest,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle completion for a specific past date (or today). Recalculates streaks from scratch."""
    try:
        target = date_type.fromisoformat(payload.date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD.")
    if target > date_type.today():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot log future dates.")
    return require_found(toggle_habit_log_date(db, habit_id, current_user.id, target), "Habit not found")
