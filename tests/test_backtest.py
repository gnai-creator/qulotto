from src.core.models import Draw
from src.evaluation.backtest import run_backtest


def test_run_backtest_is_reproducible_with_seed() -> None:
    draws = [
        Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        Draw(contest=3, numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
        Draw(contest=4, numbers=[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]),
    ]

    result_a = run_backtest(
        draws=draws,
        strategy_name="random",
        qtd_por_concurso=5,
        inicio=2,
        fim=4,
        seed=99,
    )
    result_b = run_backtest(
        draws=draws,
        strategy_name="random",
        qtd_por_concurso=5,
        inicio=2,
        fim=4,
        seed=99,
    )

    assert result_a == result_b
    assert result_a["qtd_concursos_avaliados"] == 3
    assert result_a["qtd_tickets_total"] == 15


def test_statistical_backtest_uses_prior_history_only() -> None:
    draws = [
        Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        Draw(contest=3, numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ]

    result = run_backtest(
        draws=draws,
        strategy_name="statistical",
        qtd_por_concurso=2,
        inicio=1,
        fim=3,
        history_window=1,
        seed=7,
    )

    assert result["qtd_concursos_avaliados"] == 2
    assert [item["contest"] for item in result["resultados_por_concurso"]] == [2, 3]


def test_intentionality_vector_backtest_runs_with_prior_history() -> None:
    draws = [
        Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        Draw(contest=3, numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ]

    result = run_backtest(
        draws=draws,
        strategy_name="intentionality_vector",
        qtd_por_concurso=2,
        inicio=1,
        fim=3,
        history_window=1,
        seed=7,
        strategy_kwargs={"ticket_size": 16},
    )

    assert result["qtd_concursos_avaliados"] == 2
    assert [item["contest"] for item in result["resultados_por_concurso"]] == [2, 3]


def test_quantum_inspired_backtest_runs_with_prior_history() -> None:
    draws = [
        Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        Draw(contest=3, numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ]

    result = run_backtest(
        draws=draws,
        strategy_name="quantum_inspired",
        qtd_por_concurso=2,
        inicio=1,
        fim=3,
        history_window=1,
        seed=7,
        strategy_kwargs={"ticket_size": 16},
    )

    assert result["qtd_concursos_avaliados"] == 2
    assert [item["contest"] for item in result["resultados_por_concurso"]] == [2, 3]
