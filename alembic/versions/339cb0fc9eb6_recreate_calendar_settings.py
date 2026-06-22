"""recreate_calendar_settings

Revision ID: 339cb0fc9eb6
Revises: 2b3c4d5e6f7a
Create Date: 2026-06-22 14:05:44.726023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '339cb0fc9eb6'
down_revision: Union[str, Sequence[str], None] = '2b3c4d5e6f7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'calendar_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('sub_header', sa.String(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_calendar_settings_id', 'calendar_settings', ['id'])
    op.create_index('ix_calendar_settings_user_id', 'calendar_settings', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_calendar_settings_user_id', table_name='calendar_settings')
    op.drop_index('ix_calendar_settings_id', table_name='calendar_settings')
    op.drop_table('calendar_settings')
