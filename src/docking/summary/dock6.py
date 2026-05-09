from pathlib import Path

from docking.summary.common import ligand_name_from_output, write_summary_csv


def parse_dock6_scores(path: Path, max_poses: int) -> list[str]:
    scores = []
    with open(path) as handle:
        for line in handle:
            if "Grid_Score" not in line:
                continue
            score = line.split("Grid_Score:", 1)[1].split()[0]
            scores.append(score)
            if len(scores) == max_poses:
                break
    return scores


def write_dock6_summary(results_dir: Path, receptor, max_poses: int) -> Path:
    results_dir = Path(results_dir)
    receptor_stem = Path(receptor).stem
    rows = []

    for path in sorted(results_dir.glob("*_scored.mol2")):
        name = ligand_name_from_output(path, receptor_stem, "_scored.mol2")
        scores = parse_dock6_scores(path, max_poses)
        rows.append([name] + scores + [""] * (max_poses - len(scores)))

    output_path = results_dir / f"{receptor_stem}_docking_summary.csv"
    return write_summary_csv(rows, output_path, max_poses)
