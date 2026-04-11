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
