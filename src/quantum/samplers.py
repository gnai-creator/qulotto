import random

from src.quantum.encodings import NUMBER_COUNT


class QuantumMeasurementSampler:
    """Mede o estado e amostra dezenas sem reposicao."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()

    def sample(self, state_vector: list[float], ticket_size: int) -> list[int]:
        available = list(range(1, NUMBER_COUNT + 1))
        selected: list[int] = []

        while available and len(selected) < ticket_size:
            weights = [state_vector[number - 1] ** 2 + 1e-9 for number in available]
            chosen = self.rng.choices(available, weights=weights, k=1)[0]
            selected.append(chosen)
            available.remove(chosen)

        if len(selected) != ticket_size:
            raise ValueError("Nao foi possivel medir dezenas suficientes.")

        return sorted(selected)
