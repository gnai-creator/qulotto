from src.app.cli import parse_arguments
from src.app.service import (
    preview_backtest_workflow,
    run_backtest_workflow,
    run_future_workflow,
)


def main() -> None:
    args = parse_arguments()
    options = vars(args)

    if args.future:
        result = run_future_workflow(options)
        print(
            f"Palpites gerados para o concurso futuro "
            f"{result['summary']['future_contest']}"
        )
        print(f"Markdown salvo em: {result['artifact_paths']['markdown']}")
        print(f"JSON salvo em: {result['artifact_paths']['json']}")
        print(f"CSV salvo em: {result['artifact_paths']['csv']}")
        return

    preview = preview_backtest_workflow(options)
    summary = preview["summary"]
    print(f"Executando {summary['total_runs']} runs", flush=True)
    print(
        f"Estimativa: {summary['target_draw_count']} concursos, "
        f"{summary['estimated_tickets']} tickets",
        flush=True,
    )
    print(
        f"Custo estimado da bateria: R$ {summary['estimated_total_cost']:,.2f}",
        flush=True,
    )
    print(
        "Custo estimado por tamanho: "
        + ", ".join(
            f"{bet_size} dezenas = R$ {cost:,.2f}"
            for bet_size, cost in summary["estimated_cost_by_bet_size"].items()
        ),
        flush=True,
    )
    result = run_backtest_workflow(
        options,
        progress_callback=lambda current, total, spec, seed: print(
            f"[{current}/{total}] {spec['display_name']} | seed={seed}",
            flush=True,
        ),
    )
    artifact_paths = result["artifact_paths"]
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
    print(f"Tickets CSV salvo em: {result['tickets_csv']}")


if __name__ == "__main__":
    main()
