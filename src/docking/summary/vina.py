from pathlib import Path

from docking.summary.common import ligand_name_from_output, write_summary_csv


def parse_vina_scores(path: Path, max_poses: int) -> list[str]:
    scores = []
    with open(path) as handle:
        for line in handle:
            if "REMARK VINA RESULT" not in line:
                continue
            score = line.split(":", 1)[1].split()[0]
            scores.append(score)
            if len(scores) == max_poses:
                break
    return scores


def write_vina_summary(results_dir: Path, receptor, max_poses: int) -> Path:
    results_dir = Path(results_dir)
    receptor_stem = Path(receptor).stem
    rows = []

    for path in sorted(results_dir.glob("*_docked.pdbqt")):
        name = ligand_name_from_output(path, receptor_stem, "_docked.pdbqt")
        scores = parse_vina_scores(path, max_poses)
        rows.append([name] + scores + [""] * (max_poses - len(scores)))

    output_path = results_dir / f"{receptor_stem}_docking_summary.csv"
    return write_summary_csv(rows, output_path, max_poses)
