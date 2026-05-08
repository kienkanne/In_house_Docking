from dataclasses import replace
from pathlib import Path

from docking.wrappers.shell_wrapper import ShellWrapper


class PrepareLigandWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, input_file):
        super().__init__(binary_path, work_dir)
        self.input_file = input_file

    def run(self):

        output_file = str(self.input_file).replace(".mol2", "_prepared.pdbqt")
        cmd_args = [
            #"prepare_ligand4.py",
            "-l", self.input_file,
            "-o", output_file
        ]
        self._execute(cmd_args, None)

        return self.work_dir / output_file

class PrepareReceptorWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, input_file):
        super().__init__(binary_path, work_dir)
        self.input_file = input_file

    def run(self):
        output_file = str(self.input_file).replace(".pdb", "_prepared.pdbqt")

        cmd_args = [
            #"prepare_receptor4.py",
            "-r", self.input_file,
            "-o", output_file
        ]
        self._execute(cmd_args, None)

        return self.work_dir / output_file

class VinaWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, receptor, ligand, configs):
        super().__init__(binary_path, work_dir)
        self.receptor = receptor
        self.ligand = ligand
        self.configs = configs

    def run(self):
        # Output name contains both receptor and ligand name
        # "charged" and : "_prepared" are removed for cleaner output name
        receptor_name = Path(self.receptor).stem.replace("_prepared", "").replace("_charged", "")
        ligand_name = Path(self.ligand).stem.replace("_prepared", "").replace("_charged", "") 
        output_name = f"{receptor_name}_{ligand_name}"

        cmd_args = [
            #"vina",
            "--receptor", self.receptor,
            "--ligand", self.ligand,
            "--config", self.configs,
            "--out", output_name + "_docked.pdbqt"
        ]
        return self._execute(cmd_args, None) # Return docking results