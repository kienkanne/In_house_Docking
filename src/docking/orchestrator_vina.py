from pathlib import Path
import shutil

from docking.workflows.charge_preparation import ChargeReceptorWorkflow
from docking.workflows.parallel_ligand_docking import ParallelLigandDockingWorkflow
from docking.workflows.vina_box_generation import VinaBoxWorkflow
from docking.wrappers.vina_tools import PrepareReceptorWrapper
from docking.config_schema import RootConfig
from docking.summary.vina import write_vina_summary
from docking.utils.central_logging import setup_all_logs, central_run_stage
from docking.utils.ligands import load_ligand_csv


class OrchestratorVina:
    def __init__(self, cfg: RootConfig):
        self.cfg = cfg
        self.working_dir = Path(cfg.common.working_dir)

    def run(self):
        self.working_dir.mkdir(parents=True, exist_ok=True)
        logs = setup_all_logs(
            "vina_docking",
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

        charge_receptor_workflow = ChargeReceptorWorkflow(self.cfg, self.working_dir)
        charged_receptor = central_run_stage(logs, "Charge Receptor", charge_receptor_workflow.run)

        prepare_receptor_wrapper = PrepareReceptorWrapper(
            binary_path=self.cfg.libs.prepare_receptor,
            working_dir=self.working_dir,
            input_file=charged_receptor
        )
        prepared_receptor = central_run_stage(logs, "Prepare Receptor", prepare_receptor_wrapper.run)

        vina_box_workflow = VinaBoxWorkflow(self.cfg, self.working_dir, prepared_receptor)
        vina_config, vina_box = central_run_stage(logs, "Generate Vina Box", vina_box_workflow.run)

        vina_cpu = max(1, int(self.cfg.vina.cpu or 1))
        jobs = max(1, int(self.cfg.common.total_cpu) // vina_cpu)
        parallel_workflow = ParallelLigandDockingWorkflow(
            self.cfg,
            self.working_dir,
            engine="vina",
            ligands=ligands,
            jobs=jobs,
            prepared_receptor=prepared_receptor,
            vina_config=vina_config,
        )
        docking_results, log_files = central_run_stage(
            logs,
            "Dock Vina Ligands",
            parallel_workflow.run,
            checkpoint=False,
        )
        
        self.cfg.common.results_dir.mkdir(parents=True, exist_ok=True)
        Path(self.cfg.common.results_dir / "raw").mkdir(parents=True, exist_ok=True)
        

        # results and logs are copied to results/raw/ for easier access and debugging
        for file in docking_results + log_files:
            src = self.working_dir / file
            dst = self.cfg.common.results_dir / "raw" / file
            shutil.copy2(src, dst)

        selected_copy = [
            prepared_receptor,
            vina_config, 
            vina_box,
            "run.log",
            "manifest.json",
            "state.json"
        ]

        for file in selected_copy:
            src = self.working_dir / file
            dst = self.cfg.common.results_dir / file
            shutil.copy2(src, dst)

        central_run_stage(
            logs,
            "Write Vina Summary",
            write_vina_summary,
            self.cfg.common.results_dir,
            self.cfg.common.receptor,
            self.cfg.common.max_poses,
            checkpoint=False,
        )

        logger, manifest, _ = logs
        manifest.finalize(success=True)
        logger.info("Vina pipeline completed")

        return None
