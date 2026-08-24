"""drop_habit_color

Revision ID: c1d2e3f4a5b6
Revises: b5c18f2ef6ef
Create Date: 2026-06-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'b5c18f2ef6ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('habits', 'color')


def downgrade() -> None:
    op.add_column('habits', sa.Column('color', sa.String(), nullable=True))
