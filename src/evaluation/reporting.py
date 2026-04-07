import csv
import json
from pathlib import Path

from src.evaluation.artifacts import (
    artifact_date,
    backtest_csv_path,
    backtest_json_path,
    backtest_markdown_path,
    backtest_seed_csv_path,
    backtest_summary_csv_path,
    history_csv_path,
    next_report_dir,
)
from src.evaluation.graphs import save_backtest_graphs


def _history_label(history: int | None) -> str:
    return str(history) if history is not None else "todo o historico anterior"


def _contest_label(value: int | None, fallback: str) -> str:
    return str(value) if value is not None else fallback


def _format_currency(value: float) -> str:
    return f"R$ {value:,.2f}"


def _rank_results(results: dict, key: str) -> list[tuple[str, float]]:
    return sorted(
        ((experiment_id, result["cost_analysis"][key] if key in result["cost_analysis"] else result["summary_geral"][key]) for experiment_id, result in results.items()),
        key=lambda item: item[1],
        reverse=True,
    )


def _aggregate_by_seed(comparison: dict) -> list[dict]:
    rows: list[dict] = []
    for seed in comparison["params"]["seeds"]:
        seed_media_values = []
        seed_max_values = []
        for result in comparison["results"].values():
            seed_result = result["seed_results"].get(seed)
            if seed_result is None:
                continue
            summary = seed_result["summary_geral"]
            seed_media_values.append(summary["media"])
            seed_max_values.append(summary["max"])

        if not seed_media_values:
            continue

        rows.append(
            {
                "seed": seed,
                "media_media": sum(seed_media_values) / len(seed_media_values),
                "melhor_max": max(seed_max_values),
            }
        )

    return rows


def _aggregate_by_bet_size(comparison: dict) -> list[dict]:
    grouped: dict[int, list[dict]] = {}
    for experiment_id, result in comparison["results"].items():
        bet_size = comparison["experiments"][experiment_id]["bet_size"]
        grouped.setdefault(bet_size, []).append(result)

    rows: list[dict] = []
    for bet_size, results in sorted(grouped.items()):
        media_values = [result["summary_geral"]["media"] for result in results]
        max_values = [result["summary_geral"]["max"] for result in results]
        media_por_real_values = [
            result["cost_analysis"]["media_por_real"]
            for result in results
        ]
        rows.append(
            {
                "bet_size": bet_size,
                "media_media": sum(media_values) / len(media_values),
                "melhor_max": max(max_values),
                "melhor_media_por_real": max(media_por_real_values),
            }
        )

    return rows


