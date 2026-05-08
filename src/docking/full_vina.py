import logging
from pathlib import Path
import sys

from docking.workflows.charge_preparation import ChargeReceptorWorkflow, ChargeLigandWorkflow
from docking.workflows.vina_box_generation import VinaBoxWorkflow
from docking.wrappers.vina_tools import PrepareLigandWrapper, PrepareReceptorWrapper, VinaWrapper
from docking.config_schema import RootConfig, load_config


class FullVinaWorkFlow:
    def __init__(self, cfg: RootConfig, working_dir):
        self.cfg = cfg
        self.working_dir = working_dir

    def run(self):
        # Charge receptor and ligand
        charge_receptor_workflow = ChargeReceptorWorkflow(self.cfg, self.working_dir, output_type="pdb")
        charged_receptor = charge_receptor_workflow.run()

        charge_ligand_workflow = ChargeLigandWorkflow(self.cfg, self.working_dir, output_type="mol2")
        charged_ligand = charge_ligand_workflow.run()

        # Prepare receptor and ligand for Vina
        prepare_receptor_wrapper = PrepareReceptorWrapper(
            binary_path=self.cfg.libs.prepare_receptor,
            working_dir=self.working_dir,
            input_file=charged_receptor
        )
        prepared_receptor = prepare_receptor_wrapper.run()

        prepare_ligand_wrapper = PrepareLigandWrapper(
            binary_path=self.cfg.libs.prepare_ligand,
            working_dir=self.working_dir,
            input_file=charged_ligand
        )
        prepared_ligand = prepare_ligand_wrapper.run()

        # Gnerate Vina config
        vina_box_workflow = VinaBoxWorkflow(self.cfg, self.working_dir, prepared_receptor)
        vina_config = vina_box_workflow.run()

        # Run Vina docking
        vina_wrapper = VinaWrapper(
            binary_path=self.cfg.libs.vina,
            working_dir=self.working_dir,
            receptor=prepared_receptor,
            ligand=prepared_ligand,
            configs=vina_config
        )
        docking_results = vina_wrapper.run()

        return docking_results

#test:  

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        stream=sys.stdout,
    )
    cfg = load_config("configs/docking_config.yaml")
    workflow = FullVinaWorkFlow(cfg, Path("/home/kbui/SARS_COV_2/data"))
    workflow.run()