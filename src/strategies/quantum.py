import random

from src.core.models import Draw, Ticket
from src.quantum.adapters import QuantumSimulatorAdapter
from src.quantum.circuits import QuantumCircuitSimulator
from src.quantum.encodings import QuantumStateEncoder
from src.quantum.samplers import QuantumMeasurementSampler


class QuantumSimulatorStrategy:
    """Estrategia baseada em um simulador quantico leve sobre 5 qubits."""

    def __init__(
        self,
        history_draws: list[Draw],
        rng: random.Random | None = None,
        ticket_size: int = 15,
        decay_alpha: float = 0.08,
        phase_strength: float = 0.25,
        diffusion_strength: float = 0.15,
        iterations: int = 2,
    ) -> None:
        if not history_draws:
            raise ValueError("history_draws nao pode ser vazio.")
        if not 15 <= ticket_size <= 20:
            raise ValueError("ticket_size deve estar entre 15 e 20.")

        self.history_draws = history_draws
        self.ticket_size = ticket_size
        self.rng = rng or random.Random()
        self.encoder = QuantumStateEncoder(decay_alpha=decay_alpha)
        self.circuit = QuantumCircuitSimulator(
            phase_strength=phase_strength,
            diffusion_strength=diffusion_strength,
            iterations=iterations,
        )
        self.sampler = QuantumMeasurementSampler(rng=self.rng)
        self.adapter = QuantumSimulatorAdapter(
            encoder=self.encoder,
            circuit=self.circuit,
            sampler=self.sampler,
        )

    def generate_ticket(self) -> Ticket:
        numbers = self.adapter.run(
            history_draws=self.history_draws,
            ticket_size=self.ticket_size,
        )
        return Ticket(numbers=numbers)

    def generate_tickets(self, qtd: int) -> list[Ticket]:
        return [self.generate_ticket() for _ in range(qtd)]
