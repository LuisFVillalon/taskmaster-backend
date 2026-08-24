"""add profiles table

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-06-23 00:00:00.000000

Creates the profiles table:
  user_id      VARCHAR(36) PRIMARY KEY — Supabase auth UUID
  name         VARCHAR     NOT NULL
  created_at   TIMESTAMP   server default now()
  shutoff_time VARCHAR(5)  nullable — "HH:MM" e.g. "22:00"
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd2e3f4a5b6c7'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'profiles',
        sa.Column('user_id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('shutoff_time', sa.String(5), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('profiles')
