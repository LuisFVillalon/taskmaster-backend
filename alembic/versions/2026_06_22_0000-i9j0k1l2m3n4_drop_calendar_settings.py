"""drop calendar_settings table

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-06-22

Why
───
calendar_settings is no longer used by the application.
"""

from alembic import op
import sqlalchemy as sa


revision      = 'i9j0k1l2m3n4'
down_revision = 'h8i9j0k1l2m3'
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.drop_table('calendar_settings')


def downgrade() -> None:
    op.create_table(
        'calendar_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False, server_default='SDSU Academic Calendar'),
        sa.Column('sub_header', sa.String(), nullable=False, server_default='Spring 2026'),
        sa.Column('start_date', sa.Date(), nullable=False, server_default='2026-01-20'),
        sa.Column('end_date', sa.Date(), nullable=False, server_default='2026-05-13'),
        sa.PrimaryKeyConstraint('id'),
    )
