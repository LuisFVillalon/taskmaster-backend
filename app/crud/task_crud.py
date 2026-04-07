from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import HTTPException
from app.models.tag_model import Tag as TagModel
from app.models.task_model import Task as TaskModel
from app.schemas.task_schema import TaskCreate
from app.crud.tag_crud import get_or_create_tag


def get_tasks(db: Session, user_id: str):
    """Return all tasks owned by the given user."""
    return db.query(TaskModel).filter(TaskModel.user_id == user_id).all()


def _validate_parent_task_id(db: Session, parent_task_id: int, user_id: str) -> None:
    """Raise 400 if the parent task doesn't exist or belongs to a different user."""
    if parent_task_id is None:
        return
    parent_task = (
        db.query(TaskModel)
        .filter(TaskModel.id == parent_task_id, TaskModel.user_id == user_id)
        .first()
    )
    if not parent_task:
        raise HTTPException(
            status_code=400,
            detail=f"Parent task with ID {parent_task_id} not found",
        )



def create_task(db: Session, task: TaskCreate, user_id: str):
    """Create and persist a new task, auto-creating any new tags."""
    now = datetime.now(timezone.utc)
    db_task = TaskModel(
        title=task.title,
        description=task.description,
        category=task.category,
        completed=task.completed,
        urgent=task.urgent,
        due_date=task.due_date,
        due_time=task.due_time,
        created_date=now,
        completed_date=now if task.completed else None,
        estimated_time=task.estimated_time,
        complexity=task.complexity,
        parent_task_id=task.parent_task_id,
        user_id=user_id,
    )
    for tag_data in task.tags:
        db_task.tags.append(get_or_create_tag(db, tag_data, user_id))
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int, user_id: str):
    """Delete a task. Returns the deleted record, or None if not found."""
    task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.user_id == user_id)
        .first()
    )
    if not task:
        return None
    db.delete(task)
    db.commit()
    return task


def update_task_status(db: Session, task_id: int, user_id: str):
    """Toggle a task's completed status and update completed_date accordingly."""
    task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.user_id == user_id)
        .first()
    )
    if not task:
        return None
    task.completed = not task.completed
    task.completed_date = datetime.now(timezone.utc) if task.completed else None
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, task: TaskCreate, user_id: str):
    """Replace all fields of an existing task. Returns None if not found."""
    db_task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.user_id == user_id)
        .first()
    )
    if not db_task:
        return None

    if task.parent_task_id is not None:
        if task.parent_task_id == task_id:
            raise HTTPException(status_code=400, detail="A task cannot be its own parent")
        _validate_parent_task_id(db, task.parent_task_id, user_id)

    db_task.title = task.title
    db_task.description = task.description
    db_task.category = task.category
    db_task.completed = task.completed
    db_task.urgent = task.urgent
    db_task.due_date = task.due_date
    db_task.due_time = task.due_time
    db_task.completed_date = task.completed_date
    db_task.estimated_time = task.estimated_time
    db_task.complexity = task.complexity
    db_task.parent_task_id = task.parent_task_id

    db_task.tags.clear()
    for tag_data in task.tags:
        tag = get_or_create_tag(db, tag_data, user_id)
        db.flush()
        db_task.tags.append(tag)

    db.commit()
    db.refresh(db_task)
    return db_task
