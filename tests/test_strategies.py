import random

from src.core.models import Draw
from src.strategies.statistical_baseline import StatisticalBaselineStrategy


def test_statistical_strategy_is_reproducible_with_seed() -> None:
    history_draws = [
        Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        Draw(contest=3, numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ]

    strategy_a = StatisticalBaselineStrategy(history_draws, rng=random.Random(123))
    strategy_b = StatisticalBaselineStrategy(history_draws, rng=random.Random(123))

    tickets_a = strategy_a.generate_tickets(3)
    tickets_b = strategy_b.generate_tickets(3)

    assert [ticket.numbers for ticket in tickets_a] == [ticket.numbers for ticket in tickets_b]
    assert all(len(ticket.numbers) == 15 for ticket in tickets_a)


def test_statistical_strategy_generates_tickets_with_expected_shape() -> None:
    history_draws = [
        Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        Draw(contest=3, numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
        Draw(contest=4, numbers=[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]),
        Draw(contest=5, numbers=[5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]),
    ]

    strategy = StatisticalBaselineStrategy(history_draws, rng=random.Random(321))

    ticket = strategy.generate_ticket()

    even_numbers = sum(1 for number in ticket.numbers if number % 2 == 0)
    range_counts = {
        "1-5": sum(1 for number in ticket.numbers if 1 <= number <= 5),
        "6-10": sum(1 for number in ticket.numbers if 6 <= number <= 10),
        "11-15": sum(1 for number in ticket.numbers if 11 <= number <= 15),
        "16-20": sum(1 for number in ticket.numbers if 16 <= number <= 20),
        "21-25": sum(1 for number in ticket.numbers if 21 <= number <= 25),
    }
    repeats_from_last_draw = len(set(ticket.numbers) & set(history_draws[-1].numbers))

    assert 6 <= even_numbers <= 9
    assert all(count >= 2 for count in range_counts.values())
    assert repeats_from_last_draw <= 11


def test_random_strategy_supports_ticket_size_above_15() -> None:
    from src.strategies.random_baseline import RandomBaselineStrategy

    strategy = RandomBaselineStrategy(rng=random.Random(55), ticket_size=18)

    ticket = strategy.generate_ticket()

    assert len(ticket.numbers) == 18
