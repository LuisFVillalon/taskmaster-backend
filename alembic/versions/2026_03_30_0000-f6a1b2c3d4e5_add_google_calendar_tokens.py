"""add google_calendar_tokens table

Revision ID: f6a1b2c3d4e5
Revises: e5f6a1b2c3d4
Create Date: 2026-03-30

Why
───
Stores per-user OAuth 2.0 tokens for the Google Calendar integration.
One row per user (user_id is the primary key).  The access token is
refreshed transparently on every /events request; the refresh token
enables long-term background sync without re-prompting the user.

No FK to auth.users is defined because Supabase Auth lives in the
separate 'auth' PostgreSQL schema, which is outside Alembic's scope.
Row-level cascade is handled at the application layer (DELETE /disconnect
removes the row; token rows for deleted Supabase users are cleaned up via
the /delete-account endpoint).

Security note
─────────────
access_token and refresh_token are never exposed through any API
response — this table is only read internally by the google_calendar_router.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'f6a1b2c3d4e5'
down_revision = 'e5f6a1b2c3d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # CREATE TABLE IF NOT EXISTS — idempotent; safe to re-run.
    op.execute("""
        CREATE TABLE IF NOT EXISTS google_calendar_tokens (
            user_id       VARCHAR(36)  PRIMARY KEY,
            access_token  TEXT         NOT NULL,
            refresh_token TEXT,
            expires_at    TIMESTAMP,
            scope         VARCHAR
        )
    """)


def downgrade() -> None:
    op.drop_table('google_calendar_tokens')
