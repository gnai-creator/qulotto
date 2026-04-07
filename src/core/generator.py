

import random

from src.data.models import Ticket

def generate_random_ticket() -> Ticket:
    numbers = random.sample(range(1, 26), 15)
    return Ticket(numbers=numbers)