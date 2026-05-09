from pathlib import Path

from docking.wrappers.shell_wrapper import ShellWrapper


class GNUParallelWrapper(ShellWrapper):
    def __init__(self, binary_path, working_dir, command_file, jobs):
        super().__init__(binary_path, working_dir)
        self.command_file = Path(command_file)
        self.jobs = max(1, int(jobs))

    def run(self):
        cmd_args = [
            "--jobs",
            str(self.jobs),
            "--halt",
            "soon,fail=1",
            "::::",
            str(self.command_file),
        ]
        return self._execute(cmd_args, None)
