from src.core.models import Draw
from src.quantum.circuits import QuantumCircuitSimulator
from src.quantum.encodings import QuantumStateEncoder
from src.quantum.samplers import QuantumMeasurementSampler


class QuantumSimulatorAdapter:
    """Encapsula encoder, circuito e medicao para a estrategia quantica."""

    def __init__(
        self,
        encoder: QuantumStateEncoder,
        circuit: QuantumCircuitSimulator,
        sampler: QuantumMeasurementSampler,
    ) -> None:
        self.encoder = encoder
        self.circuit = circuit
        self.sampler = sampler

    def run(self, history_draws: list[Draw], ticket_size: int) -> list[int]:
        encoded_state = self.encoder.encode(history_draws)
        evolved_state = self.circuit.evolve(
            state_vector=encoded_state,
            last_draw_numbers=set(history_draws[-1].numbers),
        )
        return self.sampler.sample(
            state_vector=evolved_state,
            ticket_size=ticket_size,
        )
