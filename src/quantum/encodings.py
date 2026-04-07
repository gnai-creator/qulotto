from src.core.models import Draw

STATE_VECTOR_SIZE = 32
NUMBER_COUNT = 25


class QuantumStateEncoder:
    """Codifica o historico em um vetor de amplitudes de 5 qubits."""

    def __init__(self, decay_alpha: float = 0.08) -> None:
        self.decay_alpha = decay_alpha

    def weighted_number_scores(self, history_draws: list[Draw]) -> dict[int, float]:
        if not history_draws:
            raise ValueError("history_draws nao pode ser vazio.")

        scores = {number: 0.0 for number in range(1, NUMBER_COUNT + 1)}
        total_draws = len(history_draws)

        for index, draw in enumerate(history_draws):
            recency_distance = total_draws - index - 1
            recency_weight = 1.0 / (1.0 + self.decay_alpha * recency_distance)
            for number in draw.numbers:
                scores[number] += recency_weight

        return scores

    def encode(self, history_draws: list[Draw]) -> list[float]:
        scores = self.weighted_number_scores(history_draws)
        total_score = sum(scores.values())
        if total_score == 0:
            probability = 1.0 / NUMBER_COUNT
            amplitudes = [probability**0.5 for _ in range(NUMBER_COUNT)]
        else:
            amplitudes = [
                (scores[number] / total_score) ** 0.5
                for number in range(1, NUMBER_COUNT + 1)
            ]

        state_vector = amplitudes + [0.0] * (STATE_VECTOR_SIZE - NUMBER_COUNT)
        return _normalize(state_vector)


def _normalize(values: list[float]) -> list[float]:
    norm = sum(value * value for value in values) ** 0.5
    if norm == 0:
        return values
    return [value / norm for value in values]
