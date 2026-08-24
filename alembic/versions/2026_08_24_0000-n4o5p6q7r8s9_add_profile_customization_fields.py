"""add profile customization fields

Revision ID: n4o5p6q7r8s9
Revises: m3n4o5p6q7r8
Create Date: 2026-08-24 00:00:00.000001

Adds six columns to profiles, added to support the customizable
calendar/widgets/theming dashboard rebuild:
  avatar          VARCHAR  nullable
  theme_accent    VARCHAR  nullable — hex color string
  page_style      VARCHAR  nullable
  day_start_time  VARCHAR(5) nullable — "HH:MM"
  rest_days       JSON     nullable — list[int], 0=Sun..6=Sat
  layout_order    JSON     nullable — list[str]
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'n4o5p6q7r8s9'
down_revision: Union[str, Sequence[str], None] = 'm3n4o5p6q7r8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profiles', sa.Column('avatar', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('theme_accent', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('page_style', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('day_start_time', sa.String(5), nullable=True))
    op.add_column('profiles', sa.Column('rest_days', sa.JSON(), nullable=True))
    op.add_column('profiles', sa.Column('layout_order', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('profiles', 'layout_order')
    op.drop_column('profiles', 'rest_days')
    op.drop_column('profiles', 'day_start_time')
    op.drop_column('profiles', 'page_style')
    op.drop_column('profiles', 'theme_accent')
    op.drop_column('profiles', 'avatar')
