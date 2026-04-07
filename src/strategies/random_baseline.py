import random

from src.core.models import Ticket


class RandomBaselineStrategy:
    def __init__(
        self,
        rng: random.Random | None = None,
        ticket_size: int = 15,
    ) -> None:
        self.rng = rng or random.Random()
        self.ticket_size = ticket_size

    def generate_ticket(self) -> Ticket:
        numbers = self.rng.sample(range(1, 26), self.ticket_size)
        return Ticket(numbers=numbers)
    
    def generate_tickets(self, qtd: int) -> list[Ticket]:
        return [self.generate_ticket() for _ in range(qtd)]
