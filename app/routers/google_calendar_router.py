"""
Google Calendar integration endpoints.

Authentication strategy: Incremental Authorization
───────────────────────────────────────────────────
Supabase already handles sign-in (Supabase JWT).  This router implements a
*separate* Google OAuth 2.0 "Authorization Code" flow that requests only the
calendar.events.readonly scope.  It works for both email/password AND Google
OAuth sign-in users — the two authorizations are completely independent.

Flow:
  1. Frontend uses google.accounts.oauth2.initCodeClient (GSI) with ux_mode='popup'.
  2. User consents; GSI calls the JavaScript callback with an authorization code.
  3. Frontend POSTs the code to POST /google-calendar/connect.
  4. Backend exchanges the code for tokens (redirect_uri="postmessage" for popup).
  5. Tokens are stored in google_calendar_tokens.  Access token is refreshed
     automatically on every GET /google-calendar/events call.

Required .env vars
──────────────────
GOOGLE_CLIENT_ID         — OAuth 2.0 client ID from Google Cloud Console
GOOGLE_CLIENT_SECRET     — OAuth 2.0 client secret from Google Cloud Console

Both are server-side only — the secret is never sent to the browser.
NEXT_PUBLIC_GOOGLE_CLIENT_ID must be set separately in the frontend .env.local.
"""

import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.core.auth import UserInfo, get_current_user
from app.database.database import get_db
from app.models.google_calendar_model import GoogleCalendarToken
from app.schemas.google_calendar_schema import (
    GoogleCalendarConnectRequest,
    GoogleCalendarEventItem,
    GoogleCalendarStatus,
)

router = APIRouter(prefix="/google-calendar", tags=["google-calendar"])

# Google Identity Services (GSI) initCodeClient automatically appends the
# OpenID Connect scopes (openid, email, profile) to every authorization
# request.  google-auth-oauthlib validates that the scopes returned in the
# token response match the scopes declared here; omitting them causes a
# "Scope has changed" error even though we never asked for them explicitly.
_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
_TOKEN_URI = "https://oauth2.googleapis.com/token"
_REVOKE_URI = "https://oauth2.googleapis.com/revoke"

_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _client_config() -> dict:
    """Build the client_config dict expected by google_auth_oauthlib Flow."""
    return {
        "web": {
            "client_id": _CLIENT_ID,
            "client_secret": _CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": _TOKEN_URI,
        }
    }


def _build_credentials(row: GoogleCalendarToken) -> Credentials:
    """Reconstruct a google.oauth2.credentials.Credentials from a stored token row."""
    return Credentials(
        token=row.access_token,
        refresh_token=row.refresh_token,
        token_uri=_TOKEN_URI,
        client_id=_CLIENT_ID,
        client_secret=_CLIENT_SECRET,
        scopes=_SCOPES,
    )


def _get_token_row(db: Session, user_id: str) -> Optional[GoogleCalendarToken]:
    """Return the token row for a user, or None if not connected."""
    return db.get(GoogleCalendarToken, user_id)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/connect", response_model=GoogleCalendarStatus)
def connect_google_calendar(
    body: GoogleCalendarConnectRequest,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Exchange a GSI popup authorization code for tokens and store them.

    The frontend must use google.accounts.oauth2.initCodeClient with
    ux_mode='popup'.  The resulting code is sent here; the backend exchanges
    it using redirect_uri='postmessage' (the special value for popup flows).
    """
    if not _CLIENT_ID or not _CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Calendar integration is not configured on this server.",
        )

    flow = Flow.from_client_config(
        _client_config(),
        scopes=_SCOPES,
        redirect_uri="postmessage",
    )
    try:
        flow.fetch_token(code=body.code)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange authorization code: {exc}",
        )

    creds = flow.credentials
    granted_scope = " ".join(creds.scopes) if creds.scopes else None

    row = _get_token_row(db, current_user.id)
    if row:
        row.access_token = creds.token
        # Google only sends a new refresh_token when the user re-authorizes
        # from scratch.  Keep the existing one if a new one wasn't returned.
        if creds.refresh_token:
            row.refresh_token = creds.refresh_token
        row.expires_at = creds.expiry
        row.scope = granted_scope
    else:
        row = GoogleCalendarToken(
            user_id=current_user.id,
            access_token=creds.token,
            refresh_token=creds.refresh_token,
            expires_at=creds.expiry,
            scope=granted_scope,
        )
        db.add(row)

    db.commit()
    return GoogleCalendarStatus(connected=True)


@router.get("/status", response_model=GoogleCalendarStatus)
def google_calendar_status(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return whether the authenticated user has connected Google Calendar."""
    row = _get_token_row(db, current_user.id)
    return GoogleCalendarStatus(connected=row is not None)


@router.delete("/disconnect", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_google_calendar(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke the user's Google Calendar tokens and remove them from the DB."""
    row = _get_token_row(db, current_user.id)
    if not row:
        return

    # Best-effort token revocation — don't fail the request if Google rejects it
    # (e.g. because the token is already expired or previously revoked).
    try:
        httpx.post(
            _REVOKE_URI,
            params={"token": row.access_token},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5.0,
        )
    except Exception:
        pass

    db.delete(row)
    db.commit()


@router.get("/events", response_model=list[GoogleCalendarEventItem])
def get_google_calendar_events(
    time_min: str = Query(..., description="ISO 8601 datetime with timezone offset (start of range)"),
    time_max: str = Query(..., description="ISO 8601 datetime with timezone offset (end of range)"),
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch events from the user's primary Google Calendar for the given time range.

    Transparently refreshes the access token when expired.  If the refresh
    token has been revoked, the stored credentials are deleted and the
    endpoint returns 403 so the frontend can prompt a reconnection.
    """
    row = _get_token_row(db, current_user.id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Google Calendar is not connected.",
        )

    creds = _build_credentials(row)

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            row.access_token = creds.token
            row.expires_at = creds.expiry
            db.commit()
        except RefreshError:
            # Refresh token revoked — clean up and tell the frontend to reconnect.
            db.delete(row)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Google Calendar access was revoked. Please reconnect.",
            )

    try:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
                maxResults=250,
            )
            .execute()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Google Calendar API error: {exc}",
        )

    events: list[GoogleCalendarEventItem] = []
    for item in result.get("items", []):
        start_obj = item.get("start", {})
        end_obj   = item.get("end",   {})
        is_all_day = "date" in start_obj and "dateTime" not in start_obj
        events.append(
            GoogleCalendarEventItem(
                id=item.get("id", ""),
                title=item.get("summary", "(No title)"),
                start=start_obj.get("date") or start_obj.get("dateTime", ""),
                end=end_obj.get("date")   or end_obj.get("dateTime",   ""),
                is_all_day=is_all_day,
                html_link=item.get("htmlLink", ""),
                description=item.get("description"),
                location=item.get("location"),
            )
        )

    return events
