"""rename profiles.grid_sizes to layout_sizes

Revision ID: u1v2w3x4y5z6
Revises: t0u1v2w3x4y5
Create Date: 2026-08-26 00:00:00.000000

The s9t0u1v2w3x4 migration originally added this column as grid_sizes and
was applied to the database under that name, but the model/migration source
was later edited to rename it to layout_sizes without a rename migration
ever being written — leaving the live DB out of sync with the ORM model
(profiles.layout_sizes does not exist) and breaking every route that
queries the profiles table (save-profile, get-profile, daily-debrief).
This migration reconciles the DB to match the current model, preserving
any existing data.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'u1v2w3x4y5z6'
down_revision: Union[str, Sequence[str], None] = 't0u1v2w3x4y5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('profiles', 'grid_sizes', new_column_name='layout_sizes')


def downgrade() -> None:
    op.alter_column('profiles', 'layout_sizes', new_column_name='grid_sizes')