def format_backtest_report(comparison: dict) -> str:
    params = comparison["params"]
    experiments = comparison["experiments"]
    results = comparison["results"]
    inicio_value = _contest_label(params["inicio"], "primeiro disponivel")
    fim_value = _contest_label(params["fim"], "ultimo disponivel")

    media_ranking = _rank_results(results, "media")
    max_ranking = _rank_results(results, "max")
    efficiency_ranking = _rank_results(results, "media_por_real")

    lines = [
        "# Backtest Completo",
        "",
        f"- Data: {artifact_date()}",
        f"- Concursos avaliados: {inicio_value} a {fim_value}",
        f"- Tickets por concurso: {params['qtd_por_concurso']}",
        f"- Tamanhos de aposta: {', '.join(map(str, params['bet_sizes']))}",
        f"- Janela de historico: {_history_label(params['history'])}",
        f"- Seed inicial: {params['seed_start']}",
        f"- Quantidade de seeds: {params['seed_count']}",
        f"- Seeds usadas: {', '.join(map(str, params['seeds']))}",
        f"- Presets comparados: {', '.join(params['presets'])}",
        f"- Runs totais: {params['total_runs']}",
        f"- Concursos no intervalo: {params['target_draw_count']}",
        f"- Tickets estimados: {params['estimated_tickets']}",
        f"- Custo estimado da bateria: {_format_currency(params['estimated_total_cost'])}",
        "",
        "## Estimativa de Custo",
        "",
    ]

    for bet_size, cost in params["estimated_cost_by_bet_size"].items():
        lines.append(f"- {bet_size} dezenas: {_format_currency(cost)}")

    lines.extend([
        "",
        "## Graficos",
        "",
        f"![Grafico principal](backtest_{artifact_date()}.png)",
        "",
        f"![Tendencia](backtest_trend_{artifact_date()}.png)",
        "",
        f"![Delta](backtest_delta_{artifact_date()}.png)",
        "",
        f"![Seeds](backtest_seeds_{artifact_date()}.png)",
        "",
        f"![Tamanhos de aposta](backtest_bet_sizes_{artifact_date()}.png)",
        "",
        "## Ranking Geral",
        "",
        f"- Melhor media: {experiments[media_ranking[0][0]]['display_name']}",
        f"- Melhor maximo de acertos: {experiments[max_ranking[0][0]]['display_name']}",
        f"- Melhor custo-beneficio: {experiments[efficiency_ranking[0][0]]['display_name']}",
        "",
        "### Ranking por Media",
        "",
    ])

    for experiment_id, value in media_ranking:
        lines.append(f"- {experiments[experiment_id]['display_name']}: {value:.2f}")

    lines.extend(["", "### Ranking por Maximo de Acertos", ""])
    for experiment_id, value in max_ranking:
        lines.append(f"- {experiments[experiment_id]['display_name']}: {value}")

    lines.extend(["", "### Ranking por Custo-Beneficio", ""])
    for experiment_id, value in efficiency_ranking:
        lines.append(f"- {experiments[experiment_id]['display_name']}: {value:.6f}")

    lines.extend(["", "## Resumo por Seed", ""])
    for row in _aggregate_by_seed(comparison):
        lines.append(
            f"- Seed {row['seed']}: media media={row['media_media']:.2f}, melhor max={row['melhor_max']}"
        )

    lines.extend(["", "## Resumo por Tamanho de Aposta", ""])
    for row in _aggregate_by_bet_size(comparison):
        lines.append(
            f"- {row['bet_size']} dezenas: media media={row['media_media']:.2f}, "
            f"melhor max={row['melhor_max']}, melhor media por real={row['melhor_media_por_real']:.6f}"
        )

    for experiment_id, result in results.items():
        experiment = experiments[experiment_id]
        summary = result["summary_geral"]
        cost = result["cost_analysis"]
        lines.extend(
            [
                "",
                f"## {experiment['display_name']}",
                "",
                f"- Familia: {experiment['family']}",
                f"- Preset: {experiment['preset_name'] or 'n/a'}",
                f"- Tamanho da aposta: {experiment['bet_size']}",
                f"- Concursos avaliados: {result['qtd_concursos_avaliados']}",
                f"- Tickets totais: {result['qtd_tickets_total']}",
                f"- Media de acertos: {summary['media']:.2f}",
                f"- Maior numero de acertos: {summary['max']}",
                f"- Menor numero de acertos: {summary['min']}",
                f"- Custo da aposta: R$ {cost['bet_cost']:.2f}",
                f"- Custo relativo: {cost['relative_cost']:.2f}x",
                f"- Media por real: {cost['media_por_real']:.6f}",
                f"- Maximo por real: {cost['maximo_por_real']:.6f}",
                "",
                "### Configuracao",
                "",
            ]
        )
        for key, value in experiment["strategy_kwargs"].items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "### Distribuicao de Acertos", ""])
        for hits, count in summary["distribution"].items():
            lines.append(f"- {hits} acertos: {count}")
        lines.extend(["", "### Resultados por Seed", ""])
        for seed, seed_result in sorted(result["seed_results"].items()):
            seed_summary = seed_result["summary_geral"]
            lines.append(
                f"- Seed {seed}: media={seed_summary['media']:.2f}, max={seed_summary['max']}, min={seed_summary['min']}"
            )

    return "\n".join(lines)


def save_backtest_report(comparison: dict, report_dir: Path) -> Path:
    report_path = backtest_markdown_path(report_dir)
    report_path.write_text(format_backtest_report(comparison), encoding="utf-8")
    return report_path


def save_backtest_json(comparison: dict, report_dir: Path) -> Path:
    report_path = backtest_json_path(report_dir)
    report_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path


def save_backtest_csv(comparison: dict, report_dir: Path) -> Path:
    report_path = backtest_csv_path(report_dir)
    with report_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["contest", "experiment", "family", "preset", "bet_size", "total", "media", "max", "min"])
        for experiment_id, result in comparison["results"].items():
            experiment = comparison["experiments"][experiment_id]
            for contest_result in result["resultados_por_concurso"]:
                summary = contest_result["summary"]
                writer.writerow([
                    contest_result["contest"],
                    experiment["display_name"],
                    experiment["family"],
                    experiment["preset_name"] or "",
                    experiment["bet_size"],
                    summary["total"],
                    f"{summary['media']:.6f}",
                    summary["max"],
                    summary["min"],
                ])
    return report_path


