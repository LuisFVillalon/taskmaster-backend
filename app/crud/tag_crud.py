from sqlalchemy.orm import Session
from app.models.tag_model import Tag as TagModel
from app.schemas.tag_schema import TagCreate


def get_or_create_tag(db: Session, tag_data, user_id: str) -> TagModel:
    """Return an existing tag matching name+user, or add a new one to the session.

    The caller is responsible for committing the session.  The tag is only
    *added* (not committed) so it can participate in the same transaction as
    the parent task or note.
    """
    tag = (
        db.query(TagModel)
        .filter(TagModel.name == tag_data.name, TagModel.user_id == user_id)
        .first()
    )
    if not tag:
        tag = TagModel(name=tag_data.name, color=tag_data.color, user_id=user_id)
        db.add(tag)
    return tag


def get_tags(db: Session, user_id: str):
    """Return all tags owned by the given user."""
    return db.query(TagModel).filter(TagModel.user_id == user_id).all()


def create_tag(db: Session, tag: TagCreate, user_id: str):
    """Create and persist a new tag, returning the saved record."""
    db_tag = TagModel(name=tag.name, color=tag.color, user_id=user_id)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, tag_id: int, user_id: str):
    """Delete a tag by ID. Returns the deleted record, or None if not found."""
    tag = (
        db.query(TagModel)
        .filter(TagModel.id == tag_id, TagModel.user_id == user_id)
        .first()
    )
    if not tag:
        return None
    db.delete(tag)
    db.commit()
    return tag


def update_tag(db: Session, tag_id: int, tag: TagCreate, user_id: str):
    """Update a tag's name and color. Returns None if not found."""
    db_tag = (
        db.query(TagModel)
        .filter(TagModel.id == tag_id, TagModel.user_id == user_id)
        .first()
    )
    if not db_tag:
        return None
    db_tag.name = tag.name
    db_tag.color = tag.color
    db.commit()
    db.refresh(db_tag)
    return db_tag
