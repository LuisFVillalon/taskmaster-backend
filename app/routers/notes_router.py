from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth import UserInfo, get_current_user
from app.database.database import get_db
from app.schemas.note_schema import Note, NoteCreate, NoteUpdate
from app.crud.note_crud import get_notes, create_note, update_note, delete_note

router = APIRouter()


@router.get("/get-notes", response_model=list[Note])
def read_notes(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all notes belonging to the authenticated user."""
    return get_notes(db, current_user.id)


@router.post("/create-note", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_new_note(
    note: NoteCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new note for the authenticated user."""
    return create_note(db, note, current_user.id)


@router.put("/update-note/{note_id}", response_model=Note)
def update_note_by_id(
    note_id: int,
    payload: NoteUpdate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Partially update a note's title, content, and tags."""
    note = update_note(db, note_id, payload, current_user.id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.delete("/del-note/{note_id}", response_model=Note)
def delete_note_by_id(
    note_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a note owned by the authenticated user."""
    note = delete_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note
