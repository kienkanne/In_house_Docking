from pathlib import Path
import shutil

from docking.workflows.charge_preparation import ChargeReceptorWorkflow, ChargeLigandWorkflow
from docking.workflows.vina_box_generation import VinaBoxWorkflow
from docking.wrappers.vina_tools import PrepareLigandWrapper, PrepareReceptorWrapper, VinaWrapper
from docking.config_schema import RootConfig
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

            prepare_ligand_wrapper = PrepareLigandWrapper(
                binary_path=self.cfg.libs.prepare_ligand,
                working_dir=self.working_dir,
                input_file=charged_ligand
            )
            prepared_ligand = central_run_stage(
                logs,
                f"Prepare Ligand {ligand.name}",
                prepare_ligand_wrapper.run,
            )

            vina_wrapper = VinaWrapper(
                binary_path=self.cfg.libs.vina,
                working_dir=self.working_dir,
                receptor=prepared_receptor,
                ligand=prepared_ligand,
                configs=vina_config
            )
            docking_result, log_file = central_run_stage(
                logs,
                f"Dock Vina {ligand.name}",
                vina_wrapper.run,
            )
            docking_results.append(docking_result)
            log_files.append(log_file)

        self.cfg.common.results_dir.mkdir(parents=True, exist_ok=True)
        
        selected_copy = [result for result in docking_results] + [log for log in log_files] + [
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
            print (dst)
            shutil.copy2(src, dst)

        logger, manifest, _ = logs
        manifest.finalize(success=True)
        logger.info("Vina pipeline completed")

        return None
