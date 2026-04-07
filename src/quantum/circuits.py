from src.quantum.encodings import NUMBER_COUNT, STATE_VECTOR_SIZE


class QuantumCircuitSimulator:
    """Aplica uma simulacao simples de fase e difusao sobre o estado."""

    def __init__(
        self,
        phase_strength: float = 0.25,
        diffusion_strength: float = 0.15,
        iterations: int = 2,
    ) -> None:
        self.phase_strength = phase_strength
        self.diffusion_strength = diffusion_strength
        self.iterations = iterations

    def evolve(
        self,
        state_vector: list[float],
        last_draw_numbers: set[int],
    ) -> list[float]:
        evolved = state_vector[:]
        for _ in range(self.iterations):
            evolved = self._apply_phase_oracle(evolved, last_draw_numbers)
            evolved = self._apply_diffusion(evolved)
        return _normalize(evolved)

    def _apply_phase_oracle(
        self,
        state_vector: list[float],
        last_draw_numbers: set[int],
    ) -> list[float]:
        transformed = state_vector[:]
        for number in range(1, NUMBER_COUNT + 1):
            index = number - 1
            if number in last_draw_numbers:
                transformed[index] *= 1.0 + self.phase_strength
            else:
                transformed[index] *= 1.0 - (self.phase_strength / 2)
        return _normalize(transformed)

    def _apply_diffusion(self, state_vector: list[float]) -> list[float]:
        active = state_vector[:NUMBER_COUNT]
        average = sum(active) / len(active)
        mixed = [
            (1.0 - self.diffusion_strength) * value
            + self.diffusion_strength * average
            for value in active
        ]
        return _normalize(mixed + [0.0] * (STATE_VECTOR_SIZE - NUMBER_COUNT))


def _normalize(values: list[float]) -> list[float]:
    norm = sum(value * value for value in values) ** 0.5
    if norm == 0:
        return values
    return [value / norm for value in values]
