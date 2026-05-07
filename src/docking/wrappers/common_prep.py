from docking.wrappers.shell_wrapper import ShellWrapper


class ChimeraXWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, stdin):
        super().__init__(binary_path, work_dir)
        self.stdin = stdin

    def run(self):
        cmd_args =[
            #"ChimeraX",
            "--nogui"
        ]
        return self._execute(cmd_args, self.stdin)
    

class ObabelWrapper(ShellWrapper):
    def __init__(self, binary_path, work_dir, input_type, input, output_name, flags):
        super().__init__(binary_path, work_dir)
        self.input_type = input_type
        self.input = input
        self.output_name = output_name
        self.flags = flags

    def run(self):
        if self.input_type == "file":
            cmd_args = [
                #"obabel",
                "-i", self.input,
                "-O", self.output_name
            ] + self.flags

        elif self.input_type == "smiles":
            cmd_args = [
                #"obabel",
                f"-:{self.input}",
                "-O", self.output_name
            ] + self.flags
        return self._execute(cmd_args, None)