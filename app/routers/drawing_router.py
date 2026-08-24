"""
Doodle canvas endpoints.

GET    /get-drawing    — returns the authenticated user's saved drawing, or 404
POST   /save-drawing   — upserts the drawing (insert or update)
DELETE /delete-drawing — deletes the drawing if present (idempotent)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import UserInfo, get_current_user
from app.core.http_utils import require_found
from app.crud.drawing_crud import delete_drawing, get_drawing, upsert_drawing
from app.database.database import get_db
from app.schemas.drawing_schema import DrawingOut, DrawingSave

router = APIRouter()


@router.get("/get-drawing", response_model=DrawingOut)
def read_drawing(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return require_found(get_drawing(db, current_user.id), "Drawing not found.")


@router.post("/save-drawing", response_model=DrawingOut)
def save_drawing(
    body: DrawingSave,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return upsert_drawing(db, current_user.id, body)


@router.delete("/delete-drawing", status_code=status.HTTP_204_NO_CONTENT)
def delete_drawing_by_user(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_drawing(db, current_user.id)
