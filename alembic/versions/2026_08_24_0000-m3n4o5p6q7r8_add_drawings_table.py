"""add drawings table

Revision ID: m3n4o5p6q7r8
Revises: l2m3n4o5p6q7
Create Date: 2026-08-24 00:00:00.000000

Creates the drawings table (doodle canvas), one row per user:
  user_id         VARCHAR(36) PRIMARY KEY — Supabase auth UUID
  image_data_url  TEXT        NOT NULL — base64 PNG data URL
  updated_at      TIMESTAMP   server default now(), updated on write
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'm3n4o5p6q7r8'
down_revision: Union[str, Sequence[str], None] = 'l2m3n4o5p6q7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'drawings',
        sa.Column('user_id', sa.String(36), primary_key=True),
        sa.Column('image_data_url', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('drawings')
