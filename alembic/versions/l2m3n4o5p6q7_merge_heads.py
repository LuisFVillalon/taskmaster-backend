"""Merge drop_complexity and add_profiles heads

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6, d2e3f4a5b6c7
Create Date: 2026-06-23 00:00:00.000000

"""
from typing import Sequence, Union

revision: str = 'l2m3n4o5p6q7'
down_revision: Union[str, Sequence[str], None] = ('k1l2m3n4o5p6', 'd2e3f4a5b6c7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
