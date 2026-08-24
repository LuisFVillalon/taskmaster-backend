"""Add notes, note_tags, and task_note_links tables

Revision ID: c3d4e5f6a1b2
Revises: a1b2c3d4e5f6
Create Date: 2026-03-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a1b2'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. notes table
    op.create_table(
        'notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False, server_default='Untitled Note'),
        sa.Column('content', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # 2. note_tags association table (notes ↔ tags, reuses existing tags)
    op.create_table(
        'note_tags',
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('note_id', 'tag_id'),
    )

    # 3. task_note_links association table (tasks ↔ notes, bidirectional smart linking)
    op.create_table(
        'task_note_links',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'note_id'),
    )


def downgrade() -> None:
    op.drop_table('task_note_links')
    op.drop_table('note_tags')
    op.drop_table('notes')
