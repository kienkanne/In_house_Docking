# Architecture

The code is organized around three layers:

- Orchestrators: top-level workflow sequencing for Vina and DOCK6.
- Workflows: reusable multi-step operations, such as receptor charging, Vina box generation, and parallel ligand docking.
- Wrappers: thin adapters around external command-line programs.

## Entry Points

CLI:

```text
docking run_vina --config configs/docking_config.yaml
docking run_dock6 --config configs/docking_config.yaml
```

Thin scripts:

```text
scripts/run_vina.py
scripts/run_dock6.py
```

Both paths load a YAML config with `load_config()` and instantiate the relevant orchestrator.

## Vina Call Hierarchy

```text
OrchestratorVina.run()
  setup_all_logs()
  central_run_stage("Validate Ligands", load_ligand_csv)
  central_run_stage("Charge Receptor", ChargeReceptorWorkflow.run)
    ChimeraXWrapper.run()
  central_run_stage("Prepare Receptor", PrepareReceptorWrapper.run)
  central_run_stage("Generate Vina Box", VinaBoxWorkflow.run)
    vina_generate_box()
  central_run_stage("Dock Vina Ligands", ParallelLigandDockingWorkflow.run)
    GNUParallelWrapper.run()
      python -m docking.workflows.parallel_ligand_task task.json
        ChargeLigandWorkflow.run()
        PrepareLigandWrapper.run()
        VinaWrapper.run()
  copy selected outputs to results_dir
  central_run_stage("Write Vina Summary", write_vina_summary)
```

## DOCK6 Call Hierarchy

```text
OrchestratorDock6.run()
  setup_all_logs()
  central_run_stage("Validate Ligands", load_ligand_csv)
  central_run_stage("Charge Receptor", ChargeReceptorWorkflow.run)
    ChimeraXWrapper.run()
  central_run_stage("Write DMS", WriteDMSWrapper.run)
  central_run_stage("Generate Spheres", SphgenDefaultWrapper.run)
  central_run_stage("Generate Binding Site", generate_site)
  central_run_stage("Select Spheres", SphereSelectorDefaultWrapper.run)
  central_run_stage("Generate Box", ShowboxDefaultWrapper.run)
  central_run_stage("Generate Grid", GridDefaultWrapper.run)
  central_run_stage("Dock DOCK6 Ligands", ParallelLigandDockingWorkflow.run)
    GNUParallelWrapper.run()
      python -m docking.workflows.parallel_ligand_task task.json
        ChargeLigandWorkflow.run()
        Dock6Preparation.run()
          Dock6Wrapper.run()
  copy selected outputs to results_dir
  central_run_stage("Write DOCK6 Summary", write_dock6_summary)
```

## Logging and State

Each orchestrator calls `setup_all_logs()` in the working directory. This creates:

- `run.log`: human-readable log messages.
- `manifest.json`: stage status, host metadata, and timing data.
- `state.json`: checkpoint state for stages that can be skipped when already complete.

Stages are wrapped with `central_run_stage()`. On failure, the stage is marked failed in both manifest and state before the exception is raised.

## Parallel Docking

`ParallelLigandDockingWorkflow` writes one JSON task per ligand under:

```text
<working_dir>/.parallel_tasks/<engine>/
```

It also writes a `commands.txt` file. GNU parallel executes those commands with the configured number of jobs.

Each ligand task writes a sibling `*.result.json` file containing the final pose and log filenames. The parent workflow reads those files after GNU parallel completes.
