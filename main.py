from src.app.cli import parse_arguments
from src.data.repository import load_draws_from_csv
from src.evaluation.artifacts import next_report_dir
from src.evaluation.experiments import (
    build_experiment_specs,
    build_seed_list,
    run_experiment_specs,
)
from src.evaluation.reporting import save_backtest_artifacts_in_dir
from src.evaluation.tickets import TicketCSVWriter


def main() -> None:
    args = parse_arguments()
    draws = load_draws_from_csv()
    report_dir = next_report_dir()
    ticket_writer = TicketCSVWriter(report_dir)

    bet_sizes = (
        [args.tamanho_aposta]
        if args.tamanho_aposta is not None
        else args.tamanhos_aposta
    )
    seeds = build_seed_list(args.seed, args.seed_count)
    experiment_specs = build_experiment_specs(args.presets, bet_sizes)

    try:
        results = run_experiment_specs(
            draws=draws,
            specs=experiment_specs,
            qtd_por_concurso=args.qtd,
            history_window=args.history,
            inicio=args.inicio,
            fim=args.fim,
            seeds=seeds,
            ticket_callback=lambda **row: ticket_writer.write(**row),
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
                "presets": args.presets,
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
