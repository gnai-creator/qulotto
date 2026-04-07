
from dataclasses import dataclass
from src.core.validation import validate_numbers

@dataclass(frozen=True)
class Ticket:
    numbers: list[int]
    
    def __post_init__(self) -> None:
        validated = validate_numbers(self.numbers)
        object.__setattr__(self, 'numbers', validated)

@dataclass(frozen=True)
class Draw:
    contest: int
    numbers: list[int]
    
    def __post_init__(self) -> None:
        validated = validate_numbers(self.numbers)
        object.__setattr__(self, 'numbers', validated)