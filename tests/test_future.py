from src.core.models import Draw
from src.evaluation.experiments import build_experiment_specs
from src.evaluation.future import build_future_predictions


def test_build_future_predictions_targets_next_contest() -> None:
    draws = [
        Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        Draw(contest=3, numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ]
    specs = build_experiment_specs(presets=["balanced"], bet_sizes=[15])

    result = build_future_predictions(
        draws=draws,
        specs=specs,
        qtd_por_experimento=2,
        history_window=2,
        seeds=[42],
    )

    assert result["params"]["future_contest"] == 4
    assert result["params"]["based_on_latest_contest"] == 3
    assert len(result["predictions"]) == len(specs) * 2
