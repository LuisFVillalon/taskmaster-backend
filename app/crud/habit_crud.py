from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from app.models.habit_model import Habit
from app.models.habit_log_model import HabitLog
from app.schemas.habit_schema import HabitCreate
from app.crud.tag_crud import get_or_create_tag


# ── Pure streak helpers (accept pre-fetched date collections) ────────────────

def _streak_ending_on(log_dates: set, end_date: date) -> int:
    """Count consecutive logged days ending on end_date (inclusive)."""
    streak = 0
    current = end_date
    while current in log_dates:
        streak += 1
        current -= timedelta(days=1)
    return streak


def _max_streak_from_dates(log_dates: set) -> int:
    """Find the all-time longest consecutive run in log_dates."""
    if not log_dates:
        return 0
    sorted_dates = sorted(log_dates)
    max_run = current_run = 1
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
            current_run += 1
            if current_run > max_run:
                max_run = current_run
        else:
            current_run = 1
    return max_run


# ── Shared toggle core ───────────────────────────────────────────────────────

def _apply_toggle_and_recalc(db: Session, habit: Habit, target_date: date) -> bool:
    """Toggle the log entry for target_date, recalculate streaks with a single DB read.

    Returns True if today is now logged (used to set the logged_today attribute).
    """
    existing_log = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit.id, HabitLog.logged_date == target_date)
        .first()
    )
    if existing_log:
        db.delete(existing_log)
    else:
        db.add(HabitLog(habit_id=habit.id, logged_date=target_date))
    db.flush()

    log_dates = {
        row.logged_date
        for row in db.query(HabitLog.logged_date).filter(HabitLog.habit_id == habit.id).all()
    }
    today = date.today()
    today_logged = today in log_dates
    streak_end = today if today_logged else today - timedelta(days=1)
    habit.current_streak = _streak_ending_on(log_dates, streak_end)
    habit.max_streak = _max_streak_from_dates(log_dates)
    return today_logged


# ── Shared helper ─────────────────────────────────────────────────────────────

def _stamp(habit: Habit, logged: bool) -> Habit:
    """Attach the transient logged_today attribute to a habit instance."""
    setattr(habit, "logged_today", logged)
    return habit


def _is_logged_today(db: Session, habit_id: int) -> bool:
    return (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id, HabitLog.logged_date == date.today())
        .first()
    ) is not None


# ── Public CRUD ──────────────────────────────────────────────────────────────

def get_habits(db: Session, user_id: str):
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    if not habits:
        return habits

    today = date.today()
    habit_ids = [h.id for h in habits]
    logged_today_ids = {
        row.habit_id
        for row in db.query(HabitLog.habit_id)
        .filter(HabitLog.habit_id.in_(habit_ids), HabitLog.logged_date == today)
        .all()
    }
    for habit in habits:
        _stamp(habit, habit.id in logged_today_ids)

    return habits


def create_habit(db: Session, habit: HabitCreate, user_id: str):
    db_habit = Habit(title=habit.title, user_id=user_id)
    for tag_data in habit.tags:
        db_habit.tags.append(get_or_create_tag(db, tag_data, user_id))
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return _stamp(db_habit, False)


def update_habit(db: Session, habit_id: int, habit: HabitCreate, user_id: str):
    db_habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == user_id)
        .first()
    )
    if not db_habit:
        return None

    db_habit.title = habit.title
    db_habit.tags.clear()
    for tag_data in habit.tags:
        db_habit.tags.append(get_or_create_tag(db, tag_data, user_id))

    db.commit()
    db.refresh(db_habit)
    return _stamp(db_habit, _is_logged_today(db, habit_id))


def delete_habit(db: Session, habit_id: int, user_id: str):
    db_habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == user_id)
        .first()
    )
    if not db_habit:
        return None
    db.delete(db_habit)
    db.commit()
    return _stamp(db_habit, False)


def toggle_habit_log(db: Session, habit_id: int, user_id: str):
    """Toggle today's completion log. Updates current_streak and max_streak."""
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == user_id)
        .first()
    )
    if not habit:
        return None
    is_logged_today = _apply_toggle_and_recalc(db, habit, date.today())
    db.commit()
    db.refresh(habit)
    return _stamp(habit, is_logged_today)


def toggle_habit_log_date(db: Session, habit_id: int, user_id: str, target_date: date):
    """Toggle completion for a specific date, then recalculate streaks from scratch."""
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == user_id)
        .first()
    )
    if not habit:
        return None
    today_logged = _apply_toggle_and_recalc(db, habit, target_date)
    db.commit()
    db.refresh(habit)
    return _stamp(habit, today_logged)


def get_habit_history(db: Session, habit_id: int, user_id: str, days: int = 30):
    """Return a list of {date, logged} entries for the past `days` days (including today)."""
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id).first()
    if not habit:
        return None

    today = date.today()
    start = today - timedelta(days=days - 1)

    rows = (
        db.query(HabitLog.logged_date)
        .filter(
            HabitLog.habit_id == habit_id,
            HabitLog.logged_date >= start,
            HabitLog.logged_date <= today,
        )
        .all()
    )
    logged_dates = {row.logged_date for row in rows}

    return [
        {"date": (start + timedelta(days=i)).isoformat(), "logged": (start + timedelta(days=i)) in logged_dates}
        for i in range(days)
    ]


def verify_and_reset_streaks(db: Session, user_id: str):
    """Reset current_streak to 0 for habits whose last log entry is older than yesterday."""
    habits = (
        db.query(Habit)
        .filter(Habit.user_id == user_id, Habit.current_streak > 0)
        .all()
    )
    if not habits:
        return {"reset_count": 0}

    yesterday = date.today() - timedelta(days=1)
    habit_ids = [h.id for h in habits]

    last_log_by_habit = {
        row.habit_id: row.last_date
        for row in db.query(HabitLog.habit_id, func.max(HabitLog.logged_date).label("last_date"))
        .filter(HabitLog.habit_id.in_(habit_ids))
        .group_by(HabitLog.habit_id)
        .all()
    }

    reset_count = 0
    for habit in habits:
        last_date = last_log_by_habit.get(habit.id)
        if last_date is None or last_date < yesterday:
            habit.current_streak = 0
            reset_count += 1

    db.commit()
    return {"reset_count": reset_count}
