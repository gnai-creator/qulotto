from src.core.scoring import count_hits
from src.core.models import Draw, Ticket


def test_count_hits_returns_intersection_size() -> None:
    draw = Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    ticket = Ticket(numbers=[1, 2, 3, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])

    assert count_hits(ticket, draw) == 5
