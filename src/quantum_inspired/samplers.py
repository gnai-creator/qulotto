import random


class QuantumSampler:
    """Amostra tickets a partir de amplitudes, usando probabilidade ao quadrado."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()

    def sample(self, amplitudes: dict[int, float], ticket_size: int) -> list[int]:
        available = list(amplitudes.keys())
        selected: list[int] = []

        while available and len(selected) < ticket_size:
            probabilities = [amplitudes[number] ** 2 + 1e-9 for number in available]
            chosen = self.rng.choices(available, weights=probabilities, k=1)[0]
            selected.append(chosen)
            available.remove(chosen)

        if len(selected) != ticket_size:
            raise ValueError("Nao foi possivel amostrar dezenas suficientes.")

        return sorted(selected)
