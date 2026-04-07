from pathlib import Path


REPORT_DIR = Path("docs/report")

DEFAULT_QTD = 10
DEFAULT_BET_SIZE = 15
DEFAULT_BET_SIZES = [15, 16]
DEFAULT_HISTORY = 50
DEFAULT_INICIO = 100
DEFAULT_FIM = 100
DEFAULT_SEED = 42
DEFAULT_SEED_COUNT = 1
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

AVAILABLE_STRATEGIES = [
    "random",
    "statistical",
    "intentionality_vector",
    "quantum",
]
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

DEFAULT_PRESET_NAMES = ["balanced"]
FULL_PRESET_NAMES = list(STATISTICAL_PRESETS.keys())
FULL_BET_SIZES = [15, 16, 17, 18, 19, 20]
LOTOFACIL_BET_COSTS = {
    15: 3.50,
    16: 56.00,
    17: 476.00,
    18: 2856.00,
    19: 13566.00,
    20: 54264.00,
}


def _minimum_feasible_max_consecutive_run(ticket_size: int) -> int:
    missing_numbers = 25 - ticket_size
    available_blocks = missing_numbers + 1
    return (ticket_size + available_blocks - 1) // available_blocks


def _minimum_feasible_repeats_from_last_draw(ticket_size: int) -> int:
    return max(0, ticket_size - 10)


def _recommended_max_consecutive_run_floor(ticket_size: int) -> int:
    if ticket_size >= 19:
        return 4
    return _minimum_feasible_max_consecutive_run(ticket_size)


def _recommended_max_repeats_from_last_draw_floor(ticket_size: int) -> int:
    if ticket_size >= 20:
        return 13
    if ticket_size >= 19:
        return 10
    return _minimum_feasible_repeats_from_last_draw(ticket_size)


def build_statistical_preset(preset_name: str, ticket_size: int) -> dict:
    if preset_name not in STATISTICAL_PRESETS:
        raise ValueError(f"Preset desconhecido: {preset_name}")

    preset = dict(STATISTICAL_PRESETS[preset_name])
    preset["ticket_size"] = ticket_size
    preset["min_even_numbers"] = max(6, ticket_size - 9)
    preset["max_even_numbers"] = min(12, ticket_size - 6)
    preset["max_consecutive_run"] = max(
        preset["max_consecutive_run"],
        _recommended_max_consecutive_run_floor(ticket_size),
    )
    preset["max_repeats_from_last_draw"] = max(
        preset["max_repeats_from_last_draw"],
        _recommended_max_repeats_from_last_draw_floor(ticket_size),
    )
    return preset
