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
    downgrade()  ############################################## REMOVE THIS AFTER DEPLOY ##############################################
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
        ('Zenith Clears', 'Celestial Zenith', 15, 4),
        ('Twisted lxxxxxxx Wins', 'Twisted Intruder', 5, 2),
        ('Aurora Defeats (Caches Claimed)', 'Aurora', 4, 4),
        ('Hexfall - Hycenea Defeats', 'Hexfall' , 8, 4),
        ('SKT Savage Mode Clears', 'Silver Knights Tomb', 8, 4),
        ('Godspore Clears', 'Godspore', 4, 4)
        ('Portal', 'Portal', 2, 4),
        ('MasqueradersRuin', 'Masqueraders Ruin', 7, 6),
        ('Combat Remnants Looted', 'Silver Knight Remnants (Combat)', 6, 1),
        ('Puzzle Remnants Looted', 'Silver Knight Remnants (Puzzle)', 8, 1)
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE leaderboard CASCADE")
