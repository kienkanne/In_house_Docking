import argparse
from docking.cli.common import add_config_arg
from docking.config_schema import load_config


def main():
    parser = argparse.ArgumentParser(prog="docking", description="Docking CLI for SARS-CoV-2 project")
    subparsers = parser.add_subparsers(dest="command", required=True)

    vina_parser = subparsers.add_parser("run_vina", help="Full Vina docking pipeline")
    add_config_arg(vina_parser)

    dock6_parser = subparsers.add_parser("run_dock6", help="Full DOCK6 docking pipeline")
    add_config_arg(dock6_parser)

    args = parser.parse_args()

    if args.command == "run_vina":
        from docking.orchestrator_vina import OrchestratorVina

        cfg = load_config(args.config)
        OrchestratorVina(cfg).run()

    elif args.command == "run_dock6":
        from docking.orchestrator_dock6 import OrchestratorDock6

        cfg = load_config(args.config)
        OrchestratorDock6(cfg).run()
