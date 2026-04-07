from pathlib import Path

from src.core.models import Draw
from src.data import repository


def test_save_and_load_draws_from_csv(tmp_path: Path, monkeypatch) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    monkeypatch.setattr(repository, "RAW_DIR", raw_dir)
    monkeypatch.setattr(repository, "PROCESSED_DIR", processed_dir)

    first_draw = Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    second_draw = Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])

    repository.save_processed_draw(first_draw, first_draw.contest)
    repository.save_processed_draw(second_draw, second_draw.contest)

    draws = repository.load_draws_from_csv()
    latest = repository.load_latest_draw_from_csv()
    by_contest = repository.load_draw_by_contest_from_csv(2)

    assert [draw.contest for draw in draws] == [1, 2]
    assert latest == second_draw
    assert by_contest == second_draw
    assert repository.get_last_processed_contest() == 2
