import requests
from time import sleep
from src.core.models import Draw
from src.data.loaders import fetch_lotofacil_result, fetch_lotofacil_raw_result
from src.data.repository import save_raw_draw, save_processed_draw, get_last_processed_contest

def main() -> None:
    """Fetches the latest Lotofácil results and saves them to a local file."""
    
    last_draw = get_last_processed_contest()  # Replace with the desired draw number
    next_draw = 1 if last_draw == 0 or last_draw is None else last_draw + 1
    
    raw_result :dict = {}
    list_of_results :list[Draw] = []
    list_of_raw_results :list[dict] = []    

    while True:
        try:
            raw_result = fetch_lotofacil_raw_result(next_draw)
            result = fetch_lotofacil_result(next_draw)
            print(f"Fetched draw {next_draw}: {result.numbers}")
            save_raw_draw(raw_result, draw_number=next_draw)
            save_processed_draw(result, draw_number=next_draw)
            next_draw += 1
        except requests.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break
        sleep(10)  # Sleep to avoid hitting the server too hard
           

if __name__ == "__main__":
    main()
