import random

from src.core.models import Draw, Ticket
from src.quantum.adapters import QuantumBackendAdapter
from src.quantum.circuits import QuantumCircuitBuilder
from src.quantum.encodings import QuantumFeatureEncoder
from src.quantum.samplers import QuantumSampler


class QuantumInspiredStrategy:
    """Estrategia probabilistica inspirada em amplitudes e interferencia."""

    def __init__(
        self,
        history_draws: list[Draw],
        rng: random.Random | None = None,
        ticket_size: int = 15,
        decay_alpha: float = 0.08,
        recent_boost: float = 0.20,
        odd_even_bias: float = 0.05,
    ) -> None:
        if not history_draws:
            raise ValueError("history_draws nao pode ser vazio.")
        if not 15 <= ticket_size <= 20:
            raise ValueError("ticket_size deve estar entre 15 e 20.")

        self.history_draws = history_draws
        self.ticket_size = ticket_size
        self.rng = rng or random.Random()
        self.encoder = QuantumFeatureEncoder(decay_alpha=decay_alpha)
        self.circuit_builder = QuantumCircuitBuilder(
            recent_boost=recent_boost,
            odd_even_bias=odd_even_bias,
        )
        self.sampler = QuantumSampler(rng=self.rng)
        self.backend = QuantumBackendAdapter(
            encoder=self.encoder,
            circuit_builder=self.circuit_builder,
            sampler=self.sampler,
        )

    def generate_ticket(self) -> Ticket:
        numbers = self.backend.run(
            history_draws=self.history_draws,
            ticket_size=self.ticket_size,
        )
        return Ticket(numbers=numbers)

    def generate_tickets(self, qtd: int) -> list[Ticket]:
        return [self.generate_ticket() for _ in range(qtd)]
