from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.task_model import Task as TaskModel
from app.crud.habit_crud import get_habits
from app.crud.profile_crud import get_profile
from app.schemas.debrief_schema import (
    DailyDebriefReport,
    DebriefTaskItem,
    HabitDebriefStatus,
    WorkloadCapacity,
    FocusNextItem,
)

# Tasks at or above this estimated_time (minutes) count as "high effort" for focus_next.
HIGH_EFFORT_MINUTES_THRESHOLD = 120
FOCUS_NEXT_WINDOW_DAYS = 3
FOCUS_NEXT_LIMIT = 5


def _minutes_between(start_str: str, end_str: str) -> float:
    """Minutes from HH:MM start to HH:MM end, assuming end is later the same day
    (or after midnight if end <= start)."""
    start_h, start_m = (int(part) for part in start_str.split(":"))
    end_h, end_m = (int(part) for part in end_str.split(":"))
    start_total = start_h * 60 + start_m
    end_total = end_h * 60 + end_m
    if end_total <= start_total:
        end_total += 24 * 60
    return float(end_total - start_total)


def _priority_sort_key(task: TaskModel):
    return (task.priority is None, task.priority or 0)


def _due_date_only(task: TaskModel) -> date | None:
    """Task.due_date is a DateTime column; normalize to a plain date for comparisons."""
    return task.due_date.date() if task.due_date else None


def _build_workload(profile, due_today: list[TaskModel]) -> WorkloadCapacity:
    is_rest_day = False
    available_minutes = None

    if profile:
        weekday = date.today().isoweekday() % 7  # 0=Sun..6=Sat, matches Profile.rest_days
        is_rest_day = bool(profile.rest_days) and weekday in profile.rest_days
        if profile.day_start_time and profile.shutoff_time:
            available_minutes = _minutes_between(profile.day_start_time, profile.shutoff_time)

    committed_minutes = sum(float(t.estimated_time) for t in due_today if t.estimated_time)

    utilization_pct = None
    is_overcommitted = False
    if available_minutes:
        utilization_pct = round((committed_minutes / available_minutes) * 100, 1)
        is_overcommitted = committed_minutes > available_minutes

    return WorkloadCapacity(
        is_rest_day=is_rest_day,
        available_minutes=available_minutes,
        committed_minutes=committed_minutes,
        utilization_pct=utilization_pct,
        is_overcommitted=is_overcommitted,
    )


def _build_focus_next(all_open: list[TaskModel], today: date) -> list[FocusNextItem]:
    window_end = today + timedelta(days=FOCUS_NEXT_WINDOW_DAYS)
    upcoming = [t for t in all_open if _due_date_only(t) and today < _due_date_only(t) <= window_end]

    high_priority = sorted((t for t in upcoming if t.priority is not None), key=_priority_sort_key)
    high_effort = sorted(
        (
            t for t in upcoming
            if t.priority is None
            and t.estimated_time
            and float(t.estimated_time) >= HIGH_EFFORT_MINUTES_THRESHOLD
        ),
        key=lambda t: float(t.estimated_time),
        reverse=True,
    )

    items = [
        FocusNextItem(
            task_id=t.id, title=t.title, priority=t.priority,
            due_date=t.due_date, estimated_time=t.estimated_time,
            reason="high_priority",
        )
        for t in high_priority
    ] + [
        FocusNextItem(
            task_id=t.id, title=t.title, priority=t.priority,
            due_date=t.due_date, estimated_time=t.estimated_time,
            reason="upcoming_high_effort",
        )
        for t in high_effort
    ]
    return items[:FOCUS_NEXT_LIMIT]


def build_daily_debrief(db: Session, user_id: str) -> DailyDebriefReport:
    """Assemble the daily debrief report: overdue/due-today tasks, habit status,
    workload capacity, and a unified 'focus next' recommendation block."""
    today = date.today()

    open_tasks = (
        db.query(TaskModel)
        .filter(TaskModel.user_id == user_id, TaskModel.completed == False)  # noqa: E712
        .all()
    )
    overdue = sorted(
        (t for t in open_tasks if _due_date_only(t) and _due_date_only(t) < today),
        key=lambda t: (_due_date_only(t), _priority_sort_key(t)),
    )
    due_today = sorted(
        (t for t in open_tasks if _due_date_only(t) == today),
        key=_priority_sort_key,
    )

    habits = get_habits(db, user_id)
    habit_status = [HabitDebriefStatus.model_validate(h) for h in habits]

    profile = get_profile(db, user_id)
    workload = _build_workload(profile, due_today)

    focus_next = _build_focus_next(open_tasks, today)

    return DailyDebriefReport(
        report_date=today,
        overdue_tasks=[DebriefTaskItem.model_validate(t) for t in overdue],
        due_today_tasks=[DebriefTaskItem.model_validate(t) for t in due_today],
        habit_status=habit_status,
        workload=workload,
        focus_next=focus_next,
    )
