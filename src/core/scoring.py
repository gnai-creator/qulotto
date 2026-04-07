from src.data.models import Draw, Ticket


def count_hits(ticket: Ticket, draw: Draw) -> int:
    """Conta o número de acertos entre o bilhete e o resultado do sorteio."""
    return len(set(ticket.numbers) & set(draw.numbers))