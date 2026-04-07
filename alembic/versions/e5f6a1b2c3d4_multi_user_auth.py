"""Multi-user auth: UUID user_id, per-user tags, per-user calendar_settings

Revision ID: e5f6a1b2c3d4
Revises: d4e5f6a1b2c3
Create Date: 2026-03-29 00:00:00.000000

What this migration does
────────────────────────
1. tasks.user_id       Integer (nullable) → VARCHAR(36) (nullable, UUID from Supabase Auth)
2. notes.user_id       Integer (nullable) → VARCHAR(36) (nullable, UUID from Supabase Auth)
3. tags                Add user_id VARCHAR(36) nullable
                       Drop global UNIQUE constraint on tags.name
                       Add UNIQUE(name, user_id) so each user can have their own "homework" tag
4. calendar_settings   Add user_id VARCHAR(36) nullable
                       Add UNIQUE(user_id) so each user gets one settings row
5. Indexes             Add ix_tasks_user_id, ix_notes_user_id for fast per-user queries

NOTE on existing data
─────────────────────
All existing rows will have user_id = NULL after the upgrade. On first sign-up the
frontend calls POST /claim-data which sets user_id on all NULL rows to the new user's UUID.
The NOT NULL constraint is intentionally deferred until after data is claimed.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'e5f6a1b2c3d4'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a1b2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. tasks.user_id: Integer → VARCHAR(36) ───────────────────────────────
    # Drop the old integer column and add the new UUID column.
    # We cannot ALTER TYPE directly in PostgreSQL without casting, so drop+add
    # is the cleanest approach for a column that has no FK constraints yet.
    op.drop_column('tasks', 'user_id')
    op.add_column('tasks', sa.Column('user_id', sa.String(36), nullable=True))
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])

    # ── 2. notes.user_id: Integer → VARCHAR(36) ───────────────────────────────
    op.drop_column('notes', 'user_id')
    op.add_column('notes', sa.Column('user_id', sa.String(36), nullable=True))
    op.create_index('ix_notes_user_id', 'notes', ['user_id'])

    # ── 3. tags: add user_id, replace global unique with per-user unique ──────
    op.add_column('tags', sa.Column('user_id', sa.String(36), nullable=True))
    op.create_index('ix_tags_user_id', 'tags', ['user_id'])

    # Drop the old global unique constraint on tags.name.
    # Constraint names vary across Postgres versions; use batch_alter_table
    # with naming convention fallback via execute() for reliability.
    # The standard SQLAlchemy-generated name is 'uq_tags_name' or just the
    # column name; Supabase/pg may have named it differently, so we use
    # IF EXISTS to be safe.
    op.execute("ALTER TABLE tags DROP CONSTRAINT IF EXISTS tags_name_key")
    op.execute("ALTER TABLE tags DROP CONSTRAINT IF EXISTS uq_tags_name")

    # New compound unique: (name, user_id) — NULL == NULL is FALSE in Postgres
    # so two NULL user_ids are treated as distinct, which is fine for legacy rows.
    op.create_unique_constraint('uq_tags_name_user_id', 'tags', ['name', 'user_id'])

    # ── 4. calendar_settings: add user_id, one-row-per-user ───────────────────
    op.add_column(
        'calendar_settings',
        sa.Column('user_id', sa.String(36), nullable=True),
    )
    op.create_index('ix_calendar_settings_user_id', 'calendar_settings', ['user_id'])
    op.create_unique_constraint('uq_calendar_settings_user_id', 'calendar_settings', ['user_id'])


def downgrade() -> None:
    # ── 4. calendar_settings ──────────────────────────────────────────────────
    op.drop_constraint('uq_calendar_settings_user_id', 'calendar_settings', type_='unique')
    op.drop_index('ix_calendar_settings_user_id', table_name='calendar_settings')
    op.drop_column('calendar_settings', 'user_id')

    # ── 3. tags ───────────────────────────────────────────────────────────────
    op.drop_constraint('uq_tags_name_user_id', 'tags', type_='unique')
    op.drop_index('ix_tags_user_id', table_name='tags')
    op.drop_column('tags', 'user_id')
    op.create_unique_constraint('tags_name_key', 'tags', ['name'])

    # ── 2. notes ──────────────────────────────────────────────────────────────
    op.drop_index('ix_notes_user_id', table_name='notes')
    op.drop_column('notes', 'user_id')
    op.add_column('notes', sa.Column('user_id', sa.Integer(), nullable=True))

    # ── 1. tasks ──────────────────────────────────────────────────────────────
    op.drop_index('ix_tasks_user_id', table_name='tasks')
    op.drop_column('tasks', 'user_id')
    op.add_column('tasks', sa.Column('user_id', sa.Integer(), nullable=True))
