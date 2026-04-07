from src.core.models import Ticket


class QuantumInspiredStrategy:
    """Placeholder para a futura estrategia inspirada em computacao quantica."""

    def __init__(self) -> None:
        self.name = "quantum_inspired"

    def generate_ticket(self) -> Ticket:
        raise NotImplementedError(
            "QuantumInspiredStrategy ainda nao foi implementada."
        )

    def generate_tickets(self, qtd: int) -> list[Ticket]:
        raise NotImplementedError(
            "QuantumInspiredStrategy ainda nao foi implementada."
        )
