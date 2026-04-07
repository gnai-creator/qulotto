import random

from src.core.scoring import count_hits
from src.core.models import Draw
from src.evaluation.metrics import sumario_de_acertos
from src.strategies.intentionality_vector import IntentionalityVectorStrategy
from src.strategies.quantum_inspired import QuantumInspiredStrategy
from src.strategies.random_baseline import RandomBaselineStrategy
from src.strategies.statistical_baseline import StatisticalBaselineStrategy


def build_strategy(
    strategy_name: str,
    history_draws: list[Draw],
    rng: random.Random | None = None,
    strategy_kwargs: dict | None = None,
):
    strategy_kwargs = strategy_kwargs or {}

    if strategy_name == "random":
        return RandomBaselineStrategy(rng=rng, **strategy_kwargs)
    
    if strategy_name == "statistical":
        return StatisticalBaselineStrategy(
            history_draws=history_draws,
            rng=rng,
            **strategy_kwargs,
        )

    if strategy_name == "intentionality_vector":
        return IntentionalityVectorStrategy(
            history_draws=history_draws,
            rng=rng,
            **strategy_kwargs,
        )

    if strategy_name == "quantum_inspired":
        return QuantumInspiredStrategy(
            history_draws=history_draws,
            rng=rng,
            **strategy_kwargs,
        )
    
    raise ValueError(f"Estrategia Desconhecida: {strategy_name}")

def run_backtest(
    draws: list[Draw],
    strategy_name: str,
    qtd_por_concurso: int,
    history_window: int | None = None,
    inicio: int | None = None,
    fim: int | None = None,
    seed: int | None = None,
    strategy_kwargs: dict | None = None,
    ticket_callback=None,
) -> dict:
    if not draws:
        raise ValueError("A lista de draws no pode estar vazia")

    all_draws = sorted(draws, key=lambda draw: draw.contest)
    draws_avaliados = all_draws

    if inicio is not None:
        draws_avaliados = [draw for draw in draws_avaliados if draw.contest >= inicio]

    if fim is not None:
        draws_avaliados = [draw for draw in draws_avaliados if draw.contest <= fim]

    resultados_por_concurso: list[dict] = []
    todos_os_acertos: list[int] = []

    for target_draw in draws_avaliados:
        history_draws = [
            draw for draw in all_draws if draw.contest < target_draw.contest
        ]

        if history_window is not None:
            history_draws = history_draws[-history_window:]

        if strategy_name in {
            "statistical",
            "intentionality_vector",
            "quantum_inspired",
        } and not history_draws:
            continue

        contest_seed = None if seed is None else seed + target_draw.contest
        rng = random.Random(contest_seed)
        strategy = build_strategy(
            strategy_name=strategy_name,
            history_draws=history_draws,
            rng=rng,
            strategy_kwargs=strategy_kwargs,
        )
        tickets = strategy.generate_tickets(qtd=qtd_por_concurso)
        hits_list: list[int] = []
        for ticket_index, ticket in enumerate(tickets, start=1):
            hits = count_hits(ticket=ticket, draw=target_draw)
            hits_list.append(hits)
            if ticket_callback is not None:
                ticket_callback(
                    contest=target_draw.contest,
                    ticket_index=ticket_index,
                    numbers=ticket.numbers,
                    hits=hits,
                )

        resultados_por_concurso.append(
            {
                "contest": target_draw.contest,
                "summary": sumario_de_acertos(hits_list=hits_list),
            }
        )

        todos_os_acertos.extend(hits_list)

    if not resultados_por_concurso:
        raise ValueError("Nenhum concurso foi avaliado no backtest.")

    return {
        "strategy": strategy_name,
        "qtd_concursos_avaliados": len(resultados_por_concurso),
        "qtd_tickets_total": len(todos_os_acertos),
        "summary_geral": sumario_de_acertos(todos_os_acertos),
        "resultados_por_concurso": resultados_por_concurso,
    }
