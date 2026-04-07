import sys
from time import sleep

import requests

from src.data.loaders import fetch_lotofacil_raw_result, parse_lotofacil_draw
from src.data.repository import (
    get_last_processed_contest,
    save_processed_draw,
    save_raw_draw,
)


REQUEST_PAUSE_SECONDS = 10


def main() -> int:
    """Busca concursos novos e retorna 0 em fim normal ou 1 em erro transitório."""
    last_draw = get_last_processed_contest()
    next_draw = 1 if last_draw in (0, None) else last_draw + 1

    while True:
        try:
            raw_result = fetch_lotofacil_raw_result(next_draw)
            result = parse_lotofacil_draw(raw_result)
            print(f"Fetched draw {next_draw}: {result.numbers}")
            save_raw_draw(raw_result, draw_number=next_draw)
            save_processed_draw(result, draw_number=next_draw)
            next_draw += 1
            sleep(REQUEST_PAUSE_SECONDS)
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code == 404:
                print(
                    f"Concurso {next_draw} ainda nao disponivel. "
                    "Atualizacao concluida com sucesso."
                )
                return 0
            print(f"HTTP error occurred: {exc}")
            return 1
        except requests.RequestException as exc:
            print(f"Request error occurred: {exc}")
            return 1
        except Exception as exc:
            print(f"An error occurred: {exc}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
