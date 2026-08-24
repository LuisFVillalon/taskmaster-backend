"""Add habit_logs table

Revision ID: 3c4d5e6f7a8b
Revises: 2b3c4d5e6f7a
Create Date: 2026-06-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3c4d5e6f7a8b'
down_revision: Union[str, Sequence[str], None] = '2b3c4d5e6f7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'habit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('habit_id', sa.Integer(), nullable=False),
        sa.Column('logged_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.ForeignKeyConstraint(['habit_id'], ['habits.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('habit_id', 'logged_date', name='uq_habit_logs_habit_date'),
    )
    op.create_index('ix_habit_logs_habit_id', 'habit_logs', ['habit_id'])


def downgrade() -> None:
    op.drop_index('ix_habit_logs_habit_id', table_name='habit_logs')
    op.drop_table('habit_logs')
