"""Add habits and habit_tags tables

Revision ID: 1a2b3c4d5e6f
Revises: f6a1b2c3d4e5
Create Date: 2026-06-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, Sequence[str], None] = 'f6a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'habits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(36), nullable=True, index=True),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'habit_tags',
        sa.Column('habit_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['habit_id'], ['habits.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('habit_id', 'tag_id'),
    )


def downgrade() -> None:
    op.drop_table('habit_tags')
    op.drop_table('habits')
