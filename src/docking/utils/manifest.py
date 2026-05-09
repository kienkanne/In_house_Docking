import json
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
import platform


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class Manifest:
    """
    Tracks metadata + stage timings.
    Writes JSON safely.
    """

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        

        self.data = {
            "project": str(name),
            "created_utc": utc_now(),
            "host": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "status": "running",
            "stages": {},
            "timings_sec": {},
            "total_wall_time": ""
        }

        self._timers = {}

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def stage_start(self, stage_name):
        self.data["stages"][stage_name] = "running"
        self._timers[stage_name] = time.perf_counter()
        self.save()

    def stage_done(self, stage_name):
        self.data["stages"][stage_name] = "done"

        if stage_name in self._timers:
            dt = time.perf_counter() - self._timers[stage_name]
            self.data["timings_sec"][stage_name] = round(dt, 3)

        self.save()

    def stage_failed(self, stage_name, reason=None):
        self.data["stages"][stage_name] = "failed"
        if reason:
            self.data.setdefault("errors", {})[stage_name] = str(reason)
        self.save()

    def finalize(self, success=True):
        self.data["status"] = "success" if success else "failed"
        self.data["finished_utc"] = utc_now()

        total_dt = time.perf_counter() - self._start_time
        self.data["total_wall_time"] = f"{total_dt:.3f}s"
        self.save()

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)