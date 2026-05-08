from pathlib import Path
from string import Template
import os

from docking.wrappers.common_prep import ChimeraXWrapper, ObabelWrapper


class ChargeReceptorWorkflow: 
    def __init__(self, cfg, working_dir) -> Path:
        self.cfg = cfg
        self.working_dir = working_dir
        with open(Path(__file__).resolve().parents[1] / "templates" / "charge_receptor_template.com") as f:
            self.charge_receptor_template = f.read()

    def run(self):
        receptor = self.cfg.common.receptor
        name = os.path.basename(receptor).split('.')[0]
        name = f"{name}_charged.pdb"

        stdin = Template(self.charge_receptor_template).substitute(
            receptor=receptor,
            name=name
            )

        chimerax_wrapper = ChimeraXWrapper(
            binary_path=self.cfg.libs.chimerax, 
            work_dir=self.working_dir, 
            stdin=stdin)
        chimerax_wrapper.run()

        return self.working_dir / name

class ChargeLigandWorkflow:
    def __init__(self, cfg, working_dir) -> Path:
        self.cfg = cfg
        self.working_dir = working_dir

    def run(self):
        lig_option = self.cfg.common.lig_option
        ligand = self.cfg.common.ligand
        name = self.cfg.common.lig_name
        name = f"{name}_charged.mol2"

        obabel_wrapper = ObabelWrapper(
            binary_path=self.cfg.libs.obabel, 
            work_dir=self.working_dir,
            input_type=lig_option,
            input=ligand, 
            output_name=name, 
            flags=["--gen3d", "--partialcharge", "gasteiger"] # Default for now
            )
        obabel_wrapper.run()

        return self.working_dir / name