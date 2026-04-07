import random

from src.app.config import build_statistical_preset
from src.core.models import Draw
from src.strategies.intentionality_vector import IntentionalityVectorStrategy
from src.strategies.quantum import QuantumSimulatorStrategy
from src.strategies.quantum_inspired import QuantumInspiredStrategy
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


def test_statistical_preset_adjusts_impossible_constraints_for_large_bets() -> None:
    preset_19 = build_statistical_preset("balanced", ticket_size=19)
    preset_20 = build_statistical_preset("conservative_shape", ticket_size=20)

    assert preset_19["max_consecutive_run"] >= 4
    assert preset_19["max_repeats_from_last_draw"] >= 10
    assert preset_20["max_consecutive_run"] >= 4
    assert preset_20["max_repeats_from_last_draw"] >= 13


def test_intentionality_vector_strategy_supports_ticket_size_above_15() -> None:
    history_draws = [
        Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        Draw(contest=3, numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ]

    strategy = IntentionalityVectorStrategy(
        history_draws=history_draws,
        rng=random.Random(999),
        ticket_size=18,
    )

    ticket = strategy.generate_ticket()

    assert len(ticket.numbers) == 18


def test_intentionality_vector_strategy_keeps_at_least_one_number_per_range() -> None:
    history_draws = [
        Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        Draw(contest=3, numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ]

    strategy = IntentionalityVectorStrategy(
        history_draws=history_draws,
        rng=random.Random(100),
        ticket_size=15,
    )

    ticket = strategy.generate_ticket()

    assert any(1 <= number <= 5 for number in ticket.numbers)
    assert any(6 <= number <= 10 for number in ticket.numbers)
    assert any(11 <= number <= 15 for number in ticket.numbers)
    assert any(16 <= number <= 20 for number in ticket.numbers)
    assert any(21 <= number <= 25 for number in ticket.numbers)


def test_quantum_inspired_strategy_supports_ticket_size_above_15() -> None:
    history_draws = [
        Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        Draw(contest=3, numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ]

    strategy = QuantumInspiredStrategy(
        history_draws=history_draws,
        rng=random.Random(777),
        ticket_size=18,
    )

    ticket = strategy.generate_ticket()

    assert len(ticket.numbers) == 18


def test_quantum_strategy_supports_ticket_size_above_15() -> None:
    history_draws = [
        Draw(contest=1, numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        Draw(contest=2, numbers=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
        Draw(contest=3, numbers=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]),
    ]

    strategy = QuantumSimulatorStrategy(
        history_draws=history_draws,
        rng=random.Random(555),
        ticket_size=18,
    )

    ticket = strategy.generate_ticket()

    assert len(ticket.numbers) == 18
