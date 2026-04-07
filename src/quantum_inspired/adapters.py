from src.core.models import Draw
from src.quantum_inspired.circuits import QuantumCircuitBuilder
from src.quantum_inspired.encodings import QuantumFeatureEncoder
from src.quantum_inspired.samplers import QuantumSampler


class QuantumBackendAdapter:
    """Encadeia encoding, interferencia e amostragem numa pipeline unica."""

    def __init__(
        self,
        encoder: QuantumFeatureEncoder,
        circuit_builder: QuantumCircuitBuilder,
        sampler: QuantumSampler,
    ) -> None:
        self.encoder = encoder
        self.circuit_builder = circuit_builder
        self.sampler = sampler

    def run(
        self,
        history_draws: list[Draw],
        ticket_size: int,
    ) -> list[int]:
        amplitudes = self.encoder.encode(history_draws)
        transformed_amplitudes = self.circuit_builder.build(
            amplitudes=amplitudes,
            last_draw_numbers=set(history_draws[-1].numbers),
        )
        return self.sampler.sample(
            amplitudes=transformed_amplitudes,
            ticket_size=ticket_size,
        )
