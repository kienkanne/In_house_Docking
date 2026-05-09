# SARS-CoV-2 Docking Pipeline

This repository runs end-to-end molecular docking workflows for a receptor PDB and a CSV of ligands. It currently supports:

- AutoDock Vina
- DOCK6

The pipeline prepares the receptor, prepares each ligand from SMILES, docks ligands in parallel with GNU parallel, copies selected outputs to a results folder, and writes a docking summary CSV sorted by the best pose score.

## Installation

Install the Python package in editable mode from the repository root:

```bash
pip install -e .
```

Most command-line tools can be installed into the active conda/mamba environment and referenced by executable name in the config:

```yaml
obabel: "obabel"
parallel: "parallel"
vina: "vina"
```

Some tools usually need explicit paths:

- `prepare_receptor` and `prepare_ligand` must include the MGLTools `pythonsh` executable plus the full script path.
- DOCK6 tools such as `dock6`, `sphgen`, `sphere_selector`, `showbox`, and `grid` are usually installed outside conda and should be absolute paths.
- `chimerax` should point to the ChimeraX executable if it is not on `PATH`.

## Running

Use the CLI with a config file:

```bash
docking run_vina --config configs/docking_config.yaml
docking run_dock6 --config configs/docking_config.yaml
```

There are also thin scripts:

```bash
python scripts/run_vina.py
python scripts/run_dock6.py
```

Those scripts load `configs/docking_config.yaml` by default.

## Ligand CSV

The ligand file must be a CSV with exactly this header:

```csv
smiles,name
CC(=O)OC1=CC=CC=C1C(=O)O,aspirin
CC1=C(C=C(C=C1)C(C)C)O,carvacrol
```

Ligand names are used in output filenames, so keep them short and file-friendly. The loader sanitizes names and raises an error for duplicate names after sanitization. Each SMILES string is validated with Open Babel before docking starts.

## Config Format

See [configs/docking_config.yaml](configs/docking_config.yaml) for a working example.

### `libs`

Tool locations and executable names.

```yaml
libs:
  chimerax: "/usr/local/chimerax/bin/ChimeraX"
  obabel: "obabel"
  parallel: "parallel"
  vina: "vina"
  prepare_receptor: "/path/to/pythonsh /path/to/prepare_receptor4.py"
  prepare_ligand: "/path/to/pythonsh /path/to/prepare_ligand4.py"
  dock6: "/path/to/DOCK6/bin/dock6"
  sphgen: "/path/to/DOCK6/bin/sphgen"
  sphere_selector: "/path/to/DOCK6/bin/sphere_selector"
  showbox: "/path/to/DOCK6/bin/showbox"
  grid: "/path/to/DOCK6/bin/grid"
```

### `common`

Inputs, scratch directory, results directory, and batch settings.

```yaml
common:
  working_dir: "/path/to/scratch/sample_vina"
  receptor: "/path/to/data/8hqg.pdb"
  ligand: "/path/to/data/sample_ligands.csv"
  results_dir: "/path/to/results/results_vina"
  pocket_name: "catalytic_site"
  total_cpu: 16
  max_poses: 8
```

- `working_dir`: scratch space where intermediate files are written.
- `receptor`: starting receptor PDB.
- `ligand`: CSV path with `smiles,name`.
- `results_dir`: final selected outputs and summary CSV are copied here.
- `total_cpu`: total CPU budget for ligand docking.
- `max_poses`: maximum number of scores to parse per ligand into the summary CSV.

### `vina`

Vina-specific settings.

```yaml
vina:
  exhaustiveness: 32
  num_modes: 8
  cpu: 1
  padding: 5.0
  pocket_option: "res"
  reference: "/path/to/ref_ligand.pdb"
  residue_selection: "chain A and resi 41+145"
```

- `cpu` is the CPU count per ligand job.
- Vina parallel job count is `common.total_cpu // vina.cpu`.
- `pocket_option: "res"` uses `residue_selection`.
- `pocket_option: "lig"` uses `reference`.

### `dock6`

DOCK6-specific settings.

```yaml
dock6:
  max_orientations: 5000
  radius: 10.0
  padding: 5.0
  residue_selection: "chain A and resi 41+145"
```

DOCK6 jobs are single-core, so the parallel job count is `common.total_cpu`.

## Outputs

The results directory contains selected final files:

- Vina poses: `*_docked.pdbqt`
- Vina docking logs: `*_docked.log`
- DOCK6 poses: `*_scored.mol2`
- DOCK6 docking logs: `*_scored.log`
- Pipeline logs: `run.log`, `manifest.json`, `state.json`
- Summary CSV: `<receptor_stem>_docking_summary.csv`

The summary CSV has this format:

```csv
name,pose1,pose2,pose3,...
aspirin,-2.383,-1.596,-1.454,...
carvacrol,-1.917,-1.528,-1.319,...
```

Rows are sorted by `pose1`, with lower scores first.

## More Documentation

- [Architecture](docs/architecture.md)
- [Data Flow](docs/data_flow.md)
- [Configuration Reference](docs/configuration.md)
