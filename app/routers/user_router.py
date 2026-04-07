"""
Account-management endpoints.

POST /update-password
  Updates the authenticated user's password via the Supabase Admin API.
  Rejected with 403 for any user whose primary provider is not "email"
  (e.g. Google OAuth accounts) — they don't have a local credential to update.

DELETE /delete-account
  1. Removes all user data from the database (tasks, notes, tags, calendar_settings
     and the junction rows that reference them).
  2. Calls the Supabase Admin REST API to hard-delete the auth.users record so the
     e-mail address is freed and no orphaned auth rows remain.

Required .env vars
──────────────────
SUPABASE_URL              — project URL (e.g. https://xyz.supabase.co)
SUPABASE_SERVICE_ROLE_KEY — service-role key (Settings → API → service_role)
"""

import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.auth import UserInfo, get_current_user
from app.database.database import get_db
from app.models.calendar_settings_model import CalendarSettings
from app.models.note_model import Note
from app.models.tag_model import Tag
from app.models.task_model import Task

router = APIRouter()

_OAUTH_PROVIDERS = {"google", "github", "facebook", "twitter", "apple"}


def _supabase_admin_headers() -> dict[str, str]:
    """Return headers for Supabase Admin API calls, or raise if not configured."""
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not service_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server is not configured for account management (missing SUPABASE_SERVICE_ROLE_KEY).",
        )
    return {"Authorization": f"Bearer {service_key}", "apikey": service_key}


def _supabase_url() -> str:
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server is not configured for account management (missing SUPABASE_URL).",
        )
    return url


# ── Password policy (mirrors frontend passwordValidation.ts) ─────────────────

_MIN_LENGTH = 12

# Normalised (lowercase, no spaces) common/breached passwords.
# Mirrors the BLACKLIST in passwordValidation.ts — keep the two in sync.
_BLACKLIST: frozenset[str] = frozenset({
    'password', 'password1', 'password12', 'password123', 'password1234',
    'password12345', 'password123456',
    'qwerty', 'qwerty123', 'qwertyuiop', 'qwertyuiop123',
    '123456789012', '12345678901234', '1234567890',
    'iloveyou1234', 'iloveyouforever',
    'welcome1234', 'welcome123456',
    'sunshine1234', 'princess1234',
    'monkey123456', 'dragon123456',
    'letmein12345', 'letmeinnow',
    'football1234', 'baseball1234',
    'superman1234', 'batman12345',
    'trustno11234', 'master123456',
    'admin12345678', 'administrator',
    'passphrase123', 'correcthorse',
    'mustang12345', 'shadow123456',
    'michael12345', 'jessica12345',
    'abc123456789', 'abcdefghijkl',
    'hunter12345', 'ranger12345',
    'starwars1234', 'starwars12345',
    'liverpool1234', 'chelsea12345',
    'harley12345', 'maverick1234',
})


def _check_password(password: str, email: str | None = None) -> None:
    """
    Raise HTTPException 422 if the password fails the NIST-aligned policy:
      1. Minimum 12 characters
      2. Not in the common-password blacklist
      3. Does not contain the user's email local-part (≥ 4 chars)

    Entropy scoring (zxcvbn equivalent) is enforced on the frontend only;
    the backend focuses on the objective, stateless checks that cannot be
    bypassed by the client.
    """
    if len(password) < _MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password must be at least {_MIN_LENGTH} characters.",
        )

    normalised = password.lower().replace(" ", "")
    if normalised in _BLACKLIST:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password is too common. Please choose something more unique.",
        )

    if email:
        local_part = email.split("@")[0].lower()
        if len(local_part) >= 4 and local_part in normalised:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must not contain your email address.",
            )


# ── Update password ───────────────────────────────────────────────────────────

class PasswordUpdateRequest(BaseModel):
    new_password: str

    @field_validator("new_password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Password cannot be blank.")
        return v


@router.post("/update-password", status_code=204)
async def update_password(
    body: PasswordUpdateRequest,
    current_user: UserInfo = Depends(get_current_user),
):
    """
    Sets a new password for the authenticated user.

    Returns 403 if the account uses a federated identity (Google, GitHub, etc.)
    and has never had a local password set — updating a credential that doesn't
    exist would create a shadow credential and is a security risk.

    Returns 422 if the password violates the NIST-aligned policy.
    """
    if current_user.provider in _OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Your account uses {current_user.provider.capitalize()} sign-in. "
                "Password changes must be made through your identity provider."
            ),
        )

    _check_password(body.new_password, current_user.email)

    headers = _supabase_admin_headers()
    supabase_url = _supabase_url()

    async with httpx.AsyncClient() as client:
        resp = await client.put(
            f"{supabase_url}/auth/v1/admin/users/{current_user.id}",
            headers=headers,
            json={"password": body.new_password},
        )

    if resp.status_code not in (200, 204):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Password update failed: {resp.text}",
        )


# ── Delete account ────────────────────────────────────────────────────────────

@router.delete("/delete-account", status_code=204)
async def delete_account(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user.id

    # ── 1. Remove junction rows that have no user_id column ──────────────────
    # task_tags has no CASCADE, so we must clear it before deleting tasks/tags.
    task_ids = [r[0] for r in db.execute(
        text("SELECT id FROM tasks WHERE user_id = :uid"), {"uid": uid}
    ).fetchall()]
    if task_ids:
        db.execute(
            text("DELETE FROM task_tags WHERE task_id = ANY(:ids)"),
            {"ids": task_ids},
        )

    # ── 2. Delete owned rows (cascade handles note_tags, task_note_links) ────
    db.query(CalendarSettings).filter(CalendarSettings.user_id == uid).delete()
    db.query(Note).filter(Note.user_id == uid).delete()
    db.query(Task).filter(Task.user_id == uid).delete()
    db.query(Tag).filter(Tag.user_id == uid).delete()
    db.commit()

    # ── 3. Delete the Supabase auth user ─────────────────────────────────────
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{_supabase_url()}/auth/v1/admin/users/{uid}",
            headers=_supabase_admin_headers(),
        )

    if resp.status_code not in (200, 204):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Supabase auth deletion failed: {resp.text}",
        )
