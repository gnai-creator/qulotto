from collections import Counter

from src.core.models import Draw, Ticket

def media_de_acertos(draw: Draw, tickets: list[Ticket]) -> float:
    total_acertos = 0
    for ticket in tickets:
        acertos = len(set(ticket.numbers) & set(draw.numbers))
        total_acertos += acertos
    media = total_acertos / len(tickets) if tickets else 0
    return media

def porcentagem_de_acertos(draw: Draw, tickets: list[Ticket]) -> float:
    total_acertos = 0
    for ticket in tickets:
        acertos = len(set(ticket.numbers) & set(draw.numbers))
        total_acertos += acertos
    porcentagem = (total_acertos / (len(tickets) * len(draw.numbers))) * 100 if tickets else 0
    return porcentagem

def maior_numero_acertos(draw: Draw, tickets: list[Ticket]) -> int:
    max_acertos = 0
    for ticket in tickets:
        acertos = len(set(ticket.numbers) & set(draw.numbers))
        if acertos > max_acertos:
            max_acertos = acertos
    return max_acertos

def menor_numero_acertos(draw: Draw, tickets: list[Ticket]) -> int:
    min_acertos = float('inf')
    for ticket in tickets:
        acertos = len(set(ticket.numbers) & set(draw.numbers))
        if acertos < min_acertos:
            min_acertos = acertos
    return int(min_acertos) if min_acertos != float('inf') else 0

def distribuicao_de_acertos(draw: Draw, tickets: list[Ticket]) -> dict[int, int]:
    distribuicao = {i: 0 for i in range(len(draw.numbers) + 1)}
    for ticket in tickets:
        acertos = len(set(ticket.numbers) & set(draw.numbers))
        distribuicao[acertos] += 1
    return distribuicao

def sumario_de_acertos(hits_list: list[int]) -> dict:
    if not hits_list:
        raise ValueError("A lista de acertos não pode estar vazia.")
    
    distribution = dict(sorted(Counter(hits_list).items()))
    
    return {
        "total": len(hits_list),
        "media": sum(hits_list) / len(hits_list),
        "max": max(hits_list),
        "min": min(hits_list),
        "distribution": distribution
    }
