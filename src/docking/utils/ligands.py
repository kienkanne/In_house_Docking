import csv
import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LigandRecord:
    smiles: str
    name: str


def _sanitize_name(name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip())
    sanitized = sanitized.strip("._-")
    if not sanitized:
        raise ValueError(f"Invalid ligand name {name!r}")
    return sanitized


def _binary_parts(binary_path) -> list[str]:
    if isinstance(binary_path, str):
        return shlex.split(binary_path)
    return [str(binary_path)]


def validate_smiles(smiles: str, name: str, obabel_binary, working_dir: Path) -> None:
    cmd = _binary_parts(obabel_binary) + [f"-:{smiles}", "-osmi"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=working_dir,
    )
    detail = result.stderr.strip() or result.stdout.strip()
    invalid_markers = (
        "0 molecules converted",
        "SMILES Parse Error",
        "Cannot read",
        "not a valid",
    )
    if result.returncode != 0 and not any(marker in detail for marker in invalid_markers):
        raise RuntimeError(f"Unable to validate SMILES with Open Babel: {detail}")
    if result.returncode != 0 or not result.stdout.strip():
        raise ValueError(f"Invalid SMILES for ligand {name!r}: {smiles!r}. {detail}")


def load_ligand_csv(csv_path: Path, obabel_binary, working_dir: Path) -> list[LigandRecord]:
    csv_path = Path(csv_path)
    if not csv_path.is_absolute():
        csv_path = Path.cwd() / csv_path
    if not csv_path.exists():
        raise FileNotFoundError(f"Ligand CSV not found: {csv_path}")

    records: list[LigandRecord] = []
    seen_names: set[str] = set()

    with open(csv_path, newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["smiles", "name"]:
            raise ValueError("Ligand CSV must have exactly this header: smiles,name")

        for row_number, row in enumerate(reader, start=2):
            smiles = (row.get("smiles") or "").strip()
            raw_name = (row.get("name") or "").strip()
            if not smiles or not raw_name:
                raise ValueError(f"Ligand CSV row {row_number} must include smiles and name")

            name = _sanitize_name(raw_name)
            if name in seen_names:
                raise ValueError(f"Duplicate ligand name after sanitization: {raw_name!r}")
            seen_names.add(name)

            validate_smiles(smiles, name, obabel_binary, working_dir)
            records.append(LigandRecord(smiles=smiles, name=name))

    if not records:
        raise ValueError(f"Ligand CSV contains no ligands: {csv_path}")

    return records
