from docking.wrappers.shell_wrapper import ShellWrapper
from pathlib import Path
from string import Template

class WriteDMSWrapper(ShellWrapper):
    def __init__(self, working_dir, noH_receptor, binary_path=None):
        super().__init__(binary_path, working_dir)
        self.noH_receptor = noH_receptor
    
        with open(Path(__file__).resolve().parents[1] / "templates" / "chimera_write_dms_template.py") as f:
            self.chimera_write_dms_template = f.read()

    def run(self):
        self.binary_path = "env " \
        "LD_PRELOAD=/usr/lib64/libz.so.1:/usr/lib64/libfreetype.so.6 " \
        "LD_LIBRARY_PATH=/usr/local/chem.sw/chimera/chimera-1.8/lib " \
        "/usr/local/chimera/chimera-1.8/bin/chimera"

        input_file = Template(self.chimera_write_dms_template).substitute(
            name=self.noH_receptor
        )

        with open(self.working_dir / "chimera_write_dms.py", "w") as file:
            file.write(input_file)

        cmd_args =[
            "--nogui",
            "chimera_write_dms.py"
        ]
        return self._execute(cmd_args, None)


class SphgenDefaultWrapper(ShellWrapper):
    def __init__(self, binary_path, working_dir):
        super().__init__(binary_path, working_dir)

        with open(Path(__file__).resolve().parents[1] / "templates" / "dock6_INSPH_template.txt") as f:
            self.dock6_INSPH_template = f.read()

    def run(self):
        input_file = Template(self.dock6_INSPH_template).substitute()

        with open(self.working_dir / "INSPH", "w") as file:
            file.write(input_file)

        cmd_args = [
            #sphgen,
            "-i", 
            "INPSH", 
            "-o", 
            "OUTSPH"
            ]
        return self._execute(cmd_args, None)


class SphereSelectorDefaultWrapper(ShellWrapper):
    def __init__(self, binary_path, working_dir, radius):
        super().__init__(binary_path, working_dir)
        self.radius = str(radius)

    def run(self):
        cmd_args = [
            #sphere_selector,
            "rec.sph", 
            "binding_site.mol2",
            self.radius  
            ]
        return self._execute(cmd_args, None)
    

class ShowboxDefaultWrapper(ShellWrapper):
    def __init__(self, binary_path, working_dir, padding):
        super().__init__(binary_path, working_dir)
        self.padding = str(padding)

    def run(self):
        stdin = f"Y\n{self.padding}\nselected_spheres.sph\n1\nrec_box.pdb\n"
        cmd_args = [
            #showbox,
            ]
        return self._execute(cmd_args, stdin)
    

class GridDefaultWrapper(ShellWrapper):
    def __init__(self, binary_path, working_dir, charged_receptor):
        super().__init__(binary_path, working_dir)
        self.charged_receptor = charged_receptor

        with open(Path(__file__).resolve().parents[1] / "templates" / "dock6_grid_template.txt") as f:
            self.dock6_grid_template = f.read()

    def run(self):
        input_file = Template(self.dock6_grid_template).substitute(
            charged_receptor=self.charged_receptor
        )
        with open(self.working_dir / "grid.in", "w") as file:
            file.write(input_file)

        cmd_args = [
            #grid,
            "-i",
            "grid.in",
            "-o",
            "grid.out", 
            ]
        return self._execute(cmd_args, None)
    
    
class Dock6Wrapper(ShellWrapper):
    def __init__(self, binary_path, working_dir, flex):
        super().__init__(binary_path, working_dir)
        self.flex = flex

    def run(self):
        cmd_args = [
            #dock6_prep,
            "-i",
            self.flex
            ]
        return self._execute(cmd_args, None)