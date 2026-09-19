import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class WeightConfig:
    weight_index: float = 15.0
    decay_floor: float = 0.75
    diversification_max_penalty: float = 0.3
    decay_threshold_hours: int = 175
    rank_boosts: dict[int, float] = field(
        default_factory=lambda: {1: 0.06, 2: 0.04, 3: 0.02}
    )


@dataclass(frozen=True)
class EntryRow:
    rank: int
    value: int
    estimated_playtime_per_completion_minutes: int
    group_size: int


@dataclass(frozen=True)
class WeightedEntry:
    rank: int
    playtime_minutes: int
    leaderboard_weight: float


_WEIGHT_CONFIG = WeightConfig()


def calculate_weight_for_rows(entries: list[EntryRow]) -> float:
    return _calculate_player_weight(_build_weighted_entries(entries))


def _build_weighted_entries(entries: list[EntryRow]) -> list[WeightedEntry]:
    return [
        WeightedEntry(
            rank=e.rank,
            playtime_minutes=e.value * e.estimated_playtime_per_completion_minutes,
            leaderboard_weight=_calculate_leaderboard_weight(e.group_size),
        )
        for e in entries
    ]


def _calculate_player_weight(entries: list[WeightedEntry]) -> float:
    raw_score = sum(
        _calculate_effective_playtime(entry.playtime_minutes)
        * entry.leaderboard_weight
        * _calculate_rank_factor(entry.rank)
        for entry in entries
    )

    playtimes = [entry.playtime_minutes for entry in entries]
    diversification_coefficient = _calculate_diversification_coefficient(playtimes)

    return raw_score * diversification_coefficient


def _calculate_leaderboard_weight(group_size: int) -> float:
    return _WEIGHT_CONFIG.weight_index * math.sqrt(group_size / 4)


def _calculate_rank_factor(rank: int) -> float:
    return _WEIGHT_CONFIG.rank_boosts.get(rank, 0.0) + 1


def _calculate_effective_playtime(playtime_minutes: int) -> float:
    # My approach mixes exponential decay & linear growth. Learn more:
    # https://en.wikipedia.org/wiki/Exponential_decay
    # https://en.wikipedia.org/wiki/Segmented_regression
    # https://en.wikipedia.org/wiki/Asymptote
    hours = playtime_minutes / 60.0
    decay_floor = _WEIGHT_CONFIG.decay_floor
    decay_threshold = _WEIGHT_CONFIG.decay_threshold_hours

    linear_comp = decay_floor * hours
    exp_comp = (
        (1.0 - decay_floor)
        * decay_threshold
        * (1.0 - math.exp(-hours / decay_threshold))
    )

    return linear_comp + exp_comp


def _calculate_diversification_coefficient(playtimes: list[int]) -> float:
    # Normalized HHI.
    # https://wikipedia.org/wiki/Herfindahl%E2%80%93Hirschman_index
    max_penalty = _WEIGHT_CONFIG.diversification_max_penalty

    playtimes_len = len(playtimes)
    if playtimes_len <= 1:
        return 1.0 - max_penalty

    total_playtime = sum(playtimes)
    shares = [p / total_playtime for p in playtimes]

    hhi = sum(share**2 for share in shares)
    hhi_normalized = (hhi - 1 / playtimes_len) / (1 - 1 / playtimes_len)

    return 1.0 - max_penalty * hhi_normalized
