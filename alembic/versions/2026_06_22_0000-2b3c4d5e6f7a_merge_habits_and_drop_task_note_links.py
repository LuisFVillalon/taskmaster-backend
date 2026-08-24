"""Merge habits branch and drop_task_note_links branch

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f, j0k1l2m3n4o5
Create Date: 2026-06-22

"""
from typing import Sequence, Union

from alembic import op


revision: str = '2b3c4d5e6f7a'
down_revision: Union[str, Sequence[str], None] = ('1a2b3c4d5e6f', 'j0k1l2m3n4o5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
