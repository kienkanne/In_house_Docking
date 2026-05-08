import logging
from pathlib import Path
import sys

from docking.workflows.charge_preparation import ChargeReceptorWorkflow, ChargeLigandWorkflow 
from docking.wrappers.dock6_tools import WriteDMSWrapper, SphgenDefaultWrapper, SphereSelectorDefaultWrapper, ShowboxDefaultWrapper, GridDefaultWrapper
from docking.workflows.dock6_preparation import Dock6Preparation
from docking.wrappers.dock6_generate_site import generate_site
from docking.config_schema import RootConfig, load_config

class OrchestratorDock6:
    def __init__(self, cfg: RootConfig, working_dir):
        self.cfg = cfg
        self.working_dir = working_dir

    def run(self):

        # Charge receptor and ligand
        charge_receptor_workflow = ChargeReceptorWorkflow(self.cfg, self.working_dir, output_type="mol2", noH=True)
        charged_receptor, noH_receptor = charge_receptor_workflow.run()

        charge_ligand_workflow = ChargeLigandWorkflow(self.cfg, self.working_dir, output_type="mol2")
        charged_ligand = charge_ligand_workflow.run()

        # Generate the charged receptor pdb file for pymol
        # Feeding pymol with mol2 files with charges seems to cause issues

        charged_receptor_pdb_workflow = ChargeReceptorWorkflow(self.cfg, self.working_dir, output_type="pdb", noH=True)
        charged_receptor_pdb, _ = charged_receptor_pdb_workflow.run()

        # Write DMS file for receptor
        write_dms = WriteDMSWrapper(working_dir=self.working_dir, noH_receptor=noH_receptor)
        write_dms.run()

        # Generate spheres
        sphgen_wrapper = SphgenDefaultWrapper(binary_path=self.cfg.libs.sphgen, working_dir=self.working_dir)
        sphgen_wrapper.run()

        # Generate binding site mol2
        # Empty for now, returns binding_site.mol2 in the working dir
        generate_site(
            self.working_dir / charged_receptor_pdb,
            self.cfg.dock6.residue_selection,
            self.working_dir / "binding_site.mol2"
        )

        # Select spheres
        sphere_selector_wrapper = SphereSelectorDefaultWrapper(self.cfg.libs.sphere_selector, self.working_dir, self.cfg.dock6.radius)
        sphere_selector_wrapper.run()

        # Generate box
        showbox_wrapper = ShowboxDefaultWrapper(self.cfg.libs.showbox, self.working_dir, self.cfg.dock6.padding)
        showbox_wrapper.run()

        # Generate grid
        grid_wrapper = GridDefaultWrapper(self.cfg.libs.grid, self.working_dir, charged_receptor)
        grid_wrapper.run()
  
        # Run Dock6
        dock6_wrapper = Dock6Preparation(
            cfg=self.cfg,
            working_dir=self.working_dir,
            charged_receptor=charged_receptor,
            charged_ligand=charged_ligand
        )
        docking_results = dock6_wrapper.run()
        return docking_results

# test:
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        stream=sys.stdout,
    )
    cfg = load_config("configs/docking_config.yaml")
    workflow = OrchestratorDock6(cfg, Path("/home/kbui/SARS_COV_2/data"))
    workflow.run()