from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import UserInfo, get_current_user
from app.database.database import get_db
from app.schemas.debrief_schema import DailyDebriefReport
from app.crud.debrief_crud import build_daily_debrief

router = APIRouter()


@router.get("/daily-debrief", response_model=DailyDebriefReport)
def read_daily_debrief(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authenticated user's daily debrief: overdue/due-today tasks,
    habit status, workload capacity, and unified focus-next recommendations."""
    return build_daily_debrief(db, current_user.id)
