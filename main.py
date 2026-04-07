
from src.core.generator import generate_random_ticket
from src.core.scoring import count_hits
from src.data.models import Draw

def main() -> None:
    draw = Draw(contest=1,numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    ticket = generate_random_ticket()
    hits = count_hits(ticket, draw)
    print(f"Draw: {draw.numbers}")
    print(f"Ticket: {ticket.numbers}")
    print(f"Hits: {hits}")

if __name__ == "__main__":
    main()