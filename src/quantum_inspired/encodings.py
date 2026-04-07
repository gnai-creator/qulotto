from src.core.models import Draw


class QuantumFeatureEncoder:
    """Codifica o historico em amplitudes inspiradas em superposicao."""

    def __init__(self, decay_alpha: float = 0.08) -> None:
        self.decay_alpha = decay_alpha

    def encode(self, history_draws: list[Draw]) -> dict[int, float]:
        if not history_draws:
            raise ValueError("history_draws nao pode ser vazio.")

        weighted_scores = {number: 0.0 for number in range(1, 26)}
        total_draws = len(history_draws)

        for index, draw in enumerate(history_draws):
            recency_distance = total_draws - index - 1
            recency_weight = 1.0 / (1.0 + self.decay_alpha * recency_distance)
            for number in draw.numbers:
                weighted_scores[number] += recency_weight

        total_score = sum(weighted_scores.values())
        if total_score == 0:
            return {number: 1 / 25 for number in range(1, 26)}

        probabilities = {
            number: score / total_score
            for number, score in weighted_scores.items()
        }
        return {
            number: probability ** 0.5
            for number, probability in probabilities.items()
        }
