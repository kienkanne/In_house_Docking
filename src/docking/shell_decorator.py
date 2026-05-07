import subprocess
import logging
from pathlib import Path

class ShellWrapper:
    def __init__(self, binary_path, work_dir=None):
        self.binary_path = binary_path
        self.work_dir = Path(work_dir) if work_dir else Path.cwd()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _execute(self, cmd_args, input_str=None):
        """Internal runner that handles the subprocess logic."""
        full_cmd = [self.binary_path] + cmd_args
        self.logger.info(f"Running: {' '.join(full_cmd)}")

        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                cwd=self.work_dir,
                input=input_str
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

# Usage for ChimeraX
class ChimeraXWrapper(ShellWrapper):
    def run_script(self, script_path):
        return self._execute([ "--nogui", str(script_path)])

# Usage for Vina
class VinaWrapper(ShellWrapper):
    def dock(self, receptor, ligand):
        return self._execute(["--receptor", receptor, "--ligand", ligand])