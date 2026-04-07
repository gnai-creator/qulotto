from datetime import date
from pathlib import Path

from src.app.config import REPORT_DIR


def next_report_dir() -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    existing = [
        int(path.name)
        for path in REPORT_DIR.iterdir()
        if path.is_dir() and path.name.isdigit()
    ]

    next_number = max(existing, default=0) + 1
    report_dir = REPORT_DIR / f"{next_number:03d}"
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir


def artifact_date() -> str:
    return date.today().isoformat()


def backtest_markdown_path(report_dir: Path) -> Path:
    return report_dir / f"backtest_{artifact_date()}.md"


def backtest_json_path(report_dir: Path) -> Path:
    return report_dir / f"backtest_{artifact_date()}.json"


def backtest_csv_path(report_dir: Path) -> Path:
    return report_dir / f"backtest_{artifact_date()}.csv"


def backtest_summary_csv_path(report_dir: Path) -> Path:
    return report_dir / f"backtest_summary_{artifact_date()}.csv"


def backtest_tickets_csv_path(report_dir: Path) -> Path:
    return report_dir / f"backtest_tickets_{artifact_date()}.csv"


def backtest_seed_csv_path(report_dir: Path) -> Path:
    return report_dir / f"backtest_seeds_{artifact_date()}.csv"


def history_csv_path() -> Path:
    return REPORT_DIR / "history.csv"


def backtest_chart_path(report_dir: Path) -> Path:
    return report_dir / f"backtest_{artifact_date()}.png"


def backtest_trend_chart_path(report_dir: Path) -> Path:
    return report_dir / f"backtest_trend_{artifact_date()}.png"


def backtest_delta_chart_path(report_dir: Path) -> Path:
    return report_dir / f"backtest_delta_{artifact_date()}.png"


def backtest_seed_chart_path(report_dir: Path) -> Path:
    return report_dir / f"backtest_seeds_{artifact_date()}.png"


def backtest_bet_size_chart_path(report_dir: Path) -> Path:
    return report_dir / f"backtest_bet_sizes_{artifact_date()}.png"
