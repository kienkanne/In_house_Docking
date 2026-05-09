import json
from pathlib import Path


class RunState:
    """
    Simple checkpoint state for resume support.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if self.path.exists():
            self.state = self.load()
        else:
            self.state = {}

    def load(self):
        with open(self.path) as f:
            return json.load(f)

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.state, f, indent=2)

    def mark_running(self, stage):
        self.state[stage] = "running"
        self.save()

    def mark_failed(self, stage):
        self.state[stage] = "failed"
        self.save()

    def mark_done(self, stage: str, output=None):
        if isinstance(output, (list, tuple)):
            stored_output = [str(item) for item in output]
        else:
            stored_output = str(output) if output else None
        self.state[stage] = {"status": "done", "output": stored_output}
        self.save()

    def get_output(self, stage: str):
        entry = self.state.get(stage, {})
        val = entry.get("output") if isinstance(entry, dict) else None
        if isinstance(val, list):
            return val
        return Path(val) if val else None
    
    def is_done(self, stage: str) -> bool:
        entry = self.state.get(stage, {})
        return (entry.get("status") == "done") if isinstance(entry, dict) else (entry == "done")
