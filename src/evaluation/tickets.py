import csv
from pathlib import Path

from src.evaluation.artifacts import backtest_tickets_csv_path


class TicketCSVWriter:
    def __init__(self, report_dir: Path) -> None:
        self.path = backtest_tickets_csv_path(report_dir)
        self.file = self.path.open("w", encoding="utf-8", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow(
            [
                "experiment_id",
                "display_name",
                "family",
                "preset_name",
                "bet_size",
                "seed",
                "contest",
                "ticket_index",
                "numbers",
                "hits",
            ]
        )

    def write(
        self,
        experiment_id: str,
        display_name: str,
        family: str,
        preset_name: str | None,
        bet_size: int,
        seed: int,
        contest: int,
        ticket_index: int,
        numbers: list[int],
        hits: int,
    ) -> None:
        self.writer.writerow(
            [
                experiment_id,
                display_name,
                family,
                preset_name or "",
                bet_size,
                seed,
                contest,
                ticket_index,
                ",".join(map(str, numbers)),
                hits,
            ]
        )

    def close(self) -> None:
        self.file.close()
