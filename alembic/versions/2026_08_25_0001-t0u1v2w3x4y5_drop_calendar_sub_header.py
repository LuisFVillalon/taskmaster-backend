"""drop calendar_settings sub_header

Revision ID: t0u1v2w3x4y5
Revises: s9t0u1v2w3x4
Create Date: 2026-08-25 00:01:00.000000

Term Tracker no longer has a subheading field.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 't0u1v2w3x4y5'
down_revision: Union[str, Sequence[str], None] = 's9t0u1v2w3x4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('calendar_settings', 'sub_header')


def downgrade() -> None:
    op.add_column('calendar_settings', sa.Column('sub_header', sa.String(), nullable=False, server_default='First Quarter'))
