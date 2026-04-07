from pathlib import Path

from src.evaluation import reporting


def test_save_backtest_artifacts_creates_expected_files(tmp_path: Path, monkeypatch) -> None:
    report_dir = tmp_path / "001"
    report_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(reporting, "next_report_dir", lambda: report_dir)
    monkeypatch.setattr(reporting, "history_csv_path", lambda: tmp_path / "history.csv")

    comparison = {
        "params": {
            "qtd_por_concurso": 10,
            "bet_sizes": [15],
            "inicio": 1,
            "fim": 2,
            "history": 5,
            "seed_start": 42,
            "seed_count": 2,
            "seeds": [42, 43],
            "presets": ["balanced"],
        },
        "experiments": {
            "random_15": {
                "id": "random_15",
                "display_name": "Random 15",
                "family": "random",
                "preset_name": None,
                "bet_size": 15,
                "strategy_name": "random",
                "strategy_kwargs": {"ticket_size": 15},
            },
            "statistical_balanced_15": {
                "id": "statistical_balanced_15",
                "display_name": "Statistical balanced 15",
                "family": "statistical",
                "preset_name": "balanced",
                "bet_size": 15,
                "strategy_name": "statistical",
                "strategy_kwargs": {
                    "frequency_weight": 0.45,
                    "delay_weight": 0.35,
                    "parity_weight": 0.10,
                    "range_weight": 0.10,
                    "ticket_size": 15,
                    "min_even_numbers": 6,
                    "max_even_numbers": 9,
                    "min_numbers_per_range": 2,
                    "max_consecutive_run": 3,
                    "max_repeats_from_last_draw": 11,
                    "max_attempts": 250,
                },
            },
        },
        "results": {
            "random_15": {
                "strategy": "random",
                "qtd_concursos_avaliados": 2,
                "qtd_tickets_total": 20,
                "summary_geral": {
                    "total": 20,
                    "media": 8.5,
                    "max": 12,
                    "min": 5,
                    "distribution": {5: 2, 8: 10, 12: 8},
                },
                "resultados_por_concurso": [
                    {"contest": 1, "summary": {"total": 10, "media": 8.2, "max": 11, "min": 5}},
                    {"contest": 2, "summary": {"total": 10, "media": 8.8, "max": 12, "min": 6}},
                ],
                "cost_analysis": {
                    "bet_cost": 3.5,
                    "relative_cost": 1.0,
                    "media_por_real": 2.428571,
                    "maximo_por_real": 3.428571,
                },
                "seed_results": {
                    42: {
                        "summary_geral": {
                            "total": 10,
                            "media": 8.4,
                            "max": 11,
                            "min": 5,
                            "distribution": {5: 1, 8: 5, 11: 4},
                        }
                    },
                    43: {
                        "summary_geral": {
                            "total": 10,
                            "media": 8.6,
                            "max": 12,
                            "min": 6,
                            "distribution": {6: 1, 8: 5, 12: 4},
                        }
                    },
                },
            },
            "statistical_balanced_15": {
                "strategy": "statistical",
                "qtd_concursos_avaliados": 2,
                "qtd_tickets_total": 20,
                "summary_geral": {
                    "total": 20,
                    "media": 9.1,
                    "max": 13,
                    "min": 6,
                    "distribution": {6: 3, 9: 9, 13: 8},
                },
                "resultados_por_concurso": [
                    {"contest": 1, "summary": {"total": 10, "media": 8.9, "max": 12, "min": 6}},
                    {"contest": 2, "summary": {"total": 10, "media": 9.3, "max": 13, "min": 7}},
                ],
                "cost_analysis": {
                    "bet_cost": 3.5,
                    "relative_cost": 1.0,
                    "media_por_real": 2.6,
                    "maximo_por_real": 3.714285,
                },
                "seed_results": {
                    42: {
                        "summary_geral": {
                            "total": 10,
                            "media": 8.9,
                            "max": 12,
                            "min": 6,
                            "distribution": {6: 2, 9: 4, 12: 4},
                        }
                    },
                    43: {
                        "summary_geral": {
                            "total": 10,
                            "media": 9.3,
                            "max": 13,
                            "min": 7,
                            "distribution": {7: 1, 9: 5, 13: 4},
                        }
                    },
                },
            },
        },
    }

    artifact_paths = reporting.save_backtest_artifacts(comparison)

    expected_keys = {
        "chart",
        "trend_chart",
        "delta_chart",
        "seed_chart",
        "bet_size_chart",
        "markdown",
        "json",
        "csv",
        "summary_csv",
        "seed_csv",
        "history_csv",
    }
    assert set(artifact_paths) == expected_keys
    assert all(path.exists() for path in artifact_paths.values())

    markdown = artifact_paths["markdown"].read_text(encoding="utf-8")
    assert "backtest_" in markdown
    assert "backtest_trend_" in markdown
    assert "backtest_delta_" in markdown
    assert "backtest_seeds_" in markdown
    assert "backtest_bet_sizes_" in markdown
