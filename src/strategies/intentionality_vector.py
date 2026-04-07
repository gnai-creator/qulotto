import random
from typing import TypeVar

from src.core.models import Draw, Ticket

RANGE_VECTORS = ("1-5", "6-10", "11-15", "16-20", "21-25")
TOTAL_NUMBERS = 25
LAST_DRAW_SIZE = 15

_RANGE_MAP: dict[str, range] = {
    "1-5":   range(1, 6),
    "6-10":  range(6, 11),
    "11-15": range(11, 16),
    "16-20": range(16, 21),
    "21-25": range(21, 26),
}

_KT = TypeVar('_KT')

def sanatiza_vetor_intencional(vetor: dict[_KT, float]) -> dict[_KT, float]:
    """Normaliza os valores do vetor para escala [0, 1]."""
    max_value = max(vetor.values(), default=0.0)
    if max_value == 0:
        return vetor
    return {k: v / max_value for k, v in vetor.items()}

def draw_to_vector(draw: Draw) -> dict[int, float]:
    vetor_intencional: dict[int, float] = {i: 0.0 for i in range(1, 26)}
    for number in draw.numbers:
        vetor_intencional[number] = number / LAST_DRAW_SIZE
    return vetor_intencional


def soma_vetor_intencional(
    draws: list[Draw],
    *,
    decay_alpha: float = 0.08,
) -> dict[int, float]:
    vetor_intencional: dict[int, float] = {i: 0.0 for i in range(1, 26)}
    total_draws = len(draws)

    for index, draw in enumerate(draws):
        recency_distance = total_draws - index - 1
        recency_weight = 1.0 / (1.0 + decay_alpha * recency_distance)
        draw_vector = draw_to_vector(draw)
        for number in draw.numbers:
            vetor_intencional[number] += draw_vector[number] * recency_weight

    return vetor_intencional

def vetor_intencional_por_range(
    draws: list[Draw],
    *,
    decay_alpha: float = 0.08,
) -> dict[str, float]:
    range_intent_vector: dict[str, float] = {r: 0.0 for r in RANGE_VECTORS}
    soma = soma_vetor_intencional(draws, decay_alpha=decay_alpha)

    for label, nums in _RANGE_MAP.items():
        range_intent_vector[label] = sum(soma[n] for n in nums)

    return sanatiza_vetor_intencional(range_intent_vector)


