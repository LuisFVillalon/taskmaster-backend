"""merge_calendar_and_habit_logs

Revision ID: b5c18f2ef6ef
Revises: 339cb0fc9eb6, 3c4d5e6f7a8b
Create Date: 2026-06-22 15:27:23.370919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5c18f2ef6ef'
down_revision: Union[str, Sequence[str], None] = ('339cb0fc9eb6', '3c4d5e6f7a8b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
