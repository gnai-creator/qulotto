import random

from src.core.models import Draw, Ticket

RANGE_LABELS = ("1-5", "6-10", "11-15", "16-20", "21-25")
TOTAL_NUMBERS = 25
LAST_DRAW_SIZE = 15


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


def minimum_feasible_max_consecutive_run(ticket_size: int) -> int:
    missing_numbers = TOTAL_NUMBERS - ticket_size
    available_blocks = missing_numbers + 1
    return (ticket_size + available_blocks - 1) // available_blocks


def minimum_feasible_repeats_from_last_draw(ticket_size: int) -> int:
    available_outside_last_draw = TOTAL_NUMBERS - LAST_DRAW_SIZE
    return max(0, ticket_size - available_outside_last_draw)


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

        self._validate_constraints()
        self.scores = self._score_numbers()

    def _validate_constraints(self) -> None:
        if not 15 <= self.ticket_size <= 20:
            raise ValueError("ticket_size deve estar entre 15 e 20.")

        if self.min_even_numbers > self.max_even_numbers:
            raise ValueError("min_even_numbers nao pode ser maior que max_even_numbers.")

        if self.min_even_numbers < max(0, self.ticket_size - 13):
            raise ValueError("min_even_numbers abaixo do minimo viavel para o tamanho da aposta.")

        if self.max_even_numbers > min(12, self.ticket_size):
            raise ValueError("max_even_numbers acima do maximo viavel para o tamanho da aposta.")

        if self.min_numbers_per_range * len(RANGE_LABELS) > self.ticket_size:
            raise ValueError("min_numbers_per_range torna o ticket impossivel para esse tamanho.")

        minimum_run = minimum_feasible_max_consecutive_run(self.ticket_size)
        if self.max_consecutive_run < minimum_run:
            raise ValueError(
                "max_consecutive_run abaixo do minimo viavel para o tamanho da aposta."
            )

        minimum_repeats = minimum_feasible_repeats_from_last_draw(self.ticket_size)
        if self.max_repeats_from_last_draw < minimum_repeats:
            raise ValueError(
                "max_repeats_from_last_draw abaixo do minimo viavel para o tamanho da aposta."
            )

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

    def _weighted_exclusions(self, amount: int) -> list[int]:
        available = list(range(1, 26))
        selected: list[int] = []
        max_score = max(self.scores.values(), default=1.0)

        while available and len(selected) < amount:
            weights = [
                (max_score - self.scores[number]) + 1e-6
                for number in available
            ]
            chosen = self.rng.choices(available, weights=weights, k=1)[0]
            selected.append(chosen)
            available.remove(chosen)

        if len(selected) != amount:
            raise ValueError("Nao foi possivel amostrar exclusoes suficientes.")

        return selected

    def _exclusion_order(self) -> list[int]:
        return self._weighted_exclusions(TOTAL_NUMBERS)

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

    def _can_complete_large_ticket(self, excluded_numbers: set[int]) -> bool:
        exclusions_needed = TOTAL_NUMBERS - self.ticket_size
        remaining_exclusions = exclusions_needed - len(excluded_numbers)
        if remaining_exclusions < 0:
            return False

        excluded_even = sum(1 for number in excluded_numbers if number % 2 == 0)
        max_final_even = 12 - excluded_even
        min_final_even = max_final_even - min(
            remaining_exclusions,
            12 - excluded_even,
        )
        if max_final_even < self.min_even_numbers:
            return False
        if min_final_even > self.max_even_numbers:
            return False

        excluded_from_last_draw = len(excluded_numbers & self.last_draw_numbers)
        current_repeats = LAST_DRAW_SIZE - excluded_from_last_draw
        available_last_draw_exclusions = LAST_DRAW_SIZE - excluded_from_last_draw
        min_possible_repeats = current_repeats - min(
            remaining_exclusions,
            available_last_draw_exclusions,
        )
        if min_possible_repeats > self.max_repeats_from_last_draw:
            return False

        excluded_by_range = {label: 0 for label in RANGE_LABELS}
        for number in excluded_numbers:
            excluded_by_range[_range_label(number)] += 1

        for label in RANGE_LABELS:
            final_included = 5 - excluded_by_range[label]
            if final_included < self.min_numbers_per_range:
                return False

        return True

    def _search_large_ticket(
        self,
        ordered_numbers: list[int],
        start_index: int,
        excluded_numbers: set[int],
    ) -> Ticket | None:
        exclusions_needed = TOTAL_NUMBERS - self.ticket_size

        if len(excluded_numbers) == exclusions_needed:
            ticket = Ticket(
                numbers=[
                    number for number in range(1, 26)
                    if number not in excluded_numbers
                ]
            )
            if self._is_valid_ticket_shape(ticket):
                return ticket
            return None

        if not self._can_complete_large_ticket(excluded_numbers):
            return None

        remaining_to_choose = exclusions_needed - len(excluded_numbers)
        remaining_candidates = len(ordered_numbers) - start_index
        if remaining_candidates < remaining_to_choose:
            return None

        for index in range(start_index, len(ordered_numbers)):
            number = ordered_numbers[index]
            excluded_numbers.add(number)
            ticket = self._search_large_ticket(
                ordered_numbers,
                index + 1,
                excluded_numbers,
            )
            if ticket is not None:
                return ticket
            excluded_numbers.remove(number)

        return None

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

    def _candidate_pool(self, selected_numbers: set[int]) -> list[int]:
        distribution = self._range_distribution(sorted(selected_numbers))
        missing_ranges = [
            label
            for label, count in distribution.items()
            if count < self.min_numbers_per_range
        ]
        if missing_ranges:
            return [
                number
                for number in range(1, 26)
                if number not in selected_numbers
                and _range_label(number) in missing_ranges
            ]

        return [
            number for number in range(1, 26)
            if number not in selected_numbers
        ]

    def _ordered_candidates(self, selected_numbers: set[int]) -> list[int]:
        candidates = self._candidate_pool(selected_numbers)
        if not candidates:
            return []
        return self._weighted_sample_without_replacement(candidates, len(candidates))

    def _search_ticket(
        self,
        selected_numbers: set[int],
        target_even_numbers: int,
    ) -> Ticket | None:
        if len(selected_numbers) == self.ticket_size:
            ticket = Ticket(numbers=sorted(selected_numbers))
            if self._is_valid_ticket_shape(ticket):
                return ticket
            return None

        for number in self._ordered_candidates(selected_numbers):
            if not self._can_add_number(selected_numbers, number, target_even_numbers):
                continue
            selected_numbers.add(number)
            ticket = self._search_ticket(selected_numbers, target_even_numbers)
            if ticket is not None:
                return ticket
            selected_numbers.remove(number)

        return None

    def _build_ticket(self) -> Ticket:
        if self.ticket_size >= 19:
            ticket = self._search_large_ticket(
                self._exclusion_order(),
                0,
                set(),
            )
            if ticket is None:
                raise ValueError("Nao foi possivel construir um ticket grande valido.")
            return ticket

        target_even_numbers = self.rng.randint(
            self.min_even_numbers,
            self.max_even_numbers,
        )
        ticket = self._search_ticket(set(), target_even_numbers)
        if ticket is None:
            raise ValueError("Nao foi possivel construir um ticket valido.")
        return ticket

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
