import subprocess
import logging
from pathlib import Path
import os

class ShellWrapper:
    def __init__(self, binary_path, working_dir):
        self.binary_path = binary_path
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.logger = logging.getLogger(f"docking.{self.__class__.__name__}")

    def _execute(self, cmd_args, stdin=None):
        """Internal runner that handles the subprocess logic."""
        # Handles if binary_path is a string with spaces (e.g. "pythonsh /path/to/script.py")
        if isinstance(self.binary_path, str):
            binary_part_expanded = os.path.expandvars(self.binary_path)
            binary_parts_expanded = binary_part_expanded.split()
            full_cmd = binary_parts_expanded + cmd_args
        else:
            full_cmd = [self.binary_path] + cmd_args
        self.logger.info(f"Running: {' '.join([str(arg) for arg in full_cmd])}")

        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                cwd=self.working_dir,
                input=stdin
            )
            
            # Log stdout/stderr for debugging
            if result.stdout:
                self.logger.debug(f"STDOUT: {result.stdout}")
            if result.stderr:
                self.logger.warning(f"STDERR: {result.stderr}")

            result.check_returncode()
            return result.stdout

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed with exit code {e.returncode}")
            self.logger.error(f"Error output: {e.stderr}")
            raise
