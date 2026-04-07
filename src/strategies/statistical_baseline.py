import random

from src.core.models import Draw, Ticket

RANGE_LABELS = ("1-5", "6-10", "11-15", "16-20", "21-25")


def frequencia_dos_numeros(draws: list[Draw]) -> dict[int, int]:
    frequencia = {i: 0 for i in range(1, 26)}
    for draw in draws:
        for number in draw.numbers:
            frequencia[number] += 1
    return frequencia


def atraso_dos_numeros(draws: list[Draw]) -> dict[int, int]:
    atraso = {i: 0 for i in range(1, 26)}
    for draw in draws:
        for number in draw.numbers:
            atraso[number] = 0
        for num in range(1, 26):
            if num not in draw.numbers:
                atraso[num] += 1
    return atraso


def quantidade_de_pares_e_impares(draws: list[Draw]) -> tuple[int, int]:
    pares = sum(1 for draw in draws for num in draw.numbers if num % 2 == 0)
    impares = sum(1 for draw in draws for num in draw.numbers if num % 2 != 0)
    return pares, impares


def distribuicao_por_faixa(draws: list[Draw]) -> dict[str, int]:
    faixas_lotofacil = {label: 0 for label in RANGE_LABELS}
    for draw in draws:
        for num in draw.numbers:
            faixas_lotofacil[_range_label(num)] += 1
    return faixas_lotofacil


def _range_label(number: int) -> str:
    if 1 <= number <= 5:
        return "1-5"
    if 6 <= number <= 10:
        return "6-10"
    if 11 <= number <= 15:
        return "11-15"
    if 16 <= number <= 20:
        return "16-20"
    return "21-25"


def _normalize(values: dict[int, int] | dict[str, int]) -> dict:
    max_value = max(values.values(), default=0)
    if max_value == 0:
        return {key: 0.0 for key in values}
    return {key: value / max_value for key, value in values.items()}


