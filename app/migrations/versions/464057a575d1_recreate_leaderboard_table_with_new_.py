"""recreate leaderboard table with new metadata

Revision ID: 464057a575d1
Revises: 8722c2b5c277
Create Date: 2026-09-01 05:21:16.061413

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "464057a575d1"
down_revision: Union[str, Sequence[str], None] = "8722c2b5c277"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "leaderboard",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("external_leaderboard_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "estimated_time_per_completion_minutes", sa.Integer(), nullable=False
        ),
        sa.Column("group_size", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_leaderboard_id"),
        sa.UniqueConstraint("name"),
        sa.CheckConstraint(
            "estimated_time_per_completion_minutes > 0",
            name="ck_estimated_time_positive",
        ),
        sa.CheckConstraint("group_size > 0", "ck_group_size_positive"),
    )

    op.execute("""
        CREATE TRIGGER trg_leaderboard_updated
        BEFORE UPDATE ON leaderboard
        FOR EACH ROW EXECUTE FUNCTION set_updated_timestamp();
        """)

    op.execute("""
        INSERT INTO leaderboard (external_leaderboard_id, name, estimated_time_per_completion_minutes, group_size)
        VALUES
        ('Zenith', 'Celestial Zenith', 15, 4),
        ('TwistedXWins', 'Twisted Intruder', 5, 2),
        ('Aurora', 'Aurora', 4, 4),
        ('Hexfall', 'Hexfall' , 8, 4),
        ('SKT', 'Silver Knights Tomb (Normal)', 4, 4),
        ('SKTH', 'Silver Knights Tomb (Savage)', 15, 4),
        ('GodsporeWins', 'Godspore', 4, 4),
        ('Portal', 'Portal', 3, 4),
        ('MasqueradersRuin', 'Masqueraders Ruin', 8, 6),
        ('SKRCombatRooms', 'Silver Knight Remnants (Combat)', 4, 1),
        ('SKRPuzzleRooms', 'Silver Knight Remnants (Puzzle)', 4, 1)
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE leaderboard CASCADE")
