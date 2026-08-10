"""add updated_at trigger

Revision ID: aa47e430a4a4
Revises: f2f71e98ce26
Create Date: 2026-08-09 21:17:51.968563

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "aa47e430a4a4"
down_revision: Union[str, Sequence[str], None] = "f2f71e98ce26"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
           NEW.updated_at = NOW();
           RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute("""
        CREATE TRIGGER trg_leaderboard_updated
        BEFORE UPDATE ON leaderboard
        FOR EACH ROW EXECUTE FUNCTION set_updated_timestamp();
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP TRIGGER IF EXISTS trg_leaderboard_updated ON leaderboard;
        """)
    op.execute("""
        DROP FUNCTION IF EXISTS set_updated_timestamp();
        """)
