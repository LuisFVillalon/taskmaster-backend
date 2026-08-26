from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date as date_type
from app.core.auth import UserInfo, get_current_user
from app.core.http_utils import require_found
from app.database.database import get_db
from app.schemas.note_schema import Note, NoteCreate, NoteUpdate
from app.schemas.note_session_schema import NoteSession, NoteSessionStart, NoteTimeSpent, NoteSessionReapResult
from app.crud.note_crud import get_notes, create_note, update_note, delete_note
from app.crud.note_session_crud import (
    start_session,
    end_session,
    get_total_time_seconds,
    get_total_time_by_note,
    get_time_by_note_for_range,
    reap_stale_sessions,
)

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
    return require_found(update_note(db, note_id, payload, current_user.id), "Note not found")


@router.delete("/del-note/{note_id}", response_model=Note)
def delete_note_by_id(
    note_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a note owned by the authenticated user."""
    return require_found(delete_note(db, note_id, current_user.id), "Note not found")


@router.post("/note-session/start", response_model=NoteSession, status_code=status.HTTP_201_CREATED)
def start_note_session(
    payload: NoteSessionStart,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new editing session for a note. Close it via /note-session/end/{id}."""
    return require_found(start_session(db, payload.note_id, current_user.id), "Note not found")


@router.put("/note-session/end/{session_id}", response_model=NoteSession)
def end_note_session(
    session_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Close an open editing session, recording its end time."""
    return require_found(end_session(db, session_id, current_user.id), "Session not found or already ended")


@router.get("/note-session/total/{note_id}", response_model=NoteTimeSpent)
def read_note_time_spent(
    note_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return total time (in seconds) spent editing a note, summed across all closed sessions."""
    return {"note_id": note_id, "total_seconds": get_total_time_seconds(db, note_id, current_user.id)}


@router.get("/note-session/totals", response_model=list[NoteTimeSpent])
def read_all_note_time_spent(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return total time (in seconds) spent per note, for every note with at least one closed session."""
    return [
        {"note_id": note_id, "total_seconds": total_seconds}
        for note_id, total_seconds in get_total_time_by_note(db, current_user.id)
    ]


@router.get("/note-session/totals-range", response_model=list[NoteTimeSpent])
def read_note_time_spent_for_range(
    start_date: str = Query(...),
    end_date: str = Query(...),
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return total time (in seconds) spent per note, for closed sessions ended within [start_date, end_date]."""
    try:
        start = date_type.fromisoformat(start_date)
        end = date_type.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD.")
    if start > end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="start_date must not be after end_date.")
    return [
        {"note_id": note_id, "total_seconds": total_seconds}
        for note_id, total_seconds in get_time_by_note_for_range(db, current_user.id, start, end)
    ]


@router.post("/note-session/reap", response_model=NoteSessionReapResult, status_code=status.HTTP_200_OK)
def reap_stale_note_sessions(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Force-close the user's own sessions left open too long (crashed tab, force-quit, etc)."""
    return {"reaped_count": reap_stale_sessions(db, current_user.id)}
