"""add layout sizes field

Revision ID: s9t0u1v2w3x4
Revises: r8s9t0u1v2w3
Create Date: 2026-08-25 00:00:00.000001

Adds one column to profiles so per-widget dashboard tile sizes (S/M/W/L)
persist the same way layout_order already does:
  layout_sizes  JSON  nullable — dict[str, str] keyed by widget id
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 's9t0u1v2w3x4'
down_revision: Union[str, Sequence[str], None] = 'r8s9t0u1v2w3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profiles', sa.Column('layout_sizes', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('profiles', 'layout_sizes')
