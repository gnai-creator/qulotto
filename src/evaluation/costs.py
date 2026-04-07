from src.app.config import LOTOFACIL_BET_COSTS


MIN_BET_COST = LOTOFACIL_BET_COSTS[15]


def bet_cost(bet_size: int) -> float:
    if bet_size not in LOTOFACIL_BET_COSTS:
        raise ValueError(f"Tamanho de aposta invalido: {bet_size}")
    return LOTOFACIL_BET_COSTS[bet_size]


def relative_bet_cost(bet_size: int) -> float:
    return bet_cost(bet_size) / MIN_BET_COST


def cost_analysis(summary: dict, bet_size: int) -> dict[str, float]:
    cost = bet_cost(bet_size)
    return {
        "bet_cost": cost,
        "relative_cost": relative_bet_cost(bet_size),
        "media_por_real": summary["media"] / cost,
        "maximo_por_real": summary["max"] / cost,
    }
