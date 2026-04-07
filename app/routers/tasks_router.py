from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.supabase_client import supabase
from app.core.auth import UserInfo, get_current_user
from app.database.database import get_db
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
    deleted_task = delete_task(db, task_id, current_user.id)
    if not deleted_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return deleted_task


@router.patch("/update-task-status/{task_id}", response_model=Task)
def update_complete_status_by_id(
    task_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle the completion status of a task."""
    task = update_task_status(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/update-task/{task_id}", response_model=Task)
def update_task_by_id(
    task_id: int,
    payload: TaskCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Replace all fields of an existing task."""
    task = update_task(db, task_id, payload, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/save-tasks-list")
async def create_new_tasks(
    tasks: list[TaskCreate],
    current_user: UserInfo = Depends(get_current_user),
):
    """Bulk-insert an array of tasks (used by the AI task-plan flow)."""
    created_tasks = []

    for task in tasks:
        task_data = task.model_dump(mode="json")
        tags = task_data.pop("tags", [])
        # Inject the authenticated user's ID — never trust a client-supplied value.
        task_data["user_id"] = current_user.id

        task_response = supabase.table("tasks").insert(task_data).execute()
        if not task_response.data:
            raise HTTPException(status_code=400, detail="Task insert failed")

        inserted_task = task_response.data[0]
        task_id = inserted_task["id"]

        if tags:
            tag_rows = [{"task_id": task_id, "tag_id": tag["id"]} for tag in tags]
            supabase.table("task_tags").insert(tag_rows).execute()

        created_tasks.append(inserted_task)

    return created_tasks


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
    from app.models.task_model import Task as TaskModel
    from app.models.note_model import Note as NoteModel
    from app.models.tag_model import Tag as TagModel
    from app.models.calendar_settings_model import CalendarSettings as CalendarSettingsModel

    uid = current_user.id

    tasks_claimed = (
        db.query(TaskModel)
        .filter(TaskModel.user_id == None)  # noqa: E711
        .update({"user_id": uid}, synchronize_session=False)
    )
    notes_claimed = (
        db.query(NoteModel)
        .filter(NoteModel.user_id == None)  # noqa: E711
        .update({"user_id": uid}, synchronize_session=False)
    )
    tags_claimed = (
        db.query(TagModel)
        .filter(TagModel.user_id == None)  # noqa: E711
        .update({"user_id": uid}, synchronize_session=False)
    )
    calendar_claimed = (
        db.query(CalendarSettingsModel)
        .filter(CalendarSettingsModel.user_id == None)  # noqa: E711
        .update({"user_id": uid}, synchronize_session=False)
    )

    db.commit()

    return {
        "claimed": {
            "tasks": tasks_claimed,
            "notes": notes_claimed,
            "tags": tags_claimed,
            "calendar_settings": calendar_claimed,
        }
    }
