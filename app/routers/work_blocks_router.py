"""
Work Blocks — REST endpoints for the Smart Scheduling feature.

Lifecycle
─────────
  POST   /work-blocks           AI service creates a 'suggested' block
  GET    /work-blocks           Frontend fetches all active blocks for calendar render
  PATCH  /work-blocks/{id}      User confirms ('confirmed') or dismisses ('dismissed') a block
  DELETE /work-blocks/{id}      User removes a confirmed block from the calendar
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import UserInfo, get_current_user
from app.crud.work_block_crud import (
    create_work_block,
    delete_work_block,
    get_work_blocks_for_user,
    reschedule_work_block,
    update_work_block_status,
)
from app.database.database import get_db
from app.schemas.work_block_schema import WorkBlockCreate, WorkBlockOut, WorkBlockUpdate

router = APIRouter(prefix="/work-blocks", tags=["work-blocks"])


@router.post("", response_model=WorkBlockOut, status_code=status.HTTP_201_CREATED)
def create_block(
    data: WorkBlockCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Called by the AI service after it has selected the best slot.
    The JWT is forwarded from the frontend, so user isolation is enforced
    by the same auth middleware used by every other endpoint.
    """
    return create_work_block(db, data, current_user.id)


@router.get("", response_model=list[WorkBlockOut])
def list_blocks(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return all suggested and confirmed work blocks for the current user.
    The calendar view calls this alongside /google-calendar/events to
    render both external events and AI-scheduled work sessions.
    """
    return get_work_blocks_for_user(db, current_user.id)


@router.patch("/{block_id}", response_model=WorkBlockOut)
def update_block(
    block_id: int,
    data: WorkBlockUpdate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Three operations share this endpoint:
      • { status: "confirmed" }           — accept a suggested block
      • { status: "dismissed" }           — hard-delete a rejected suggestion
      • { start_time, end_time }          — drag-and-drop reschedule
    The payload schema enforces that exactly one operation is expressed.
    Only blocks owned by the authenticated user can be modified.
    """
    if data.status == "dismissed":
        block = delete_work_block(db, block_id, current_user.id)
    elif data.status is not None:
        block = update_work_block_status(db, block_id, current_user.id, data.status)
    else:
        # Reschedule — start_time and end_time are guaranteed non-None by schema.
        try:
            block = reschedule_work_block(
                db, block_id, current_user.id, data.start_time, data.end_time  # type: ignore[arg-type]
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work block not found",
        )
    return block


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_block(
    block_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Hard-delete a work block — used when the user removes a confirmed block
    from the calendar ("Remove from Calendar" action on TaskItem).
    The dismiss path on suggested blocks also internally hard-deletes via
    the PATCH route; this endpoint exists for the explicit calendar removal case.
    """
    block = delete_work_block(db, block_id, current_user.id)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work block not found",
        )
