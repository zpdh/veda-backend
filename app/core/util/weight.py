from dataclasses import dataclass

_RANK_BOOSTS = {1: 0.06, 2: 0.04, 3: 0.02}
_WEIGHT_INDEX = 10.0


@dataclass
class WeightedEntry:
    rank: int
    playtime_minutes: int
    leaderboard_weight: float


def calculate_player_weight(entries: list[WeightedEntry]) -> float:
    raw_score = sum(
        entry.playtime_minutes * entry.leaderboard_weight * get_rank_factor(entry.rank)
        for entry in entries
    )

    playtimes = [entry.playtime_minutes for entry in entries]
    d_coeff = calculate_diversification_coeff(playtimes)

    return raw_score * d_coeff


def get_rank_factor(rank: int) -> float:
    return _RANK_BOOSTS.get(rank, 0.0) + 1


def calculate_leaderboard_weight(
    group_size: int, estimated_time_per_completion_minutes: int
) -> float:
    return (_WEIGHT_INDEX * group_size) / estimated_time_per_completion_minutes


def calculate_diversification_coeff(playtimes: list[int]) -> float:
    # https://wikipedia.org/wiki/Herfindahl%E2%80%93Hirschman_index
    n = len(playtimes)
    if n <= 1:
        return 0.7

    total_playtime = sum(playtimes)
    shares = [p / total_playtime for p in playtimes]
    hhi = sum(s**2 for s in shares)
    hhi_normalized = (hhi - 1 / n) / (1 - 1 / n)

    return 1 - 0.3 * hhi_normalized
