from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.work_block_model import WorkBlock
from app.schemas.work_block_schema import WorkBlockCreate


def create_work_block(db: Session, data: WorkBlockCreate, user_id: str) -> WorkBlock:
    block = WorkBlock(
        task_id      = data.task_id,
        user_id      = user_id,
        start_time   = data.start_time,
        end_time     = data.end_time,
        status       = data.status,
        ai_reasoning = data.ai_reasoning,
        confidence   = data.confidence,
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


def get_work_blocks_for_user(db: Session, user_id: str) -> list[WorkBlock]:
    """Return all work blocks for a user, ordered by start time."""
    return (
        db.query(WorkBlock)
        .filter(WorkBlock.user_id == user_id)
        .order_by(WorkBlock.start_time)
        .all()
    )


def get_work_block(db: Session, block_id: int, user_id: str) -> WorkBlock | None:
    return (
        db.query(WorkBlock)
        .filter(WorkBlock.id == block_id, WorkBlock.user_id == user_id)
        .first()
    )


def update_work_block_status(
    db: Session, block_id: int, user_id: str, status: str
) -> WorkBlock | None:
    block = get_work_block(db, block_id, user_id)
    if not block:
        return None
    block.status = status
    db.commit()
    db.refresh(block)
    return block


def reschedule_work_block(
    db: Session,
    block_id: int,
    user_id: str,
    start_time: datetime,
    end_time: datetime,
) -> WorkBlock | None:
    """
    Move a work block to a new time window chosen by the user via drag-and-drop.
    Rejects times in the past; does NOT enforce blackout windows because the
    user made a deliberate manual override.
    Returns None if the block doesn't exist or doesn't belong to this user.
    Raises ValueError for a past start_time (caller turns this into a 422).
    """
    block = get_work_block(db, block_id, user_id)
    if not block:
        return None
    now = datetime.now(tz=timezone.utc)
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)
    if start_time <= now:
        raise ValueError("Cannot reschedule to a time in the past")
    block.start_time = start_time
    block.end_time   = end_time
    db.commit()
    db.refresh(block)
    return block


def delete_work_block(db: Session, block_id: int, user_id: str) -> WorkBlock | None:
    """
    Hard-delete a dismissed work block.  The block is expunged from the
    session before the DELETE is committed so its attributes remain readable
    for the router to serialize — expunge detaches the Python object from
    session tracking, keeping loaded attribute values in memory even after
    the row is gone from the database.
    """
    block = get_work_block(db, block_id, user_id)
    if not block:
        return None
    db.expunge(block)
    db.query(WorkBlock).filter(
        WorkBlock.id == block_id,
        WorkBlock.user_id == user_id,
    ).delete(synchronize_session=False)
    db.commit()
    return block