class IntentionalityVectorStrategy:
    def __init__(
        self,
        history_draws: list[Draw],
        rng: random.Random | None = None,
        ticket_size: int = 15,
        decay_alpha: float = 0.08,
        min_numbers_per_range: int = 1,
        ) -> None:
        if not history_draws:
            raise ValueError("history_draws não pode ser vazio.")
        
        self.history_draws = history_draws
        self.rng = rng or random.Random()
        self.ticket_size = ticket_size
        self.decay_alpha = decay_alpha
        self.min_numbers_per_range = min_numbers_per_range
        self.last_draw_numbers = set(history_draws[-1].numbers)
        
        self._validate_constraints()
        self.number_scores = self._number_scores()
        self.range_scores = self._vetor_intencional_por_range()
            
    def _validate_constraints(self) -> None:
        if not 15 <= self.ticket_size <= 20:
            raise ValueError("ticket_size deve estar entre 15 e 20.")
        if self.min_numbers_per_range < 0:
            raise ValueError("min_numbers_per_range nao pode ser negativo.")
        if self.min_numbers_per_range * len(RANGE_VECTORS) > self.ticket_size:
            raise ValueError("min_numbers_per_range inviavel para o tamanho da aposta.")
    
    def _soma_vetor_intencional(self) -> dict[int, float]:
        return soma_vetor_intencional(
            self.history_draws,
            decay_alpha=self.decay_alpha,
        )

    def _vetor_intencional_por_range(self) -> dict[str, float]:
        return vetor_intencional_por_range(
            self.history_draws,
            decay_alpha=self.decay_alpha,
        )

    def _number_scores(self) -> dict[int, float]:
        recency_bonus = {
            number: 1.0 if number in self.last_draw_numbers else 0.25
            for number in range(1, 26)
        }
        base_scores = self._soma_vetor_intencional()
        adjusted_scores = {
            number: base_scores[number] * recency_bonus[number]
            for number in range(1, 26)
        }
        return sanatiza_vetor_intencional(adjusted_scores)

    def _target_counts_by_range(self) -> dict[str, int]:
        weights = self.range_scores
        total_weight = sum(weights.values())
        if total_weight == 0:
            normalized_weights = {
                label: 1 / len(RANGE_VECTORS) for label in RANGE_VECTORS
            }
        else:
            normalized_weights = {
                label: weights[label] / total_weight for label in RANGE_VECTORS
            }

        target_counts = {
            label: self.min_numbers_per_range for label in RANGE_VECTORS
        }
        allocated = sum(target_counts.values())
        remaining_slots = self.ticket_size - allocated

        if remaining_slots == 0:
            return target_counts

        raw_extra = {
            label: normalized_weights[label] * remaining_slots
            for label in RANGE_VECTORS
        }
        for label in RANGE_VECTORS:
            capacity = len(_RANGE_MAP[label]) - target_counts[label]
            base_extra = min(capacity, int(raw_extra[label]))
            target_counts[label] += base_extra

        allocated = sum(target_counts.values())
        remaining_slots = self.ticket_size - allocated

        while remaining_slots > 0:
            remainders = sorted(
                RANGE_VECTORS,
                key=lambda label: (
                    raw_extra[label] - int(raw_extra[label]),
                    normalized_weights[label],
                ),
                reverse=True,
            )
            assigned = False
            for label in remainders:
                if target_counts[label] >= len(_RANGE_MAP[label]):
                    continue
                target_counts[label] += 1
                remaining_slots -= 1
                assigned = True
                if remaining_slots == 0:
                    break
            if not assigned:
                break

        return target_counts

    def _weighted_sample_without_replacement(
        self,
        numbers: list[int],
        amount: int,
        weights: dict[int, float],
    ) -> list[int]:
        available = numbers[:]
        selected: list[int] = []

        while available and len(selected) < amount:
            choices_weights = [weights[number] + 1e-6 for number in available]
            chosen = self.rng.choices(available, weights=choices_weights, k=1)[0]
            selected.append(chosen)
            available.remove(chosen)

        if len(selected) != amount:
            raise ValueError("Nao foi possivel selecionar dezenas suficientes.")

        return selected

    def _sample_weighted_without_replacement(
        self,
        numbers: list[int],
        amount: int,
        scores: dict[int, float],
    ) -> list[int]:
        return self._weighted_sample_without_replacement(numbers, amount, scores)

    def _remaining_range_targets(
        self,
        selected_numbers: set[int],
    ) -> dict[str, int]:
        range_targets = self._target_counts_by_range()
        for number in selected_numbers:
            label = next(label for label, nums in _RANGE_MAP.items() if number in nums)
            if range_targets[label] > 0:
                range_targets[label] -= 1
        return range_targets
    
    def generate_ticket(self) -> Ticket:
        selected_numbers: set[int] = set()
        counts_by_range = self._target_counts_by_range()

        for label in RANGE_VECTORS:
            range_numbers = list(_RANGE_MAP[label])
            amount = counts_by_range[label]
            if amount == 0:
                continue
            chosen = self._sample_weighted_without_replacement(
                numbers=range_numbers,
                amount=amount,
                scores=self.number_scores,
            )
            selected_numbers.update(chosen)

        if len(selected_numbers) < self.ticket_size:
            remaining_numbers = [
                number for number in range(1, 26)
                if number not in selected_numbers
            ]
            chosen = self._sample_weighted_without_replacement(
                numbers=remaining_numbers,
                amount=self.ticket_size - len(selected_numbers),
                scores=self.number_scores,
            )
            selected_numbers.update(chosen)

        return Ticket(numbers=sorted(selected_numbers))
        
    
    def generate_tickets(self, qtd: int) -> list[Ticket]:
        return [self.generate_ticket() for _ in range(qtd)]
