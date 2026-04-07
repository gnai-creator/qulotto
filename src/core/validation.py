

def validate_numbers(numbers: list[int]) -> list[int]:
    """Valida a lista de números, garantindo que sejam únicos e estejam entre 1 e 25."""
    
    if len(numbers) != 15:
        raise ValueError("O bilhete deve conter exatamente 15 números.")
    
    if len(set(numbers)) != 15:
        raise ValueError("Os números do bilhete devem ser únicos.")
    
    if any(num < 1 or num > 25 for num in numbers):
        raise ValueError("Os números do bilhete devem estar entre 1 e 25.")
    
    return sorted(numbers)