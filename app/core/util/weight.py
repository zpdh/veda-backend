import math
from dataclasses import dataclass

_RANK_BOOSTS = {1: 0.06, 2: 0.04, 3: 0.02}
_WEIGHT_INDEX = 15.0
_DECAY_FLOOR = 0.75
_DECAY_THRESHOLD_HOURS = 175


@dataclass
class WeightedEntry:
    rank: int
    playtime_minutes: int
    leaderboard_weight: float


def calculate_player_weight(entries: list[WeightedEntry]) -> float:
    raw_score = sum(
        _get_effective_playtime(entry.playtime_minutes)
        * entry.leaderboard_weight
        * _get_rank_factor(entry.rank)
        for entry in entries
    )

    playtimes = [entry.playtime_minutes for entry in entries]
    d_coeff = _calculate_diversification_coeff(playtimes)

    return raw_score * d_coeff


def calculate_leaderboard_weight(group_size: int) -> float:
    return _WEIGHT_INDEX * (group_size / 4) ** 0.5  # pyright: ignore[reportAny]


def _get_rank_factor(rank: int) -> float:
    return _RANK_BOOSTS.get(rank, 0.0) + 1


def _get_effective_playtime(playtime_minutes: int) -> float:
    # My approach mixes exponential decay & linear growth. Learn more:
    # https://en.wikipedia.org/wiki/Exponential_decay
    # https://en.wikipedia.org/wiki/Segmented_regression
    # https://en.wikipedia.org/wiki/Asymptote
    hours = playtime_minutes / 60.0

    return _DECAY_FLOOR * hours + (1 - _DECAY_FLOOR) * _DECAY_THRESHOLD_HOURS * (
        1 - math.exp(-hours / _DECAY_THRESHOLD_HOURS)
    )


def _calculate_diversification_coeff(playtimes: list[int]) -> float:
    # Normalized HHI.
    # https://wikipedia.org/wiki/Herfindahl%E2%80%93Hirschman_index
    n = len(playtimes)
    if n <= 1:
        return 0.7

    total_playtime = sum(playtimes)
    shares = [p / total_playtime for p in playtimes]
    hhi = sum(s**2 for s in shares)
    hhi_normalized = (hhi - 1 / n) / (1 - 1 / n)

    return 1 - 0.3 * hhi_normalized