class StatisticalBaselineStrategy:
    def __init__(
        self,
        history_draws: list[Draw],
        rng: random.Random | None = None,
        frequency_weight: float = 0.45,
        delay_weight: float = 0.35,
        parity_weight: float = 0.10,
        range_weight: float = 0.10,
        ticket_size: int = 15,
        min_even_numbers: int | None = None,
        max_even_numbers: int | None = None,
        min_numbers_per_range: int = 2,
        max_consecutive_run: int = 3,
        max_repeats_from_last_draw: int = 11,
        max_attempts: int = 250,
    ) -> None:
        if not history_draws:
            raise ValueError("history_draws não pode ser vazio.")

        self.history_draws = history_draws
        self.rng = rng or random.Random()
        self.frequency_weight = frequency_weight
        self.delay_weight = delay_weight
        self.parity_weight = parity_weight
        self.range_weight = range_weight
        self.ticket_size = ticket_size
        self.min_even_numbers = (
            min_even_numbers
            if min_even_numbers is not None
            else max(6, ticket_size - 9)
        )
        self.max_even_numbers = (
            max_even_numbers
            if max_even_numbers is not None
            else min(12, ticket_size - 6)
        )
        self.min_numbers_per_range = min_numbers_per_range
        self.max_consecutive_run = max_consecutive_run
        self.max_repeats_from_last_draw = max_repeats_from_last_draw
        self.max_attempts = max_attempts
        self.last_draw_numbers = set(history_draws[-1].numbers)

        self.scores = self._score_numbers()

    def _frequencia_dos_numeros(self) -> dict[int, int]:
        return frequencia_dos_numeros(self.history_draws)

    def _atraso_dos_numeros(self) -> dict[int, int]:
        return atraso_dos_numeros(self.history_draws)

    def _parity_scores(self) -> dict[int, float]:
        pares, impares = quantidade_de_pares_e_impares(self.history_draws)
        total = pares + impares
        if total == 0:
            even_score = 0.5
            odd_score = 0.5
        else:
            even_score = pares / total
            odd_score = impares / total

        return {
            number: even_score if number % 2 == 0 else odd_score
            for number in range(1, 26)
        }

    def _range_scores(self) -> dict[int, float]:
        normalized_ranges = _normalize(distribuicao_por_faixa(self.history_draws))
        return {
            number: normalized_ranges[_range_label(number)]
            for number in range(1, 26)
        }

    def _score_numbers(self) -> dict[int, float]:
        normalized_frequency = _normalize(self._frequencia_dos_numeros())
        normalized_delay = _normalize(self._atraso_dos_numeros())
        parity_scores = self._parity_scores()
        range_scores = self._range_scores()

        scores: dict[int, float] = {}
        for number in range(1, 26):
            scores[number] = (
                self.frequency_weight * normalized_frequency[number]
                + self.delay_weight * normalized_delay[number]
                + self.parity_weight * parity_scores[number]
                + self.range_weight * range_scores[number]
            )
        return scores

    def _weighted_sample_without_replacement(
        self,
        numbers: list[int],
        amount: int,
    ) -> list[int]:
        available = numbers[:]
        selected: list[int] = []

        while available and len(selected) < amount:
            weights = [self.scores[number] + 1e-6 for number in available]
            chosen = self.rng.choices(available, weights=weights, k=1)[0]
            selected.append(chosen)
            available.remove(chosen)

        if len(selected) != amount:
            raise ValueError("Nao foi possivel amostrar numeros suficientes.")

        return selected

    def _count_even_numbers(self, numbers: list[int]) -> int:
        return sum(1 for number in numbers if number % 2 == 0)

    def _range_distribution(self, numbers: list[int]) -> dict[str, int]:
        distribution = {label: 0 for label in RANGE_LABELS}
        for number in numbers:
            distribution[_range_label(number)] += 1
        return distribution

    def _max_consecutive_sequence(self, numbers: list[int]) -> int:
        if not numbers:
            return 0

        longest = 1
        current = 1

        for index in range(1, len(numbers)):
            if numbers[index] == numbers[index - 1] + 1:
                current += 1
            else:
                current = 1
            longest = max(longest, current)

        return longest

    def _can_add_number(
        self,
        selected_numbers: set[int],
        number: int,
        target_even_numbers: int,
    ) -> bool:
        candidate_numbers = sorted(selected_numbers | {number})

        even_numbers = self._count_even_numbers(candidate_numbers)
        remaining_slots = self.ticket_size - len(candidate_numbers)
        remaining_even_candidates = sum(
            1
            for candidate in range(1, 26)
            if candidate not in candidate_numbers and candidate % 2 == 0
        )
        remaining_odd_candidates = sum(
            1
            for candidate in range(1, 26)
            if candidate not in candidate_numbers and candidate % 2 != 0
        )

        if even_numbers > target_even_numbers:
            return False
        if even_numbers + remaining_slots < target_even_numbers:
            return False
        if remaining_even_candidates < target_even_numbers - even_numbers:
            return False
        odd_numbers = len(candidate_numbers) - even_numbers
        target_odd_numbers = self.ticket_size - target_even_numbers
        if odd_numbers > target_odd_numbers:
            return False
        if remaining_odd_candidates < target_odd_numbers - odd_numbers:
            return False

        range_distribution = self._range_distribution(candidate_numbers)
        for label, count in range_distribution.items():
            available_in_range = sum(
                1
                for candidate in range(1, 26)
                if candidate not in candidate_numbers and _range_label(candidate) == label
            )
            missing_for_minimum = max(0, self.min_numbers_per_range - count)
            if missing_for_minimum > available_in_range:
                return False
            if missing_for_minimum > remaining_slots:
                return False

        if self._max_consecutive_sequence(candidate_numbers) > self.max_consecutive_run:
            return False

        repeated_from_last_draw = len(set(candidate_numbers) & self.last_draw_numbers)
        if repeated_from_last_draw > self.max_repeats_from_last_draw:
            return False

        if not self._can_complete_ticket(candidate_numbers):
            return False

        return True

    def _can_complete_ticket(self, candidate_numbers: list[int]) -> bool:
        remaining_slots = self.ticket_size - len(candidate_numbers)
        if remaining_slots < 0:
            return False

        range_distribution = self._range_distribution(candidate_numbers)
        minimum_numbers_needed = sum(
            max(0, self.min_numbers_per_range - count)
            for count in range_distribution.values()
        )
        return minimum_numbers_needed <= remaining_slots

    def _pick_number(
        self,
        selected_numbers: set[int],
        candidates: list[int],
        target_even_numbers: int,
    ) -> int:
        available = candidates[:]

        while available:
            weights = [self.scores[number] + 1e-6 for number in available]
            chosen = self.rng.choices(available, weights=weights, k=1)[0]
            if self._can_add_number(selected_numbers, chosen, target_even_numbers):
                return chosen
            available.remove(chosen)

        raise ValueError("Nao foi possivel selecionar um numero valido.")

    def _build_ticket(self) -> Ticket:
        selected_numbers: set[int] = set()
        target_even_numbers = self.rng.randint(
            self.min_even_numbers,
            self.max_even_numbers,
        )

        for label in RANGE_LABELS:
            range_numbers = [
                number for number in range(1, 26)
                if _range_label(number) == label
            ]
            while (
                self._range_distribution(sorted(selected_numbers))[label]
                < self.min_numbers_per_range
            ):
                chosen = self._pick_number(
                    selected_numbers,
                    [number for number in range_numbers if number not in selected_numbers],
                    target_even_numbers,
                )
                selected_numbers.add(chosen)

        while len(selected_numbers) < self.ticket_size:
            remaining_numbers = [
                number for number in range(1, 26)
                if number not in selected_numbers
            ]
            chosen = self._pick_number(
                selected_numbers,
                remaining_numbers,
                target_even_numbers,
            )
            selected_numbers.add(chosen)

        return Ticket(numbers=sorted(selected_numbers))

    def _is_valid_ticket_shape(self, ticket: Ticket) -> bool:
        if len(ticket.numbers) != self.ticket_size:
            return False

        even_numbers = self._count_even_numbers(ticket.numbers)
        if not (self.min_even_numbers <= even_numbers <= self.max_even_numbers):
            return False

        range_distribution = self._range_distribution(ticket.numbers)
        if any(
            count < self.min_numbers_per_range
            for count in range_distribution.values()
        ):
            return False

        if self._max_consecutive_sequence(ticket.numbers) > self.max_consecutive_run:
            return False

        repeated_from_last_draw = len(set(ticket.numbers) & self.last_draw_numbers)
        if repeated_from_last_draw > self.max_repeats_from_last_draw:
            return False

        return True

    def generate_ticket(self) -> Ticket:
        for _ in range(self.max_attempts):
            try:
                ticket = self._build_ticket()
            except ValueError:
                continue
            if self._is_valid_ticket_shape(ticket):
                return ticket

        raise RuntimeError(
            "Nao foi possivel gerar um ticket valido com as restricoes configuradas."
        )

    def generate_tickets(self, qtd: int) -> list[Ticket]:
        return [self.generate_ticket() for _ in range(qtd)]
