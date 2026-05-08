from pathlib import Path
from string import Template
import os

from docking.wrappers.charge_tools import ChimeraXWrapper, ObabelWrapper


class ChargeReceptorWorkflow: 
    def __init__(self, cfg, working_dir, output_type, noH=False):
        self.cfg = cfg
        self.working_dir = working_dir
        self.output_type = output_type
        self.noH = noH
        with open(Path(__file__).resolve().parents[1] / "templates" / "chimerax_charge_receptor_template.com") as f:
            self.charge_receptor_template = f.read()

    def run(self):
        receptor = self.cfg.common.receptor
        name = os.path.basename(receptor).split('.')[0]
        charged_name = f"{name}_charged.{self.output_type}"

        stdin = Template(self.charge_receptor_template).substitute(
            receptor=receptor,
            name=charged_name
            )
        
        # Writes an additional line to input to remove H if noH is True, otherwise keeps H
        # Save another file with _noH suffix if noH is True. It should be {name}_charged_noH.{self.output_type}
        if self.noH:
            stdin += "\ndelete H\n"
            stdin += f"\nsave {name}_charged_noH.{self.output_type}\n"

        chimerax_wrapper = ChimeraXWrapper(
            binary_path=self.cfg.libs.chimerax, 
            working_dir=self.working_dir, 
            stdin=stdin)
        chimerax_wrapper.run()
        
        if self.noH:
            return (charged_name, f"{name}_charged_noH.{self.output_type}")

        return charged_name

class ChargeLigandWorkflow:
    def __init__(self, cfg, working_dir, output_type) -> Path:
        self.cfg = cfg
        self.working_dir = working_dir
        self.output_type = output_type

    def run(self):
        lig_option = self.cfg.common.lig_option
        ligand = self.cfg.common.ligand
        name = self.cfg.common.lig_name
        name = f"{name}_charged.{self.output_type}"

        obabel_wrapper = ObabelWrapper(
            binary_path=self.cfg.libs.obabel, 
            working_dir=self.working_dir,
            input_type=lig_option,
            input=ligand, 
            output_name=name, 
            flags=["--gen3d", "--partialcharge", "gasteiger"] # Default for now
            )
        obabel_wrapper.run()

        return name