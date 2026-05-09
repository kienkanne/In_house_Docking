import csv
import math
from pathlib import Path


def ligand_name_from_output(path: Path, receptor_stem: str, suffix: str) -> str:
    """Convert receptor_ligand_suffix output filenames back to ligand names."""
    name = path.name
    prefix = f"{receptor_stem}_"
    if name.startswith(prefix):
        name = name[len(prefix):]
    if name.endswith(suffix):
        name = name[:-len(suffix)]
    return name


def write_summary_csv(rows, output_path: Path, max_poses: int) -> Path:
    """Write score rows sorted by the first pose score."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    headers = ["name"] + [f"pose{i}" for i in range(1, max_poses + 1)]

    def pose1_sort(row):
        score = row[1] if len(row) > 1 else ""
        return float(score) if score != "" else math.inf

    rows = sorted(rows, key=pose1_sort)
    with open(output_path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)
    return output_path
