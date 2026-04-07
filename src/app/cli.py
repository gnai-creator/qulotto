import argparse

from src.app.config import (
    AVAILABLE_STRATEGIES,
    DEFAULT_BET_SIZES,
    DEFAULT_FIM,
    DEFAULT_HISTORY,
    DEFAULT_INICIO,
    DEFAULT_PRESET_NAMES,
    DEFAULT_QTD,
    DEFAULT_SEED,
    DEFAULT_SEED_COUNT,
    DEFAULT_STRATEGY,
    STATISTICAL_PRESETS,
)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--qtd",
        type=int,
        default=DEFAULT_QTD,
        help="Quantidade de jogos a gerar",
    )
    parser.add_argument(
        "--tamanho-aposta",
        type=int,
        default=None,
        help="Quantidade de dezenas por aposta, entre 15 e 20",
    )
    parser.add_argument(
        "--tamanhos-aposta",
        nargs="*",
        type=int,
        default=DEFAULT_BET_SIZES,
        help="Lista de tamanhos de aposta para a bateria completa",
    )
    parser.add_argument(
        "--concurso",
        type=int,
        help="Numero do concurso a usar",
    )
    parser.add_argument(
        "--estrategia",
        type=str,
        choices=AVAILABLE_STRATEGIES,
        default=DEFAULT_STRATEGY,
        help="Estrategia para gerar jogos",
    )
    parser.add_argument(
        "--presets",
        nargs="*",
        choices=sorted(STATISTICAL_PRESETS.keys()),
        default=DEFAULT_PRESET_NAMES,
        help="Presets estatisticos para comparar no relatorio",
    )
    parser.add_argument(
        "--history",
        type=int,
        default=DEFAULT_HISTORY,
        help="Quantidade de concursos passados para a estrategia estatistica",
    )
    parser.add_argument(
        "--inicio",
        type=int,
        default=DEFAULT_INICIO,
    )
    parser.add_argument(
        "--fim",
        type=int,
        default=DEFAULT_FIM,
    )
    parser.add_argument(
        "--backtest",
        action="store_true",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Seed para execucoes reproduziveis",
    )
    parser.add_argument(
        "--seed-count",
        type=int,
        default=DEFAULT_SEED_COUNT,
        help="Quantidade de seeds consecutivas para rodar em cada experimento",
    )
    parser.add_argument(
        "--completo",
        action="store_true",
        help="Roda a bateria completa com todos os presets e tamanhos de aposta",
    )
    parser.add_argument(
        "--future",
        action="store_true",
        help="Gera apenas palpites para o proximo concurso, sem backtest",
    )
    return parser.parse_args()
