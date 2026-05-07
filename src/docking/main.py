import logging
import sys

from docking.workflows.charge_preparation import ChargeLigandWorkflow, ChargeReceptorWorkflow
from docking.config_schema import RootConfig
from docking.config_schema import load_config

class Main:
    def __init__(self, config: RootConfig):
        self.config = config

    def run(self):
        charge_receptor_workflow = ChargeReceptorWorkflow(self.config, "scratch/")
        charge_receptor_workflow.run()

    def run2(self):
        # Example of running a different workflow
        charge_ligand_workflow = ChargeLigandWorkflow(self.config, "scratch/")
        charge_ligand_workflow.run()

if __name__ == "__main__":
    # Enable logging so ShellWrapper and other loggers emit to stdout
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        stream=sys.stdout,
    )

    cfg = load_config("configs/docking_config.yaml")
    Main(cfg).run2()