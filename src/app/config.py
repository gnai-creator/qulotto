from pathlib import Path


REPORT_DIR = Path("docs/report")

DEFAULT_QTD = 100
DEFAULT_BET_SIZE = 15
DEFAULT_BET_SIZES = [15, 16, 17, 18, 19, 20]
DEFAULT_HISTORY = 50
DEFAULT_INICIO = 100
DEFAULT_FIM = 200
DEFAULT_SEED = 42
DEFAULT_SEED_COUNT = 5
DEFAULT_FREQUENCY_WEIGHT = 0.45
DEFAULT_DELAY_WEIGHT = 0.35
DEFAULT_PARITY_WEIGHT = 0.10
DEFAULT_RANGE_WEIGHT = 0.10
DEFAULT_MIN_EVEN_NUMBERS = 6
DEFAULT_MAX_EVEN_NUMBERS = 9
DEFAULT_MIN_NUMBERS_PER_RANGE = 2
DEFAULT_MAX_CONSECUTIVE_RUN = 3
DEFAULT_MAX_REPEATS_FROM_LAST_DRAW = 11
DEFAULT_MAX_ATTEMPTS = 250

AVAILABLE_STRATEGIES = ["random", "statistical", "quantum"]
DEFAULT_STRATEGY = "random"

STATISTICAL_PRESETS = {
    "balanced": {
        "frequency_weight": 0.45,
        "delay_weight": 0.35,
        "parity_weight": 0.10,
        "range_weight": 0.10,
        "min_numbers_per_range": 2,
        "max_consecutive_run": 3,
        "max_repeats_from_last_draw": 11,
        "max_attempts": 250,
    },
    "frequency_heavy": {
        "frequency_weight": 0.60,
        "delay_weight": 0.20,
        "parity_weight": 0.10,
        "range_weight": 0.10,
        "min_numbers_per_range": 2,
        "max_consecutive_run": 3,
        "max_repeats_from_last_draw": 12,
        "max_attempts": 250,
    },
    "delay_heavy": {
        "frequency_weight": 0.20,
        "delay_weight": 0.55,
        "parity_weight": 0.10,
        "range_weight": 0.15,
        "min_numbers_per_range": 2,
        "max_consecutive_run": 3,
        "max_repeats_from_last_draw": 10,
        "max_attempts": 250,
    },
    "conservative_shape": {
        "frequency_weight": 0.35,
        "delay_weight": 0.30,
        "parity_weight": 0.15,
        "range_weight": 0.20,
        "min_numbers_per_range": 2,
        "max_consecutive_run": 2,
        "max_repeats_from_last_draw": 9,
        "max_attempts": 300,
    },
}

DEFAULT_PRESET_NAMES = list(STATISTICAL_PRESETS.keys())
LOTOFACIL_BET_COSTS = {
    15: 3.50,
    16: 56.00,
    17: 476.00,
    18: 2856.00,
    19: 13566.00,
    20: 54264.00,
}


def build_statistical_preset(preset_name: str, ticket_size: int) -> dict:
    if preset_name not in STATISTICAL_PRESETS:
        raise ValueError(f"Preset desconhecido: {preset_name}")

    preset = dict(STATISTICAL_PRESETS[preset_name])
    preset["ticket_size"] = ticket_size
    preset["min_even_numbers"] = max(6, ticket_size - 9)
    preset["max_even_numbers"] = min(12, ticket_size - 6)
    return preset
