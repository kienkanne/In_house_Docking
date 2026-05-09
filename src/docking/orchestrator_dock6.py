from pathlib import Path
import shutil

from docking.workflows.charge_preparation import ChargeReceptorWorkflow, ChargeLigandWorkflow 
from docking.wrappers.dock6_tools import WriteDMSWrapper, SphgenDefaultWrapper, SphereSelectorDefaultWrapper, ShowboxDefaultWrapper, GridDefaultWrapper
from docking.workflows.dock6_preparation import Dock6Preparation
from docking.wrappers.dock6_generate_site import generate_site
from docking.config_schema import RootConfig
from docking.utils.central_logging import setup_all_logs, central_run_stage
from docking.utils.ligands import load_ligand_csv

class OrchestratorDock6:
    def __init__(self, cfg: RootConfig):
        self.cfg = cfg
        self.working_dir = Path(cfg.common.working_dir)

    def run(self):
        self.working_dir.mkdir(parents=True, exist_ok=True)
        logs = setup_all_logs(
            "dock6_docking",
            self.working_dir / "run.log",
            self.working_dir / "manifest.json",
            self.working_dir / "state.json",
        )

        ligands = central_run_stage(
            logs,
            "Validate Ligands",
            load_ligand_csv,
            self.cfg.common.ligand,
            self.cfg.libs.obabel,
            self.working_dir,
            checkpoint=False,
        )

        charge_receptor_workflow = ChargeReceptorWorkflow(self.cfg, self.working_dir, dock6=True)
        charged_receptor, noH_receptor, noH_receptor_pdb = central_run_stage(
            logs,
            "Charge Receptor",
            charge_receptor_workflow.run,
        )

        write_dms = WriteDMSWrapper(working_dir=self.working_dir, noH_receptor=noH_receptor)
        central_run_stage(logs, "Write DMS", write_dms.run)

        sphgen_wrapper = SphgenDefaultWrapper(binary_path=self.cfg.libs.sphgen, working_dir=self.working_dir)
        central_run_stage(logs, "Generate Spheres", sphgen_wrapper.run)

        central_run_stage(
            logs,
            "Generate Binding Site",
            generate_site,
            self.working_dir / noH_receptor_pdb,
            self.cfg.dock6.residue_selection,
            self.working_dir / "binding_site.mol2",
        )

        sphere_selector_wrapper = SphereSelectorDefaultWrapper(self.cfg.libs.sphere_selector, self.working_dir, self.cfg.dock6.radius)
        central_run_stage(logs, "Select Spheres", sphere_selector_wrapper.run)

        showbox_wrapper = ShowboxDefaultWrapper(self.cfg.libs.showbox, self.working_dir, self.cfg.dock6.padding)
        central_run_stage(logs, "Generate Box", showbox_wrapper.run)

        grid_wrapper = GridDefaultWrapper(self.cfg.libs.grid, self.working_dir, charged_receptor)
        central_run_stage(logs, "Generate Grid", grid_wrapper.run)
  
        docking_results = []
        log_files = []

        for ligand in ligands:
            charge_ligand_workflow = ChargeLigandWorkflow(
                self.cfg,
                self.working_dir,
                output_type="mol2",
                ligand=ligand.smiles,
                ligand_name=ligand.name,
            )
            charged_ligand = central_run_stage(
                logs,
                f"Charge Ligand {ligand.name}",
                charge_ligand_workflow.run,
            )

            dock6_wrapper = Dock6Preparation(
                cfg=self.cfg,
                working_dir=self.working_dir,
                charged_receptor=charged_receptor,
                charged_ligand=charged_ligand
            )
            docking_result, log_file = central_run_stage(
                logs,
                f"Dock DOCK6 {ligand.name}",
                dock6_wrapper.run,
            )
            docking_results.append(docking_result)
            log_files.append(log_file)

        self.cfg.common.results_dir.mkdir(parents=True, exist_ok=True)

        selected_copy = [result for result in docking_results] + [log for log in log_files] + [
            charged_receptor,
            "rec_box.pdb",
            "run.log",
            "manifest.json",
            "state.json"
        ]

        for file in selected_copy:
            src = self.working_dir / file
            dst = self.cfg.common.results_dir / file
            print (dst)
            shutil.copy2(src, dst)

        logger, manifest, _ = logs
        manifest.finalize(success=True)
        logger.info("DOCK6 pipeline completed")

        return docking_results
