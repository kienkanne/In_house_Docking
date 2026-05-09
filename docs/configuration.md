# Configuration Reference

The default config is [configs/docking_config.yaml](../configs/docking_config.yaml).

## `libs`

External tools used by wrappers.

| Key | Meaning | Typical value |
| --- | --- | --- |
| `chimerax` | ChimeraX executable for receptor preparation | Absolute path or `ChimeraX` |
| `obabel` | Open Babel executable | `obabel` |
| `parallel` | GNU parallel executable | `parallel` |
| `vina` | AutoDock Vina executable | `vina` |
| `prepare_receptor` | MGLTools receptor script invocation | `/path/to/pythonsh /path/to/prepare_receptor4.py` |
| `prepare_ligand` | MGLTools ligand script invocation | `/path/to/pythonsh /path/to/prepare_ligand4.py` |
| `dock6` | DOCK6 executable | `/path/to/DOCK6/bin/dock6` |
| `sphgen` | DOCK6 sphere generator | `/path/to/DOCK6/bin/sphgen` |
| `sphere_selector` | DOCK6 sphere selector | `/path/to/DOCK6/bin/sphere_selector` |
| `showbox` | DOCK6 box generator | `/path/to/DOCK6/bin/showbox` |
| `grid` | DOCK6 grid generator | `/path/to/DOCK6/bin/grid` |

Conda/mamba-installed tools can usually stay as executable names. MGLTools scripts are the main exception because they need the matching `pythonsh` interpreter.

## `common`

| Key | Meaning |
| --- | --- |
| `working_dir` | Scratch directory for intermediate files and run logs |
| `receptor` | Starting receptor PDB path |
| `ligand` | Ligand CSV path with `smiles,name` columns |
| `results_dir` | Directory where selected outputs and summaries are copied |
| `pocket_name` | Prefix for generated pocket/box files |
| `total_cpu` | Total CPU budget for GNU parallel docking |
| `max_poses` | Maximum number of poses parsed into summary CSVs |

For Vina, concurrent jobs are:

```text
total_cpu // vina.cpu
```

For DOCK6, each ligand job is treated as single-core, so concurrent jobs are:

```text
total_cpu
```

## `vina`

| Key | Meaning |
| --- | --- |
| `exhaustiveness` | Vina search exhaustiveness |
| `num_modes` | Maximum number of Vina poses to write |
| `cpu` | CPU count per ligand job |
| `padding` | Padding added around generated binding box |
| `pocket_option` | `res` for residue selection, `lig` for reference ligand |
| `reference` | Reference ligand path when `pocket_option` is `lig` |
| `residue_selection` | PyMOL-style residue selection when `pocket_option` is `res` |

## `dock6`

| Key | Meaning |
| --- | --- |
| `max_orientations` | DOCK6 flexible docking max orientations |
| `radius` | Sphere selection radius |
| `padding` | Showbox padding |
| `residue_selection` | PyMOL-style residue selection used to write `binding_site.mol2` |

## Minimal Example

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

common:
  working_dir: "/tmp/docking_scratch"
  receptor: "/path/to/8hqg.pdb"
  ligand: "/path/to/sample_ligands.csv"
  results_dir: "/tmp/docking_results"
  pocket_name: "catalytic_site"
  total_cpu: 16
  max_poses: 8

vina:
  exhaustiveness: 32
  num_modes: 8
  cpu: 1
  padding: 5.0
  pocket_option: "res"
  reference: "/path/to/ref_ligand.pdb"
  residue_selection: "chain A and resi 41+145"

dock6:
  max_orientations: 5000
  radius: 10.0
  padding: 5.0
  residue_selection: "chain A and resi 41+145"
```
