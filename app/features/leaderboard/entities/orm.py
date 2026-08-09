from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Leaderboard(Base):
    __tablename__ = "leaderboard"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class LeaderboardSnapshot(Base):
    __tablename__ = "leaderboard_snapshot"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    leaderboard_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("leaderboard.id", ondelete="CASCADE"), nullable=False
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard_entry"
    __table_args__ = (
        UniqueConstraint("snapshot_id", "rank"),
        CheckConstraint("rank > 0"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("leaderboard_snapshot.id", ondelete="CASCADE"),
        nullable=False,
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    player_name: Mapped[str] = mapped_column(Text, nullable=False)
