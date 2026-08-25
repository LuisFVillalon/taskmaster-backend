"""add layout preference fields

Revision ID: p6q7r8s9t0u1
Revises: n4o5p6q7r8s9
Create Date: 2026-08-24 00:00:02.000001

Adds four columns to profiles so the remaining per-session UI state
(mode switcher, daily brief collapse, dashboard grid/calendar toggle,
notes view mode) persists the same way layout_order already does:
  app_mode              VARCHAR  nullable — 'normal' | 'focus' | 'doodle'
  daily_brief_collapsed BOOLEAN  nullable
  dashboard_view        VARCHAR  nullable — 'grid' | 'calendar'
  notes_view_mode       VARCHAR  nullable — 'cards' | 'folders'
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'p6q7r8s9t0u1'
down_revision: Union[str, Sequence[str], None] = 'n4o5p6q7r8s9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profiles', sa.Column('app_mode', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('daily_brief_collapsed', sa.Boolean(), nullable=True))
    op.add_column('profiles', sa.Column('dashboard_view', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('notes_view_mode', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('profiles', 'notes_view_mode')
    op.drop_column('profiles', 'dashboard_view')
    op.drop_column('profiles', 'daily_brief_collapsed')
    op.drop_column('profiles', 'app_mode')
