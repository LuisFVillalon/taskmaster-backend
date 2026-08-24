"""Drop task_note_links table

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-06-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'j0k1l2m3n4o5'
down_revision: Union[str, Sequence[str], None] = 'i9j0k1l2m3n4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('task_note_links')


def downgrade() -> None:
    op.create_table(
        'task_note_links',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'note_id'),
    )
