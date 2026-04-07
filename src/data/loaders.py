

import requests

from src.core.models import Draw

def fetch_lotofacil_result(draw_number: int) -> Draw:
    """Fetches the latest Lotofácil results from the official website."""
    
    payload = fetch_lotofacil_raw_result(draw_number)

    
    return parse_lotofacil_draw(payload)

def fetch_lotofacil_raw_result(draw_number: int) -> dict:
    """Fetches the raw Lotofácil results from the official website."""
    
    url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{draw_number}"
    
    response = requests.get(url,  timeout=30)
    response.raise_for_status()
    
    return response.json()


def parse_lotofacil_draw(payload: dict) -> Draw:
    """Parses the raw Lotofácil draw data into a Draw object."""
    return Draw(
        contest=int(payload["numero"]),
        numbers=[int(num) for num in payload["listaDezenas"]]
    )
