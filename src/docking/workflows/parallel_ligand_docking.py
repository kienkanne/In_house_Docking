import json
import shlex
import sys
from pathlib import Path

from docking.utils.ligands import LigandRecord
from docking.wrappers.parallel_tools import GNUParallelWrapper


class ParallelLigandDockingWorkflow:
    """Write per-ligand task files and execute them with GNU parallel."""

    def __init__(self, cfg, working_dir, engine, ligands, jobs, **task_inputs):
        self.cfg = cfg
        self.working_dir = Path(working_dir)
        self.engine = engine
        self.ligands = ligands
        self.jobs = max(1, int(jobs))
        self.task_inputs = task_inputs

    def _ligand_payload(self, ligand):
        if isinstance(ligand, LigandRecord):
            return {"smiles": ligand.smiles, "name": ligand.name}
        return {"smiles": ligand["smiles"], "name": ligand["name"]}

    def _write_tasks(self):
        """Create task JSON files plus the command file consumed by GNU parallel."""
        task_dir = self.working_dir / ".parallel_tasks" / self.engine
        task_dir.mkdir(parents=True, exist_ok=True)
        command_file = task_dir / "commands.txt"
        commands = []

        for ligand in self.ligands:
            ligand_payload = self._ligand_payload(ligand)
            task_path = task_dir / f"{ligand_payload['name']}.json"
            task_data = {
                "cfg": self.cfg.model_dump(mode="json"),
                "working_dir": str(self.working_dir),
                "engine": self.engine,
                "ligand": ligand_payload,
                **self.task_inputs,
            }
            with open(task_path, "w") as handle:
                json.dump(task_data, handle, indent=2)

            commands.append(
                " ".join(
                    [
                        shlex.quote(sys.executable),
                        "-m",
                        "docking.workflows.parallel_ligand_task",
                        shlex.quote(str(task_path)),
                    ]
                )
            )

        with open(command_file, "w") as handle:
            handle.write("\n".join(commands))
            handle.write("\n")

        return command_file, task_dir

    def run(self):
        command_file, task_dir = self._write_tasks()
        GNUParallelWrapper(
            binary_path=self.cfg.libs.parallel,
            working_dir=self.working_dir,
            command_file=command_file,
            jobs=self.jobs,
        ).run()

        outputs = []
        logs = []
        for ligand in self.ligands:
            ligand_payload = self._ligand_payload(ligand)
            result_path = task_dir / f"{ligand_payload['name']}.result.json"
            if not result_path.exists():
                raise FileNotFoundError(f"Parallel task did not produce result: {result_path}")
            with open(result_path) as handle:
                result = json.load(handle)
            outputs.append(result["output_file"])
            logs.append(result["log_file"])

        return outputs, logs
