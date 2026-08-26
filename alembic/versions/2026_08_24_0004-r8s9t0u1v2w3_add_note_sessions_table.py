"""add_note_sessions_table

Revision ID: r8s9t0u1v2w3
Revises: q7r8s9t0u1v2
Create Date: 2026-08-24 00:04:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'r8s9t0u1v2w3'
down_revision: Union[str, Sequence[str], None] = 'q7r8s9t0u1v2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'note_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_note_sessions_note_id', 'note_sessions', ['note_id'])
    op.create_index('ix_note_sessions_user_id', 'note_sessions', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_note_sessions_user_id', table_name='note_sessions')
    op.drop_index('ix_note_sessions_note_id', table_name='note_sessions')
    op.drop_table('note_sessions')
