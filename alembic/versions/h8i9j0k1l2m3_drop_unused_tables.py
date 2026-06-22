"""drop work_blocks, availability_preferences, and google_calendar_tokens tables

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-06-22

Why
───
These three tables are no longer used by the application. The work_blocks and
availability_preferences tables supported a Smart Scheduling feature that was
removed, and google_calendar_tokens stored OAuth tokens for a Google Calendar
integration that has also been removed.
"""

from alembic import op

revision      = 'h8i9j0k1l2m3'
down_revision = 'g7h8i9j0k1l2'
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_work_blocks_user_id")
    op.execute("DROP INDEX IF EXISTS ix_work_blocks_task_id")
    op.execute("DROP TABLE IF EXISTS work_blocks")

    op.execute("DROP INDEX IF EXISTS ix_availability_preferences_user_id")
    op.execute("DROP TABLE IF EXISTS availability_preferences")

    op.execute("DROP TABLE IF EXISTS google_calendar_tokens")


def downgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS google_calendar_tokens (
            id            SERIAL       PRIMARY KEY,
            user_id       VARCHAR(36)  NOT NULL UNIQUE,
            access_token  TEXT         NOT NULL,
            refresh_token TEXT,
            token_expiry  TIMESTAMPTZ,
            created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS availability_preferences (
            id         SERIAL       PRIMARY KEY,
            user_id    VARCHAR(36)  NOT NULL,
            day_of_week INTEGER     NOT NULL,
            start_time TIME         NOT NULL,
            end_time   TIME         NOT NULL,
            created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_availability_preferences_user_id "
        "ON availability_preferences (user_id)"
    )

    op.execute("""
        CREATE TABLE IF NOT EXISTS work_blocks (
            id           SERIAL       PRIMARY KEY,
            task_id      INTEGER      NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            user_id      VARCHAR(36)  NOT NULL,
            start_time   TIMESTAMPTZ  NOT NULL,
            end_time     TIMESTAMPTZ  NOT NULL,
            status       VARCHAR(20)  NOT NULL DEFAULT 'suggested',
            ai_reasoning TEXT,
            confidence   FLOAT,
            created_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_work_blocks_user_id ON work_blocks (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_work_blocks_task_id ON work_blocks (task_id)")
