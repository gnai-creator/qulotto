from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.evaluation.artifacts import (
    backtest_bet_size_chart_path,
    backtest_chart_path,
    backtest_delta_chart_path,
    backtest_seed_chart_path,
    backtest_trend_chart_path,
)


def _experiment_labels(comparison: dict) -> tuple[list[str], list[str]]:
    experiment_ids = list(comparison["results"].keys())
    labels = [
        comparison["experiments"][experiment_id]["display_name"]
        for experiment_id in experiment_ids
    ]
    return experiment_ids, labels


def _experiment_colors(experiment_ids: list[str]) -> dict[str, tuple]:
    colors = plt.get_cmap("tab10").colors
    return {
        experiment_id: colors[index % len(colors)]
        for index, experiment_id in enumerate(experiment_ids)
    }


def _group_results_by_bet_size(comparison: dict) -> dict[int, list[tuple[str, dict]]]:
    grouped: dict[int, list[tuple[str, dict]]] = {}
    for experiment_id, result in comparison["results"].items():
        bet_size = comparison["experiments"][experiment_id]["bet_size"]
        grouped.setdefault(bet_size, []).append((experiment_id, result))
    return dict(sorted(grouped.items()))


def save_backtest_chart(comparison: dict, report_dir: Path) -> Path:
    report_path = backtest_chart_path(report_dir)
    experiment_ids, labels = _experiment_labels(comparison)
    summaries = {
        experiment_id: comparison["results"][experiment_id]["summary_geral"]
        for experiment_id in experiment_ids
    }
    medias = [summaries[experiment_id]["media"] for experiment_id in experiment_ids]
    colors_by_id = _experiment_colors(experiment_ids)
    experiment_colors = [colors_by_id[experiment_id] for experiment_id in experiment_ids]
    positions = list(range(len(experiment_ids)))

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    axes[0].bar(positions, medias, color=experiment_colors)
    axes[0].set_title("Media de Acertos")
    axes[0].set_ylabel("Acertos")
    axes[0].set_ylim(0, max(medias) + 1)
    axes[0].set_xticks(positions)
    axes[0].set_xticklabels([str(index + 1) for index in positions])

    for index, value in enumerate(medias):
        axes[0].text(index, value + 0.05, f"{value:.2f}", ha="center")

    all_hits = sorted(
        {
            hit
            for summary in summaries.values()
            for hit in summary["distribution"].keys()
        }
    )
    for index, experiment_id in enumerate(experiment_ids):
        counts = [
            summaries[experiment_id]["distribution"].get(hit, 0)
            for hit in all_hits
        ]
        axes[1].plot(
            all_hits,
            counts,
            marker="o",
            label=labels[index],
            color=experiment_colors[index],
        )

    axes[1].set_title("Distribuicao de Acertos")
    axes[1].set_xlabel("Acertos")
    axes[1].set_ylabel("Quantidade de tickets")
    axes[1].set_xticks(all_hits)
    axes[1].legend()

    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, color=experiment_colors[index])
        for index in positions
    ]
    fig.legend(
        legend_handles,
        labels,
        loc="lower left",
        bbox_to_anchor=(0.02, 0.02),
        frameon=True,
        title="Experimentos",
    )
    fig.suptitle("Comparacao de Experimentos")
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.savefig(report_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return report_path


def save_backtest_trend_chart(comparison: dict, report_dir: Path) -> Path:
    report_path = backtest_trend_chart_path(report_dir)
    experiment_ids, labels = _experiment_labels(comparison)
    colors_by_id = _experiment_colors(experiment_ids)

    fig, ax = plt.subplots(figsize=(14, 6))
    for index, experiment_id in enumerate(experiment_ids):
        result = comparison["results"][experiment_id]
        contests = [item["contest"] for item in result["resultados_por_concurso"]]
        medias = [item["summary"]["media"] for item in result["resultados_por_concurso"]]
        ax.plot(contests, medias, label=labels[index], color=colors_by_id[experiment_id])

    ax.set_title("Media de Acertos por Concurso")
    ax.set_xlabel("Concurso")
    ax.set_ylabel("Media de Acertos")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(report_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return report_path


def save_backtest_delta_chart(comparison: dict, report_dir: Path) -> Path:
    report_path = backtest_delta_chart_path(report_dir)
    experiment_ids, _ = _experiment_labels(comparison)
    colors_by_id = _experiment_colors(experiment_ids)
    baselines_by_bet_size = {}

    for experiment_id, result in comparison["results"].items():
        experiment = comparison["experiments"][experiment_id]
        if experiment["family"] != "random":
            continue
        baselines_by_bet_size[experiment["bet_size"]] = {
            item["contest"]: item["summary"]["media"]
            for item in result["resultados_por_concurso"]
        }

    fig, ax = plt.subplots(figsize=(14, 6))
    plotted = 0
    for experiment_id, result in comparison["results"].items():
        experiment = comparison["experiments"][experiment_id]
        if experiment["family"] == "random":
            continue
        baseline = baselines_by_bet_size[experiment["bet_size"]]
        strategy_by_contest = {
            item["contest"]: item["summary"]["media"]
            for item in result["resultados_por_concurso"]
        }
        contests = sorted(set(baseline) & set(strategy_by_contest))
        deltas = [strategy_by_contest[c] - baseline[c] for c in contests]
        ax.plot(
            contests,
            deltas,
            marker="o",
            label=f"{experiment['display_name']} - Random {experiment['bet_size']}",
            color=colors_by_id[experiment_id],
        )
        plotted += 1

    ax.axhline(0, color="black", linewidth=1)
    ax.set_title("Diferenca de Media por Concurso")
    ax.set_xlabel("Concurso")
    ax.set_ylabel("Experimento - Random")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(report_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return report_path


def save_backtest_seed_chart(comparison: dict, report_dir: Path) -> Path:
    report_path = backtest_seed_chart_path(report_dir)
    experiment_ids, labels = _experiment_labels(comparison)
    colors_by_id = _experiment_colors(experiment_ids)
    seeds = comparison["params"]["seeds"]

    fig, ax = plt.subplots(figsize=(14, 6))
    for index, experiment_id in enumerate(experiment_ids):
        result = comparison["results"][experiment_id]
        medias = [
            result["seed_results"][seed]["summary_geral"]["media"]
            for seed in seeds
            if seed in result["seed_results"]
        ]
        ax.plot(
            seeds[: len(medias)],
            medias,
            marker="o",
            label=labels[index],
            color=colors_by_id[experiment_id],
        )

    ax.set_title("Media de Acertos por Seed")
    ax.set_xlabel("Seed")
    ax.set_ylabel("Media de Acertos")
    ax.set_xticks(seeds)
    ax.grid(alpha=0.3)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(report_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return report_path


def save_backtest_bet_size_chart(comparison: dict, report_dir: Path) -> Path:
    report_path = backtest_bet_size_chart_path(report_dir)
    grouped = _group_results_by_bet_size(comparison)
    bet_sizes = list(grouped.keys())
    experiment_ids, _ = _experiment_labels(comparison)
    colors_by_id = _experiment_colors(experiment_ids)

    fig, axes = plt.subplots(
        len(bet_sizes),
        1,
        figsize=(14, max(5, len(bet_sizes) * 3.6)),
        squeeze=False,
    )

    for row_index, bet_size in enumerate(bet_sizes):
        ax = axes[row_index][0]
        items = grouped[bet_size]
        labels = [comparison["experiments"][experiment_id]["display_name"] for experiment_id, _ in items]
        medias = [result["summary_geral"]["media"] for _, result in items]
        positions = list(range(len(items)))
        bar_colors = [colors_by_id[experiment_id] for experiment_id, _ in items]

        ax.bar(positions, medias, color=bar_colors)
        ax.set_title(f"Media de Acertos para Apostas com {bet_size} dezenas")
        ax.set_ylabel("Media")
        ax.set_xticks(positions)
        ax.set_xticklabels([str(index + 1) for index in positions])
        ax.set_ylim(0, max(medias) + 1)

        for index, value in enumerate(medias):
            ax.text(index, value + 0.03, f"{value:.2f}", ha="center", fontsize=8)

        legend_handles = [
            plt.Rectangle((0, 0), 1, 1, color=bar_colors[index])
            for index in positions
        ]
        ax.legend(
            legend_handles,
            labels,
            loc="lower left",
            bbox_to_anchor=(0.0, -0.02),
            frameon=True,
            fontsize=8,
            title=f"Bet size {bet_size}",
        )
        ax.grid(axis="y", alpha=0.2)

    axes[-1][0].set_xlabel("Experimentos")
    fig.tight_layout()
    fig.savefig(report_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return report_path


def save_backtest_graphs(comparison: dict, report_dir: Path) -> dict[str, Path]:
    return {
        "chart": save_backtest_chart(comparison, report_dir),
        "trend_chart": save_backtest_trend_chart(comparison, report_dir),
        "delta_chart": save_backtest_delta_chart(comparison, report_dir),
        "seed_chart": save_backtest_seed_chart(comparison, report_dir),
        "bet_size_chart": save_backtest_bet_size_chart(comparison, report_dir),
    }
