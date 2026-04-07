

import random

from src.core.models import Ticket

def generate_random_ticket() -> Ticket:
    numbers = random.sample(range(1, 26), 15)
    return Ticket(numbers=numbers)
