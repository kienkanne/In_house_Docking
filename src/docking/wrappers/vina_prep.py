from docking.wrappers.shell_wrapper import ShellWrapper


class PrepareLigandWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, input_file):
        super().__init__(binary_path, work_dir)
        self.input_file = input_file

    def run(self):
        cmd_args = [
            #"prepare_ligand4.py",
            "-l", self.input_file,
            "-o", self.input_file.replace(".pdb", "_prepared.pdbqt")
        ]
        return self._execute(cmd_args, None)
    

class PrepareReceptorWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, input_file):
        super().__init__(binary_path, work_dir)
        self.input_file = input_file

    def run(self):
        cmd_args = [
            #"prepare_receptor4.py",
            "-r", self.input_file,
            "-o", self.input_file.replace(".pdb", "_prepared.pdbqt")
        ]
        return self._execute(cmd_args, None)
    

class VinaWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, receptor, ligand, configs):
        super().__init__(binary_path, work_dir)
        self.receptor = receptor
        self.ligand = ligand
        self.configs = configs

    def run(self):
        cmd_args = [
            #"vina",
            "--receptor", self.receptor,
            "--ligand", self.ligand,
            "--config", self.configs,
            "--out", self.ligand.replace(".pdbqt", "_docked.pdbqt")
        ]
        return self._execute(cmd_args, None) # Return docking results