"""add_habit_estimated_time

Revision ID: q7r8s9t0u1v2
Revises: p6q7r8s9t0u1
Create Date: 2026-08-24 00:03:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'q7r8s9t0u1v2'
down_revision: Union[str, Sequence[str], None] = 'p6q7r8s9t0u1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('habits', sa.Column('estimated_time', sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade() -> None:
    op.drop_column('habits', 'estimated_time')
