"""create player and snapshot indices)


Revision ID: 68fcaf4a3a38
Revises: 464057a575d1
Create Date: 2026-09-15 13:39:59.141073

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "68fcaf4a3a38"
down_revision: Union[str, Sequence[str], None] = "464057a575d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "idx_leaderboard_entry_player_name_lower",
        "leaderboard_entry",
        [sa.text("lower(player_name)")],
    )

    op.create_index(
        "idx_leaderboard_snapshot_leaderboard_id_latest",
        "leaderboard_snapshot",
        ["leaderboard_id", sa.text("fetched_at DESC")],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "idx_leaderboard_entry_player_name_lower",
        table_name="leaderboard_entry",
    )
    op.drop_index(
        "idx_leaderboard_snapshot_leaderboard_id_latest",
        "leaderboard_snapshot",
    )
