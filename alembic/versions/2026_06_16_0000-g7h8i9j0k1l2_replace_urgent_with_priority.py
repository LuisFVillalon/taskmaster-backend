"""replace urgent boolean with priority integer

Revision ID: g7h8i9j0k1l2
Revises: f6a1b2c3d4e5
Create Date: 2026-06-16

Why
───
Replaces the binary urgent flag with a numeric priority field so tasks can be
ranked relative to each other.  Priority 1 is the most important; values must
be unique per user.

Existing tasks are backfilled with sequential priority numbers ordered by id
within each user partition, so no data is lost during upgrade.
"""

from alembic import op
import sqlalchemy as sa

revision = 'g7h8i9j0k1l2'
down_revision = 'c4d5e6f7a8b9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('priority', sa.Integer(), nullable=True))

    # Backfill: assign sequential priorities per user ordered by task id
    op.execute("""
        UPDATE tasks t
        SET priority = sub.row_num
        FROM (
            SELECT id,
                   ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY id) AS row_num
            FROM tasks
        ) sub
        WHERE t.id = sub.id
    """)

    op.drop_column('tasks', 'urgent')


def downgrade() -> None:
    op.add_column('tasks', sa.Column('urgent', sa.Boolean(), nullable=True,
                                      server_default=sa.text('false')))
    op.drop_column('tasks', 'priority')
