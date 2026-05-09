import argparse
from docking.cli.common import add_config_arg
from docking.config_schema import load_config
from docking.orchestrator_vina import OrchestratorVina

def main():
    parser = argparse.ArgumentParser(prog="docking", description="Docking CLI for SARS-CoV-2 project")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run command
    run_parser = subparsers.add_parser("run_vina", help="Full vina docking pipeline")
    add_config_arg(run_parser)

    # run command
    run_parser = subparsers.add_parser("run_dock6", help="Full dock6 docking pipeline")
    add_config_arg(run_parser)

    args = parser.parse_args()

    if args.command == "run_vina":
        from docking.orchestrator_vina import OrchestratorVina

        cfg = load_config(args.config)
        OrchestratorVina(cfg).run()

    elif args.command == "run_dock6":
        from docking.orchestrator_dock6 import OrchestratorDock6

        cfg = load_config(args.config)
        OrchestratorDock6(cfg).run()
