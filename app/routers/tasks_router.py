from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.auth import UserInfo, get_current_user
from app.core.http_utils import require_found
from app.database.database import get_db
from app.models.note_model import Note as NoteModel
from app.models.tag_model import Tag as TagModel
from app.models.task_model import Task as TaskModel
from app.schemas.task_schema import Task, TaskCreate
from app.crud.task_crud import get_tasks, create_task, delete_task, update_task_status, update_task

router = APIRouter()


@router.get("/get-tasks", response_model=list[Task])
def read_tasks(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all tasks belonging to the authenticated user."""
    return get_tasks(db, current_user.id)


@router.post("/create-task", response_model=Task)
def create_new_task(
    task: TaskCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new task for the authenticated user."""
    return create_task(db, task, current_user.id)


@router.delete("/del-task/{task_id}", response_model=Task)
def delete_task_by_id(
    task_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a task owned by the authenticated user."""
    return require_found(delete_task(db, task_id, current_user.id), "Task not found")


@router.patch("/update-task-status/{task_id}", response_model=Task)
def update_complete_status_by_id(
    task_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle the completion status of a task."""
    return require_found(update_task_status(db, task_id, current_user.id), "Task not found")


@router.put("/update-task/{task_id}", response_model=Task)
def update_task_by_id(
    task_id: int,
    payload: TaskCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Replace all fields of an existing task."""
    return require_found(update_task(db, task_id, payload, current_user.id), "Task not found")


@router.post("/save-tasks-list", response_model=list[Task])
def create_new_tasks(
    tasks: list[TaskCreate],
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bulk-insert an array of tasks (used by the AI task-plan flow)."""
    return [create_task(db, task, current_user.id) for task in tasks]


_CLAIMABLE_MODELS = {"tasks": TaskModel, "notes": NoteModel, "tags": TagModel}


@router.post("/claim-data", status_code=status.HTTP_200_OK)
def claim_existing_data(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    One-time migration endpoint for existing single-user data.

    Assigns all orphaned rows (user_id IS NULL) to the currently
    authenticated user. Call this once on first sign-up if the user
    had pre-existing local data to import.

    Returns the count of rows claimed per table.
    """
    uid = current_user.id
    claimed = {
        name: db.query(model).filter(model.user_id == None).update(  # noqa: E711
            {"user_id": uid}, synchronize_session=False
        )
        for name, model in _CLAIMABLE_MODELS.items()
    }
    db.commit()
    return {"claimed": claimed}
