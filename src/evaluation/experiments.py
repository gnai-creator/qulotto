from src.app.config import build_statistical_preset
from src.evaluation.backtest import run_backtest
from src.evaluation.costs import cost_analysis


def experiment_id(family: str, bet_size: int, preset_name: str | None = None) -> str:
    if preset_name is None:
        return f"{family}_{bet_size}"
    return f"{family}_{preset_name}_{bet_size}"


def display_name(family: str, bet_size: int, preset_name: str | None = None) -> str:
    if preset_name is None:
        return f"{family.title()} {bet_size}"
    return f"{family.title()} {preset_name} {bet_size}"


def build_experiment_specs(presets: list[str], bet_sizes: list[int]) -> list[dict]:
    specs: list[dict] = []

    for bet_size in bet_sizes:
        specs.append(
            {
                "id": experiment_id("random", bet_size),
                "display_name": display_name("random", bet_size),
                "family": "random",
                "preset_name": None,
                "bet_size": bet_size,
                "strategy_name": "random",
                "strategy_kwargs": {"ticket_size": bet_size},
            }
        )

        for preset_name in presets:
            specs.append(
                {
                    "id": experiment_id("statistical", bet_size, preset_name),
                    "display_name": display_name("statistical", bet_size, preset_name),
                    "family": "statistical",
                    "preset_name": preset_name,
                    "bet_size": bet_size,
                    "strategy_name": "statistical",
                    "strategy_kwargs": build_statistical_preset(preset_name, bet_size),
                }
            )

    return specs


def build_seed_list(seed_start: int, seed_count: int) -> list[int]:
    return [seed_start + offset for offset in range(seed_count)]


def _merge_summaries(summaries: list[dict]) -> dict:
    distribution: dict[int, int] = {}
    total = 0
    weighted_sum = 0.0
    maximum = None
    minimum = None

    for summary in summaries:
        total += summary["total"]
        weighted_sum += summary["media"] * summary["total"]
        maximum = summary["max"] if maximum is None else max(maximum, summary["max"])
        minimum = summary["min"] if minimum is None else min(minimum, summary["min"])

        for hits, count in summary["distribution"].items():
            distribution[int(hits)] = distribution.get(int(hits), 0) + count

    if total == 0:
        raise ValueError("Nao foi possivel agregar sumarios vazios.")

    return {
        "total": total,
        "media": weighted_sum / total,
        "max": maximum,
        "min": minimum,
        "distribution": dict(sorted(distribution.items())),
    }


def _aggregate_seed_runs(seed_runs: dict[int, dict], spec: dict) -> dict:
    summary_geral = _merge_summaries(
        [run["summary_geral"] for run in seed_runs.values()]
    )
    contests = sorted(
        {
            contest_result["contest"]
            for run in seed_runs.values()
            for contest_result in run["resultados_por_concurso"]
        }
    )
    resultados_por_concurso: list[dict] = []

    for contest in contests:
        contest_summaries = []
        for run in seed_runs.values():
            for contest_result in run["resultados_por_concurso"]:
                if contest_result["contest"] == contest:
                    contest_summaries.append(contest_result["summary"])
                    break

        resultados_por_concurso.append(
            {
                "contest": contest,
                "summary": _merge_summaries(contest_summaries),
            }
        )

    result = {
        "strategy": spec["strategy_name"],
        "qtd_concursos_avaliados": len(resultados_por_concurso),
        "qtd_tickets_total": summary_geral["total"],
        "summary_geral": summary_geral,
        "resultados_por_concurso": resultados_por_concurso,
        "seed_results": seed_runs,
        "metadata": spec,
    }
    result["cost_analysis"] = cost_analysis(summary_geral, spec["bet_size"])
    return result


def run_experiment_specs(
    draws: list,
    specs: list[dict],
    qtd_por_concurso: int,
    history_window: int | None,
    inicio: int | None,
    fim: int | None,
    seeds: list[int],
    ticket_callback=None,
) -> dict[str, dict]:
    results: dict[str, dict] = {}

    for spec in specs:
        seed_runs: dict[int, dict] = {}
        for seed in seeds:
            seed_runs[seed] = run_backtest(
                draws=draws,
                strategy_name=spec["strategy_name"],
                qtd_por_concurso=qtd_por_concurso,
                history_window=history_window,
                inicio=inicio,
                fim=fim,
                seed=seed,
                strategy_kwargs=spec["strategy_kwargs"],
                ticket_callback=(
                    None
                    if ticket_callback is None
                    else lambda **row: ticket_callback(
                        experiment_id=spec["id"],
                        display_name=spec["display_name"],
                        family=spec["family"],
                        preset_name=spec["preset_name"],
                        bet_size=spec["bet_size"],
                        seed=seed,
                        **row,
                    )
                ),
            )
        results[spec["id"]] = _aggregate_seed_runs(seed_runs, spec)

    return results
