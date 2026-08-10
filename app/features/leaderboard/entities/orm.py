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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.orm_config import Base


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
    snapshots: Mapped[list["LeaderboardSnapshot"]] = relationship(
        back_populates="leaderboard"
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
    leaderboard: Mapped["Leaderboard"] = relationship(back_populates="snapshots")
    entries: Mapped[list["LeaderboardEntry"]] = relationship(back_populates="snapshot")


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
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped["LeaderboardSnapshot"] = relationship(back_populates="entries")
