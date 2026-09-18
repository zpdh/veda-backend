"""add player weight and index

Revision ID: 3b975d77fcbb
Revises: 68fcaf4a3a38
Create Date: 2026-09-18 13:53:34.823200

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3b975d77fcbb"
down_revision: Union[str, Sequence[str], None] = "68fcaf4a3a38"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "player", sa.Column("weight", sa.Float(), nullable=False, server_default="0")
    )
    op.create_index("idx_player_weight", "player", ["weight"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_player_weight", "player")
    op.drop_column("player", "weight")
