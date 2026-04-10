"""add availability_preferences table

Revision ID: c4d5e6f7a8b9
Revises: b2c3d4e5f6a1
Create Date: 2026-04-10

Why
───
Stores recurring weekly blackout windows so the AI scheduler never suggests
work blocks during times the user is unavailable (gym, classes, family time, etc.).

Schema notes
────────────
• day_of_week  JS Date.getDay() convention: 0 = Sunday … 6 = Saturday.
               The gap-finder converts this to Python's weekday() at query time.
• start_time / end_time  "HH:MM" strings in UTC — same timezone the gap-finder
               uses for its working-hour window (_WORK_START/_WORK_END in scheduleTask.py).
• label        Optional human-readable name shown in the UI (e.g. "Gym", "Class").
• No ON DELETE CASCADE needed — rows are scoped to user_id (a string UUID),
               not a FK to a users table.
"""

from alembic import op

revision      = 'c4d5e6f7a8b9'
down_revision = 'b2c3d4e5f6a1'
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS availability_preferences (
            id          SERIAL       PRIMARY KEY,
            user_id     VARCHAR(36)  NOT NULL,
            day_of_week SMALLINT     NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
            start_time  VARCHAR(5)   NOT NULL,
            end_time    VARCHAR(5)   NOT NULL,
            label       TEXT
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_availability_preferences_user_id "
        "ON availability_preferences (user_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_availability_preferences_user_id")
    op.drop_table("availability_preferences")