def save_backtest_summary_csv(comparison: dict, report_dir: Path) -> Path:
    report_path = backtest_summary_csv_path(report_dir)
    with report_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "experiment", "family", "preset", "bet_size", "bet_cost", "relative_cost",
            "qtd_concursos_avaliados", "qtd_tickets_total", "media", "max", "min",
            "media_por_real", "maximo_por_real",
        ])
        for experiment_id, result in comparison["results"].items():
            experiment = comparison["experiments"][experiment_id]
            summary = result["summary_geral"]
            cost = result["cost_analysis"]
            writer.writerow([
                experiment["display_name"],
                experiment["family"],
                experiment["preset_name"] or "",
                experiment["bet_size"],
                f"{cost['bet_cost']:.2f}",
                f"{cost['relative_cost']:.6f}",
                result["qtd_concursos_avaliados"],
                result["qtd_tickets_total"],
                f"{summary['media']:.6f}",
                summary["max"],
                summary["min"],
                f"{cost['media_por_real']:.6f}",
                f"{cost['maximo_por_real']:.6f}",
            ])
    return report_path


def save_backtest_seed_csv(comparison: dict, report_dir: Path) -> Path:
    report_path = backtest_seed_csv_path(report_dir)
    with report_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "experiment", "family", "preset", "bet_size", "seed",
            "total", "media", "max", "min",
        ])
        for experiment_id, result in comparison["results"].items():
            experiment = comparison["experiments"][experiment_id]
            for seed, seed_result in sorted(result["seed_results"].items()):
                summary = seed_result["summary_geral"]
                writer.writerow([
                    experiment["display_name"],
                    experiment["family"],
                    experiment["preset_name"] or "",
                    experiment["bet_size"],
                    seed,
                    summary["total"],
                    f"{summary['media']:.6f}",
                    summary["max"],
                    summary["min"],
                ])
    return report_path


def append_history_csv(comparison: dict) -> Path:
    report_path = history_csv_path()
    file_exists = report_path.exists()
    with report_path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "report_date", "experiment", "family", "preset", "bet_size",
                "seed_start", "seed_count", "inicio", "fim", "history", "qtd_por_concurso",
                "bet_cost", "relative_cost", "media", "max", "min", "media_por_real", "maximo_por_real",
            ])
        for experiment_id, result in comparison["results"].items():
            experiment = comparison["experiments"][experiment_id]
            summary = result["summary_geral"]
            cost = result["cost_analysis"]
            writer.writerow([
                artifact_date(),
                experiment["display_name"],
                experiment["family"],
                experiment["preset_name"] or "",
                experiment["bet_size"],
                comparison["params"]["seed_start"],
                comparison["params"]["seed_count"],
                comparison["params"]["inicio"],
                comparison["params"]["fim"],
                comparison["params"]["history"],
                comparison["params"]["qtd_por_concurso"],
                f"{cost['bet_cost']:.2f}",
                f"{cost['relative_cost']:.6f}",
                f"{summary['media']:.6f}",
                summary["max"],
                summary["min"],
                f"{cost['media_por_real']:.6f}",
                f"{cost['maximo_por_real']:.6f}",
            ])
    return report_path


def save_backtest_artifacts_in_dir(comparison: dict, report_dir: Path) -> dict[str, Path]:
    graph_paths = save_backtest_graphs(comparison, report_dir)
    markdown_path = save_backtest_report(comparison, report_dir)
    json_path = save_backtest_json(comparison, report_dir)
    csv_path = save_backtest_csv(comparison, report_dir)
    summary_csv_path = save_backtest_summary_csv(comparison, report_dir)
    seed_csv_path = save_backtest_seed_csv(comparison, report_dir)
    history_path = append_history_csv(comparison)
    return {
        **graph_paths,
        "markdown": markdown_path,
        "json": json_path,
        "csv": csv_path,
        "summary_csv": summary_csv_path,
        "seed_csv": seed_csv_path,
        "history_csv": history_path,
    }


def save_backtest_artifacts(comparison: dict) -> dict[str, Path]:
    report_dir = next_report_dir()
    return save_backtest_artifacts_in_dir(comparison, report_dir)
