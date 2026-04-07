import json
import random
from pathlib import Path

from src.evaluation.artifacts import (
    artifact_date,
    future_csv_path,
    future_json_path,
    future_markdown_path,
)
from src.evaluation.backtest import build_strategy


def build_future_predictions(
    draws: list,
    specs: list[dict],
    qtd_por_experimento: int,
    history_window: int | None,
    seeds: list[int],
) -> dict:
    if not draws:
        raise ValueError("Nao ha draws processados para gerar palpites futuros.")

    all_draws = sorted(draws, key=lambda draw: draw.contest)
    latest_draw = all_draws[-1]
    history_draws = all_draws if history_window is None else all_draws[-history_window:]
    future_contest = latest_draw.contest + 1
    predictions: list[dict] = []

    for spec in specs:
        for seed in seeds:
            rng = random.Random(seed + future_contest)
            strategy = build_strategy(
                strategy_name=spec["strategy_name"],
                history_draws=history_draws,
                rng=rng,
                strategy_kwargs=spec["strategy_kwargs"],
            )
            tickets = strategy.generate_tickets(qtd=qtd_por_experimento)
            for ticket_index, ticket in enumerate(tickets, start=1):
                predictions.append(
                    {
                        "future_contest": future_contest,
                        "based_on_latest_contest": latest_draw.contest,
                        "experiment_id": spec["id"],
                        "display_name": spec["display_name"],
                        "family": spec["family"],
                        "preset_name": spec["preset_name"],
                        "bet_size": spec["bet_size"],
                        "seed": seed,
                        "ticket_index": ticket_index,
                        "numbers": ticket.numbers,
                    }
                )

    return {
        "params": {
            "qtd_por_experimento": qtd_por_experimento,
            "history": history_window,
            "seed_count": len(seeds),
            "seeds": seeds,
            "future_contest": future_contest,
            "based_on_latest_contest": latest_draw.contest,
        },
        "experiments": {spec["id"]: spec for spec in specs},
        "predictions": predictions,
    }


def _format_future_report(prediction_bundle: dict) -> str:
    params = prediction_bundle["params"]
    lines = [
        "# Palpites Futuros",
        "",
        f"- Data: {artifact_date()}",
        f"- Concurso futuro alvo: {params['future_contest']}",
        f"- Ultimo concurso disponivel no historico: {params['based_on_latest_contest']}",
        f"- Tickets por experimento: {params['qtd_por_experimento']}",
        f"- Janela de historico: {params['history'] if params['history'] is not None else 'todo o historico'}",
        f"- Seeds usadas: {', '.join(map(str, params['seeds']))}",
        "",
    ]

    by_experiment: dict[str, list[dict]] = {}
    for row in prediction_bundle["predictions"]:
        by_experiment.setdefault(row["experiment_id"], []).append(row)

    for experiment_id, rows in by_experiment.items():
        experiment = prediction_bundle["experiments"][experiment_id]
        lines.extend(
            [
                f"## {experiment['display_name']}",
                "",
                f"- Familia: {experiment['family']}",
                f"- Tamanho da aposta: {experiment['bet_size']}",
                f"- Preset: {experiment['preset_name'] or 'n/a'}",
                "",
            ]
        )
        for row in rows:
            lines.append(
                f"- Seed {row['seed']} | Ticket {row['ticket_index']}: {row['numbers']}"
            )
        lines.append("")

    return "\n".join(lines)


def save_future_artifacts(prediction_bundle: dict, report_dir: Path) -> dict[str, Path]:
    markdown_path = future_markdown_path(report_dir)
    json_path = future_json_path(report_dir)
    csv_path = future_csv_path(report_dir)

    markdown_path.write_text(
        _format_future_report(prediction_bundle),
        encoding="utf-8",
    )
    json_path.write_text(
        json.dumps(prediction_bundle, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with csv_path.open("w", encoding="utf-8") as file:
        file.write(
            "future_contest,based_on_latest_contest,experiment_id,display_name,"
            "family,preset_name,bet_size,seed,ticket_index,numbers\n"
        )
        for row in prediction_bundle["predictions"]:
            file.write(
                f"{row['future_contest']},{row['based_on_latest_contest']},"
                f"{row['experiment_id']},{row['display_name']},{row['family']},"
                f"{row['preset_name'] or ''},{row['bet_size']},{row['seed']},"
                f"{row['ticket_index']},\"{','.join(map(str, row['numbers']))}\"\n"
            )

    return {
        "markdown": markdown_path,
        "json": json_path,
        "csv": csv_path,
    }
