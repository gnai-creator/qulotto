from pathlib import Path

from src.app.config import FULL_BET_SIZES, FULL_PRESET_NAMES
from src.data.repository import load_draws_from_csv
from src.evaluation.artifacts import next_report_dir
from src.evaluation.costs import bet_cost
from src.evaluation.experiments import (
    build_experiment_specs,
    build_seed_list,
    run_experiment_specs,
)
from src.evaluation.future import build_future_predictions, save_future_artifacts
from src.evaluation.reporting import save_backtest_artifacts_in_dir
from src.evaluation.tickets import TicketCSVWriter


def _count_target_draws(draws: list, inicio: int | None, fim: int | None) -> int:
    filtered = draws
    if inicio is not None:
        filtered = [draw for draw in filtered if draw.contest >= inicio]
    if fim is not None:
        filtered = [draw for draw in filtered if draw.contest <= fim]
    return len(filtered)


def _estimate_batch_cost(
    experiment_specs: list[dict],
    target_draw_count: int,
    qtd_por_concurso: int,
    seed_count: int,
) -> tuple[float, dict[int, float]]:
    cost_by_bet_size: dict[int, float] = {}
    for spec in experiment_specs:
        bet_size = spec["bet_size"]
        experiment_cost = (
            bet_cost(bet_size) * target_draw_count * qtd_por_concurso * seed_count
        )
        cost_by_bet_size[bet_size] = (
            cost_by_bet_size.get(bet_size, 0.0) + experiment_cost
        )

    total_cost = sum(cost_by_bet_size.values())
    return total_cost, dict(sorted(cost_by_bet_size.items()))


def _build_backtest_summary(
    draws: list,
    options: dict,
    seeds: list[int],
    experiment_specs: list[dict],
) -> dict:
    target_draw_count = _count_target_draws(
        draws,
        options["inicio"],
        options["fim"],
    )
    total_runs = len(experiment_specs) * len(seeds)
    estimated_tickets = total_runs * target_draw_count * options["qtd"]
    estimated_total_cost, estimated_cost_by_bet_size = _estimate_batch_cost(
        experiment_specs=experiment_specs,
        target_draw_count=target_draw_count,
        qtd_por_concurso=options["qtd"],
        seed_count=len(seeds),
    )
    return {
        "target_draw_count": target_draw_count,
        "total_runs": total_runs,
        "estimated_tickets": estimated_tickets,
        "estimated_total_cost": estimated_total_cost,
        "estimated_cost_by_bet_size": estimated_cost_by_bet_size,
    }


def _resolve_execution_options(options: dict) -> tuple[list, list[int], list[str], list[dict]]:
    draws = load_draws_from_csv()
    completo = bool(options.get("completo", False))
    presets = FULL_PRESET_NAMES if completo else options["presets"]
    bet_sizes = (
        [options["tamanho_aposta"]]
        if options.get("tamanho_aposta") is not None
        else (FULL_BET_SIZES if completo else options["tamanhos_aposta"])
    )
    seeds = build_seed_list(options["seed"], options["seed_count"])
    experiment_specs = build_experiment_specs(presets, bet_sizes)
    return draws, seeds, presets, experiment_specs


def preview_backtest_workflow(options: dict) -> dict:
    draws, seeds, presets, experiment_specs = _resolve_execution_options(options)
    summary = _build_backtest_summary(
        draws=draws,
        options=options,
        seeds=seeds,
        experiment_specs=experiment_specs,
    )
    return {
        "seeds": seeds,
        "presets": presets,
        "experiment_specs": experiment_specs,
        "summary": summary,
    }


def run_backtest_workflow(options: dict, progress_callback=None) -> dict:
    draws, seeds, presets, experiment_specs = _resolve_execution_options(options)
    report_dir = next_report_dir()
    ticket_writer = TicketCSVWriter(report_dir)
    summary = _build_backtest_summary(
        draws=draws,
        options=options,
        seeds=seeds,
        experiment_specs=experiment_specs,
    )

    try:
        results = run_experiment_specs(
            draws=draws,
            specs=experiment_specs,
            qtd_por_concurso=options["qtd"],
            history_window=options["history"],
            inicio=options["inicio"],
            fim=options["fim"],
            seeds=seeds,
            ticket_callback=lambda **row: ticket_writer.write(**row),
            progress_callback=progress_callback,
        )
        comparison = {
            "params": {
                "qtd_por_concurso": options["qtd"],
                "bet_sizes": sorted({spec["bet_size"] for spec in experiment_specs}),
                "inicio": options["inicio"],
                "fim": options["fim"],
                "history": options["history"],
                "seed_start": options["seed"],
                "seed_count": options["seed_count"],
                "seeds": seeds,
                "presets": presets,
                "completo": options.get("completo", False),
                **summary,
            },
            "experiments": {spec["id"]: spec for spec in experiment_specs},
            "results": results,
        }
        artifact_paths = save_backtest_artifacts_in_dir(comparison, report_dir)
    finally:
        ticket_writer.close()

    return {
        "mode": "backtest",
        "report_dir": report_dir,
        "artifact_paths": {
            key: str(value) for key, value in artifact_paths.items()
        },
        "tickets_csv": str(ticket_writer.path),
        "summary": summary,
    }


def run_future_workflow(options: dict) -> dict:
    draws, seeds, _, experiment_specs = _resolve_execution_options(options)
    report_dir = next_report_dir()
    prediction_bundle = build_future_predictions(
        draws=draws,
        specs=experiment_specs,
        qtd_por_experimento=options["qtd"],
        history_window=options["history"],
        seeds=seeds,
    )
    artifact_paths = save_future_artifacts(prediction_bundle, report_dir)
    return {
        "mode": "future",
        "report_dir": report_dir,
        "artifact_paths": {
            key: str(value) for key, value in artifact_paths.items()
        },
        "summary": prediction_bundle["params"],
    }
