

def _validate_base_numbers(numbers: list[int]) -> list[int]:
    if len(set(numbers)) != len(numbers):
        raise ValueError("Os numeros nao podem se repetir.")

    if any(num < 1 or num > 25 for num in numbers):
        raise ValueError("Os numeros devem estar entre 1 e 25.")

    return sorted(numbers)


def validate_ticket_numbers(numbers: list[int]) -> list[int]:
    """Valida uma aposta da Lotofacil, permitindo de 15 a 20 numeros."""
    if not 15 <= len(numbers) <= 20:
        raise ValueError("A aposta deve conter entre 15 e 20 numeros.")
    return _validate_base_numbers(numbers)


def validate_draw_numbers(numbers: list[int]) -> list[int]:
    """Valida um resultado oficial da Lotofacil, sempre com 15 numeros."""
    if len(numbers) != 15:
        raise ValueError("O concurso deve conter exatamente 15 numeros.")
    return _validate_base_numbers(numbers)
