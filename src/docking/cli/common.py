import argparse
from pathlib import Path

def add_config_arg(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to config YAML file",
    )
    return parser