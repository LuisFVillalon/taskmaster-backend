"""Add calendar_settings table

Revision ID: d4e5f6a1b2c3
Revises: c3d4e5f6a1b2
Create Date: 2026-03-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e5f6a1b2c3'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'calendar_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False, server_default='SDSU Academic Calendar'),
        sa.Column('sub_header', sa.String(), nullable=False, server_default='Spring 2026'),
        sa.Column('start_date', sa.Date(), nullable=False, server_default='2026-01-20'),
        sa.Column('end_date', sa.Date(), nullable=False, server_default='2026-05-13'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('calendar_settings')
