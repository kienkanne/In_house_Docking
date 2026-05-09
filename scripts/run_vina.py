#!/usr/bin/env python3

import sys
from pathlib import Path

from docking.config_schema import load_config
from docking.orchestrator_vina import OrchestratorVina


def main():
    config_path = Path(__file__).resolve().parents[1] / "configs" / "docking_config.yaml"
    cfg = load_config(config_path)
    OrchestratorVina(cfg).run()


if __name__ == "__main__":
    sys.exit(main())
