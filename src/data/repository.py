
import json
import csv
from pathlib import Path
from src.core.models import Draw

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

def ensure_data_dir() -> None:
    """Ensures that the data directories exist."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
def save_raw_draw(payload: dict, draw_number: int) -> Path:
    """Saves the raw draw data to a JSON file."""
    ensure_data_dir()
    filename = RAW_DIR / f"lotofacil_draw_{draw_number:04d}.json"
    filename.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return filename
    
def save_processed_draw(draw: Draw, draw_number: int) -> Path:
    """Saves the processed draw data to a CSV file."""
    ensure_data_dir()
    filename = PROCESSED_DIR / f"lotofacil_draws.csv"
    
    # Check if the file exists to determine if we need to write the header
    file_exists = filename.exists()
    with filename.open("a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["contest", "numbers"])
        writer.writerow([draw.contest, ",".join(map(str, draw.numbers))])
    return filename


def get_last_processed_contest() -> int:
    """Returns the last processed contest number from the CSV file."""
    filename = PROCESSED_DIR / "lotofacil_draws.csv"
    if not filename.exists():
        return 0
    
    with filename.open("r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        last_row = None
        for row in reader:
            last_row = row
        if last_row:
            return int(last_row[0])
    
    return 0

def load_draws_from_csv() -> list[Draw]:
    """Loads all processed draws from the CSV file."""
    filename = PROCESSED_DIR / "lotofacil_draws.csv"
    if not filename.exists():
        return []
    
    draws: list[Draw] = []
    with filename.open("r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            contest = int(row[0])
            numbers = list(map(int, row[1].split(",")))
            draws.append(Draw(contest=contest, numbers=numbers))
    
    return draws

def load_latest_draw_from_csv() -> Draw | None:
    """Loads the latest processed draw from the CSV file."""
    filename = PROCESSED_DIR / "lotofacil_draws.csv"
    if not filename.exists():
        return None
    
    with filename.open("r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        last_row = None
        for row in reader:
            last_row = row
        if last_row:
            contest = int(last_row[0])
            numbers = list(map(int, last_row[1].split(",")))
            return Draw(contest=contest, numbers=numbers)
    
    return None

def load_draw_by_contest_from_csv(contest_number: int) -> Draw | None:
    """Loads a specific draw by contest number from the CSV file."""
    filename = PROCESSED_DIR / "lotofacil_draws.csv"
    if not filename.exists():
        return None
    
    with filename.open("r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            contest = int(row[0])
            if contest == contest_number:
                numbers = list(map(int, row[1].split(",")))
                return Draw(contest=contest, numbers=numbers)
    
    return None
