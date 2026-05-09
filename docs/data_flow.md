# Data Flow

This page describes the files produced and consumed by each major stage.

## Shared Inputs

The config provides:

- A receptor PDB file: `common.receptor`
- A ligand CSV file: `common.ligand`
- A scratch folder: `common.working_dir`
- A results folder: `common.results_dir`

The ligand CSV is read into `LigandRecord` objects with:

```text
smiles,name
```

SMILES validation happens once before docking starts.

## Vina Data Flow

```text
receptor.pdb
  -> ChargeReceptorWorkflow
  -> receptor_charged.pdb
  -> PrepareReceptorWrapper
  -> receptor_charged_prepared.pdbqt
```

The prepared receptor is passed into `VinaBoxWorkflow`, which writes:

```text
vina_config.txt
<pocket_name>.pdb
```

Each ligand goes through an independent GNU parallel task:

```text
ligand SMILES
  -> ChargeLigandWorkflow
  -> ligand_charged.mol2
  -> PrepareLigandWrapper
  -> ligand_charged_prepared.pdbqt
  -> VinaWrapper
  -> receptor_ligand_docked.pdbqt
  -> receptor_ligand_docked.log
```

The orchestrator copies final pose files, docking logs, receptor/config files, and pipeline logs to `results_dir`.

`write_vina_summary()` scans all `*_docked.pdbqt` files in `results_dir` and parses every `REMARK VINA RESULT` line up to `common.max_poses`.

## DOCK6 Data Flow

```text
receptor.pdb
  -> ChargeReceptorWorkflow(dock6=True)
  -> receptor_charged.pdb
  -> receptor_charged_noH.pdb
  -> receptor_charged_noH.mol2
```

The no-H receptor files are used to build the DOCK6 site:

```text
receptor_charged_noH.mol2
  -> WriteDMSWrapper
  -> rec.dms
  -> SphgenDefaultWrapper
  -> rec.sph

receptor_charged_noH.pdb
  -> generate_site
  -> binding_site.mol2

rec.sph + binding_site.mol2
  -> SphereSelectorDefaultWrapper
  -> selected_spheres.sph
  -> ShowboxDefaultWrapper
  -> rec_box.pdb
  -> GridDefaultWrapper
  -> grid.bmp / grid.nrg / grid.out
```

Each ligand goes through an independent GNU parallel task:

```text
ligand SMILES
  -> ChargeLigandWorkflow
  -> ligand_charged.mol2
  -> Dock6Preparation
  -> flex_<ligand>.in
  -> Dock6Wrapper
  -> receptor_ligand_scored.mol2
  -> receptor_ligand_scored.log
```

Per-ligand `flex_<ligand>.in` files avoid collisions when many DOCK6 jobs run at the same time.

`write_dock6_summary()` scans all `*_scored.mol2` files in `results_dir` and parses every `Grid_Score` line up to `common.max_poses`.

## Summary Output

Both engines write:

```text
<receptor_stem>_docking_summary.csv
```

The format is:

```text
name,pose1,pose2,pose3,...
```

Rows are sorted by `pose1` in ascending numeric order. Missing poses are left empty.
