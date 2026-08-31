import pytest
from pydantic import ValidationError

from app.features.leaderboard.dto.request import (
    CreateSnapshotRequest,
    EntryIn,
    LeaderboardSnapshotIn,
)
from app.features.leaderboard.errors.errors import LeaderboardError, LeaderboardErrors


class TestEntryInDTO:
    def test_valid_entry(self):
        entry = EntryIn(rank=1, playerName="Alice_123", value=100)
        assert entry.rank == 1
        assert entry.player_name == "Alice_123"
        assert entry.value == 100

    def test_valid_entry_by_field_name(self):
        entry = EntryIn(rank=2, playerName="Bob", value=0)
        assert entry.player_name == "Bob"
        assert entry.value == 0

    def test_rank_must_be_greater_than_zero(self):
        with pytest.raises(ValidationError):
            _ = EntryIn(rank=0, playerName="Alice", value=10)

        with pytest.raises(ValidationError):
            _ = EntryIn(rank=-1, playerName="Alice", value=10)

    def test_value_must_be_non_negative(self):
        with pytest.raises(ValidationError):
            _ = EntryIn(rank=1, playerName="Alice", value=-1)

    def test_player_name_empty_raises_validation_error(self):
        with pytest.raises(ValidationError):
            _ = EntryIn(rank=1, playerName="", value=10)

    def test_player_name_length_boundary(self):
        valid_16 = EntryIn(rank=1, playerName="A" * 16, value=10)
        assert len(valid_16.player_name) == 16

        with pytest.raises(ValidationError):
            _ = EntryIn(rank=1, playerName="A" * 17, value=10)


class TestLeaderboardSnapshotInDTO:
    def test_valid_snapshot_in(self):
        snap = LeaderboardSnapshotIn(
            leaderboardName="Global Rankings",
            entries=[
                EntryIn(rank=1, playerName="Alice", value=100),
                EntryIn(rank=2, playerName="Bob", value=80),
            ],
        )
        assert snap.leaderboard_name == "Global Rankings"
        assert len(snap.entries) == 2

    def test_empty_entries_raises_validation_error(self):
        with pytest.raises(ValidationError):
            _ = LeaderboardSnapshotIn(
                leaderboardName="Global Rankings",
                entries=[],
            )

    def test_empty_leaderboard_name_raises_validation_error(self):
        with pytest.raises(ValidationError):
            _ = LeaderboardSnapshotIn(
                leaderboardName="",
                entries=[EntryIn(rank=1, playerName="Alice", value=100)],
            )

    def test_duplicate_ranks_raises_custom_leaderboard_error(self):
        with pytest.raises(LeaderboardError) as exc_info:
            _ = LeaderboardSnapshotIn(
                leaderboardName="Global Rankings",
                entries=[
                    EntryIn(rank=1, playerName="Alice", value=100),
                    EntryIn(rank=1, playerName="Bob", value=80),
                ],
            )
        assert (
            exc_info.value.error_code
            == LeaderboardErrors.DUPLICATE_RANK.value.error_code
        )
        assert exc_info.value.status_code == 400


class TestCreateSnapshotRequestDTO:
    def test_valid_create_snapshot_request(self):
        req = CreateSnapshotRequest(
            snapshots=[
                LeaderboardSnapshotIn(
                    leaderboardName="Global",
                    entries=[EntryIn(rank=1, playerName="Alice", value=10)],
                )
            ]
        )
        assert len(req.snapshots) == 1
        assert req.snapshots[0].leaderboard_name == "Global"

    def test_empty_snapshots_list_raises_validation_error(self):
        with pytest.raises(ValidationError):
            _ = CreateSnapshotRequest(snapshots=[])
