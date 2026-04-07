from src.app.cli import parse_arguments
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
        cost_by_bet_size[bet_size] = cost_by_bet_size.get(bet_size, 0.0) + experiment_cost

    total_cost = sum(cost_by_bet_size.values())
    return total_cost, dict(sorted(cost_by_bet_size.items()))


def main() -> None:
    args = parse_arguments()
    draws = load_draws_from_csv()
    report_dir = next_report_dir()
    ticket_writer = TicketCSVWriter(report_dir)

    presets = FULL_PRESET_NAMES if args.completo else args.presets
    bet_sizes = (
        [args.tamanho_aposta]
        if args.tamanho_aposta is not None
        else (FULL_BET_SIZES if args.completo else args.tamanhos_aposta)
    )
    seeds = build_seed_list(args.seed, args.seed_count)
    experiment_specs = build_experiment_specs(presets, bet_sizes)

    if args.future:
        prediction_bundle = build_future_predictions(
            draws=draws,
            specs=experiment_specs,
            qtd_por_experimento=args.qtd,
            history_window=args.history,
            seeds=seeds,
        )
        artifact_paths = save_future_artifacts(prediction_bundle, report_dir)
        print(
            f"Palpites gerados para o concurso futuro "
            f"{prediction_bundle['params']['future_contest']}"
        )
        print(f"Markdown salvo em: {artifact_paths['markdown']}")
        print(f"JSON salvo em: {artifact_paths['json']}")
        print(f"CSV salvo em: {artifact_paths['csv']}")
        return

    target_draw_count = _count_target_draws(draws, args.inicio, args.fim)
    total_runs = len(experiment_specs) * len(seeds)
    estimated_tickets = total_runs * target_draw_count * args.qtd
    estimated_total_cost, estimated_cost_by_bet_size = _estimate_batch_cost(
        experiment_specs=experiment_specs,
        target_draw_count=target_draw_count,
        qtd_por_concurso=args.qtd,
        seed_count=len(seeds),
    )

    try:
        print(
            f"Executando {len(experiment_specs)} experimentos x {len(seeds)} seeds "
            f"= {total_runs} runs",
            flush=True,
        )
        print(
            f"Estimativa: {target_draw_count} concursos, "
            f"{estimated_tickets} tickets, bet_sizes={bet_sizes}, presets={presets}",
            flush=True,
        )
        print(
            f"Custo estimado da bateria: R$ {estimated_total_cost:,.2f}",
            flush=True,
        )
        print(
            "Custo estimado por tamanho: "
            + ", ".join(
                f"{bet_size} dezenas = R$ {cost:,.2f}"
                for bet_size, cost in estimated_cost_by_bet_size.items()
            ),
            flush=True,
        )
        results = run_experiment_specs(
            draws=draws,
            specs=experiment_specs,
            qtd_por_concurso=args.qtd,
            history_window=args.history,
            inicio=args.inicio,
            fim=args.fim,
            seeds=seeds,
            ticket_callback=lambda **row: ticket_writer.write(**row),
            progress_callback=lambda current, total, spec, seed: print(
                f"[{current}/{total}] {spec['display_name']} | seed={seed}",
                flush=True,
            ),
        )
        comparison = {
            "params": {
                "qtd_por_concurso": args.qtd,
                "bet_sizes": bet_sizes,
                "inicio": args.inicio,
                "fim": args.fim,
                "history": args.history,
                "seed_start": args.seed,
                "seed_count": args.seed_count,
                "seeds": seeds,
                "presets": presets,
                "completo": args.completo,
                "target_draw_count": target_draw_count,
                "total_runs": total_runs,
                "estimated_tickets": estimated_tickets,
                "estimated_total_cost": estimated_total_cost,
                "estimated_cost_by_bet_size": estimated_cost_by_bet_size,
            },
            "experiments": {spec["id"]: spec for spec in experiment_specs},
            "results": results,
        }
        artifact_paths = save_backtest_artifacts_in_dir(comparison, report_dir)
    finally:
        ticket_writer.close()

    print(f"Grafico PNG salvo em: {artifact_paths['chart']}")
    print(f"Grafico de tendencia salvo em: {artifact_paths['trend_chart']}")
    print(f"Grafico de delta salvo em: {artifact_paths['delta_chart']}")
    print(f"Grafico por seed salvo em: {artifact_paths['seed_chart']}")
    print(f"Grafico por tamanho de aposta salvo em: {artifact_paths['bet_size_chart']}")
    print(f"Relatório Markdown salvo em: {artifact_paths['markdown']}")
    print(f"Artefato JSON salvo em: {artifact_paths['json']}")
    print(f"Resumo CSV salvo em: {artifact_paths['csv']}")
    print(f"CSV agregado salvo em: {artifact_paths['summary_csv']}")
    print(f"CSV por seed salvo em: {artifact_paths['seed_csv']}")
    print(f"Histórico CSV salvo em: {artifact_paths['history_csv']}")
    print(f"Tickets CSV salvo em: {ticket_writer.path}")


if __name__ == "__main__":
    main()
