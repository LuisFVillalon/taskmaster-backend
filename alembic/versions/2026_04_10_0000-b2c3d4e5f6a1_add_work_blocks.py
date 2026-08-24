"""add work_blocks table

Revision ID: b2c3d4e5f6a1
Revises: f6a1b2c3d4e5
Create Date: 2026-04-10

Why
───
Stores AI-suggested and user-confirmed work blocks for the Smart Scheduling
feature.  A work block is a time interval (start_time → end_time) during which
the user should work on a specific task — distinct from the task's due_date,
which is only a point-in-time deadline.

Schema notes
────────────
• status  'suggested' → user has not yet accepted or dismissed
           'confirmed' → user accepted; calendar renders it solid
           'dismissed' → user dismissed; row kept for audit but hidden from UI
• ai_reasoning  one sentence from gpt-4o-mini explaining why this slot
• confidence    0.0–1.0 score returned by the AI along with the reasoning
• ON DELETE CASCADE  if the parent task is deleted, its work blocks are removed

estimated_hours column
──────────────────────
The tasks table already has an `estimated_time` column (Numeric) that stores
the same value (task duration in hours).  Adding a second column would create
ambiguity, so we intentionally omit it here and read estimated_time directly
in the scheduling service.
"""

from alembic import op

revision      = 'b2c3d4e5f6a1'
down_revision = 'f6a1b2c3d4e5'
branch_labels = None
depends_on    = None


def upgrade() -> None:
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


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_work_blocks_user_id")
    op.execute("DROP INDEX IF EXISTS ix_work_blocks_task_id")
    op.drop_table("work_blocks")
