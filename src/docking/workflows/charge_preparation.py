from pathlib import Path
from string import Template
import os

from docking.wrappers.charge_tools import ChimeraXWrapper, ObabelWrapper


class ChargeReceptorWorkflow: 
    def __init__(self, cfg, working_dir, dock6=False):
        self.cfg = cfg
        self.working_dir = working_dir
        self.dock6 = dock6

        with open(Path(__file__).resolve().parents[1] / "templates" / "chimerax_charge_receptor_template.com") as f:
            self.charge_receptor_template = f.read()

    def run(self):
        receptor = self.cfg.common.receptor
        name = Path(receptor).stem
        if self.dock6:
            charged_name = f"{name}_charged.mol2"
        else:
            charged_name = f"{name}_charged.pdb"
        
        stdin = Template(self.charge_receptor_template).substitute(
            receptor=receptor,
            name=charged_name
            )
        
        # Writes an additional line to input to remove H if noH is True, otherwise keeps H
        if self.dock6:
            stdin += "\ndelete H\n"
            stdin += f"\nsave {name}_charged_noH.pdb\n"
            stdin += f"\nsave {name}_charged_noH.mol2\n"

        chimerax_wrapper = ChimeraXWrapper(
            binary_path=self.cfg.libs.chimerax, 
            working_dir=self.working_dir, 
            stdin=stdin)
        chimerax_wrapper.run()
        
        if self.dock6:
            return (charged_name, f"{name}_charged_noH.mol2", f"{name}_charged_noH.pdb")
        else:
            return charged_name

class ChargeLigandWorkflow:
    def __init__(self, cfg, working_dir, output_type, ligand=None, ligand_name=None) -> Path:
        self.cfg = cfg
        self.working_dir = working_dir
        self.output_type = output_type
        self.ligand = ligand
        self.ligand_name = ligand_name

    def run(self):
        ligand = self.ligand
        name = self.ligand_name
        out_name = f"{name}_charged.{self.output_type}"

        obabel_wrapper = ObabelWrapper(
            binary_path=self.cfg.libs.obabel, 
            working_dir=self.working_dir,
            input=ligand, 
            output_name=out_name, 
            flags=["--gen3d", "--partialcharge", "gasteiger"] # Default for now
            )
        obabel_wrapper.run()

        return out_name
