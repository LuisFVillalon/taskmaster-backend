"""
Seed data generator for the demo/trial account.

Builds a fresh dataset (tasks, habits + streak history, notes) anchored to
date.today() so the trial always looks current, no matter when someone
clicks "Try Demo". seed_demo_data() wipes the demo user's existing rows
first, so repeated trials always start from the same clean baseline instead
of accumulating whatever a previous visitor left behind.
"""

from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.habit_log_model import HabitLog
from app.models.habit_model import Habit
from app.models.note_model import Note
from app.models.tag_model import Tag
from app.models.task_model import Task


def _wipe_demo_data(db: Session, user_id: str) -> None:
    """Delete all of the demo user's existing rows so each trial starts clean."""
    task_ids = [
        row[0]
        for row in db.execute(
            text("SELECT id FROM tasks WHERE user_id = :uid"), {"uid": user_id}
        ).fetchall()
    ]
    if task_ids:
        db.execute(text("DELETE FROM task_tags WHERE task_id = ANY(:ids)"), {"ids": task_ids})

    # note_tags/habit_tags cascade automatically; task_tags was cleared above.
    for model in (Note, Task, Habit, Tag):
        db.query(model).filter(model.user_id == user_id).delete(synchronize_session=False)
    db.flush()


def _make_tag(db: Session, name: str, color: str, user_id: str) -> Tag:
    tag = Tag(name=name, color=color, user_id=user_id)
    db.add(tag)
    db.flush()
    return tag


def seed_demo_data(db: Session, user_id: str) -> None:
    """Wipe and repopulate the demo account with tasks, habits, and notes
    dated relative to today."""
    _wipe_demo_data(db, user_id)

    today = date.today()
    now = datetime.now(timezone.utc)

    work_tag = _make_tag(db, "Work", "#3b82f6", user_id)
    personal_tag = _make_tag(db, "Personal", "#22c55e", user_id)
    health_tag = _make_tag(db, "Health", "#f97316", user_id)

    # ── Tasks: a mix of overdue, due-today, and upcoming ──────────────────────
    # (title, days offset from today, completed, priority, tags)
    task_defs = [
        ("Send client status report", -3, False, 1, [work_tag]),
        ("Renew car registration", -1, False, None, [personal_tag]),
        ("Book dentist appointment", -5, True, None, [health_tag]),
        ("Finish Q3 budget review", 0, False, 2, [work_tag]),
        ("Team standup notes", 0, True, None, [work_tag]),
        ("Grocery run", 0, False, None, [personal_tag]),
        ("Prep slides for Friday demo", 2, False, 3, [work_tag]),
        ("Plan weekend hike", 4, False, None, [personal_tag, health_tag]),
        ("Annual health checkup", 7, False, None, [health_tag]),
    ]
    for title, offset, completed, priority, tags in task_defs:
        due = today + timedelta(days=offset)
        created = now - timedelta(days=abs(offset) + 1)
        db_task = Task(
            title=title,
            completed=completed,
            priority=priority,
            due_date=datetime.combine(due, time(0, 0)),
            due_time=time(9, 0),
            created_date=created,
            completed_date=created + timedelta(hours=2) if completed else None,
            user_id=user_id,
        )
        db_task.tags = tags
        db.add(db_task)

    # ── Habits: streak history 7-14 days back, all scheduled for today ───────
    # (title, consecutive days logged up to and including today, tags)
    habit_defs = [
        ("Morning meditation", 10, [health_tag]),
        ("Read 20 pages", 6, [personal_tag]),
        ("No-sugar diet", 13, [health_tag]),
    ]
    for title, streak_days, tags in habit_defs:
        habit = Habit(title=title, user_id=user_id, current_streak=streak_days, max_streak=streak_days)
        habit.tags = tags
        db.add(habit)
        db.flush()

        for i in range(streak_days):
            db.add(HabitLog(habit_id=habit.id, logged_date=today - timedelta(days=i)))
        # An older, disconnected log day so the habit's history view has
        # some texture beyond a single unbroken streak.
        db.add(HabitLog(habit_id=habit.id, logged_date=today - timedelta(days=streak_days + 2)))

    # ── Notes: timestamps spanning the last several days ──────────────────────
    note_defs = [
        (
            "Sprint retro takeaways",
            "## What went well\n- Shipped the new dashboard\n\n## What to improve\n- Standups running long",
            6,
            [work_tag],
        ),
        (
            "Recipe: weeknight stir fry",
            "Garlic, ginger, soy sauce, broccoli, chicken thigh. 20 min total.",
            3,
            [],
        ),
        (
            "Book notes - Atomic Habits",
            "Habit stacking: attach a new habit to an existing one.",
            1,
            [personal_tag],
        ),
        (
            "Ideas for demo project",
            "- Add dark mode\n- Export to PDF\n- Keyboard shortcuts",
            0,
            [work_tag],
        ),
    ]
    for title, content, days_ago, tags in note_defs:
        ts = now - timedelta(days=days_ago, hours=3)
        note = Note(title=title, content=content, user_id=user_id, created_date=ts, updated_date=ts)
        note.tags = tags
        db.add(note)

    db.commit()
