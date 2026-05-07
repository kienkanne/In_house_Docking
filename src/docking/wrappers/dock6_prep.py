from docking.wrappers.shell_wrapper import ShellWrapper


class ChimeraWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, stdin):
        super().__init__(binary_path, work_dir)
        self.stdin = stdin

    def run(self):
        cmd_args =[
            #env 
            #LD_PRELOAD=/usr/lib64/libz.so.1:/usr/lib64/libfreetype.so.6 
            #LD_LIBRARY_PATH=/usr/local/chem.sw/chimera/chimera-1.8/lib 
            #chimera,
            "--nogui"
        ]
        return self._execute(cmd_args, self.stdin)


class SphgenDefaultWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir):
        super().__init__(binary_path, work_dir)

    def run(self):
        cmd_args = [
            #sphgen,
            "-i", 
            "INPSH", 
            "-o", 
            "OUTSPH"
            ]
        return self._execute(cmd_args, None)


class SphereSelectorDefaultWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, binding_site, radius):
        super().__init__(binary_path, work_dir)
        self.binding_site = binding_site
        self.radius = radius

    def run(self):
        cmd_args = [
            #sphere_selector,
            "rec.sph", 
            self.binding_site,
            self.radius  
            ]
        return self._execute(cmd_args, None)
    

class ShowboxDefaultWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, padding):
        super().__init__(binary_path, work_dir)
        self.padding = padding

    def run(self):
        stdin = f"Y\n{self.padding}\nselected_spheres.sph\n1\nrec_box.pdb\n"
        cmd_args = [
            #showbox,
            ]
        return self._execute(cmd_args, stdin)
    

class GridDefaultWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, binding_site, radius):
        super().__init__(binary_path, work_dir)
        self.binding_site = binding_site
        self.radius = radius

    def run(self):
        cmd_args = [
            #grid,
            "-i",
            "grid.in",
            "-o",
            "grid.out", 
            ]
        return self._execute(cmd_args, None)
    
    
class Dock6Wrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, flex):
        super().__init__(binary_path, work_dir)
        self.flex = flex

    def run(self):
        cmd_args = [
            #dock6_prep,
            "-i",
            self.flex
            ]
        return self._execute(cmd_args, None)