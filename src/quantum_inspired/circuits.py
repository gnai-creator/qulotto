class QuantumCircuitBuilder:
    """Aplica um operador simples de interferencia sobre amplitudes classicas."""

    def __init__(
        self,
        recent_boost: float = 0.20,
        odd_even_bias: float = 0.05,
    ) -> None:
        self.recent_boost = recent_boost
        self.odd_even_bias = odd_even_bias

    def build(
        self,
        amplitudes: dict[int, float],
        last_draw_numbers: set[int],
    ) -> dict[int, float]:
        transformed = dict(amplitudes)

        for number in transformed:
            if number in last_draw_numbers:
                transformed[number] *= 1.0 + self.recent_boost

            if number % 2 == 0:
                transformed[number] *= 1.0 + self.odd_even_bias
            else:
                transformed[number] *= 1.0 - self.odd_even_bias

        norm = sum(value * value for value in transformed.values()) ** 0.5
        if norm == 0:
            return {number: 1 / (25 ** 0.5) for number in range(1, 26)}

        return {
            number: value / norm
            for number, value in transformed.items()
        }
