"""
Demo / trial account endpoints.

Lets a prospective user click "Try Demo" on the login or sign-up page to
instantly explore the app through a fixed, pre-seeded account, with no
sign-up required.

POST /demo/ensure-account   (public)
  Idempotently finds-or-creates the Supabase auth user for the demo account.
  The frontend calls this right before signing in, in case this is the very
  first demo trial and the account doesn't exist yet. Always operates on the
  hardcoded DEMO_EMAIL — never accepts an email from the client — so this
  public endpoint can't be used to probe or create arbitrary accounts.

POST /demo/seed             (authenticated)
  Wipes and repopulates the demo account's tasks/habits/notes with fresh,
  date-relative sample data. Guarded to the demo account's own email, so
  this can never be triggered against a real user's data — that guard is
  the entire separation between demo edits and production accounts; no
  other user can ever hold a JWT whose email matches DEMO_EMAIL.

Required .env vars (shared with user_router.py's account-management endpoints)
──────────────────
SUPABASE_URL              — project URL (e.g. https://xyz.supabase.co)
SUPABASE_SERVICE_ROLE_KEY — service-role key (Settings → API → service_role)

Optional .env vars
──────────────────
DEMO_EMAIL     — defaults to demo@example.com
DEMO_PASSWORD  — defaults to demopassword123
"""

import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import UserInfo, get_current_user
from app.crud.demo_crud import seed_demo_data
from app.database.database import get_db

router = APIRouter(prefix="/demo", tags=["demo"])

DEMO_EMAIL = os.getenv("DEMO_EMAIL", "demo@example.com")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "demopassword123")


def _supabase_admin_headers() -> dict[str, str]:
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not service_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server is not configured for demo mode (missing SUPABASE_SERVICE_ROLE_KEY).",
        )
    return {"Authorization": f"Bearer {service_key}", "apikey": service_key}


def _supabase_url() -> str:
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server is not configured for demo mode (missing SUPABASE_URL).",
        )
    return url


@router.post("/ensure-account", status_code=status.HTTP_204_NO_CONTENT)
async def ensure_demo_account():
    """Create the fixed demo auth user if it doesn't already exist."""
    headers = _supabase_admin_headers()
    base = _supabase_url()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base}/auth/v1/admin/users",
            headers=headers,
            json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD, "email_confirm": True},
        )

    if resp.status_code in (200, 201):
        return
    # Supabase returns 400/422 with a "already been registered" style message
    # once the demo account exists — that's the expected steady state.
    if "already" in resp.text.lower() or "registered" in resp.text.lower():
        return

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Could not provision demo account: {resp.text}",
    )


@router.post("/seed", status_code=status.HTTP_204_NO_CONTENT)
def reset_and_seed_demo_data(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reset the demo account's data to a fresh, date-relative sample set."""
    if current_user.email.lower() != DEMO_EMAIL.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo reset is only available for the demo account.",
        )
    seed_demo_data(db, current_user.id)
