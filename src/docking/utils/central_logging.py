from pathlib import Path
from amber_pipeline.utils.logging_utils import setup_logger
from amber_pipeline.utils.manifest import Manifest
from amber_pipeline.utils.run_state import RunState


def setup_all_logs(prj_name: str, logger_path: Path, manifest_path: Path, state_path: Path) -> tuple:
    logger = setup_logger(logger_path)
    manifest = Manifest(prj_name, manifest_path)
    state = RunState(state_path)

    return (logger, manifest, state)

# Central running and logging wrapper
def central_run_stage(logs, stage_name, func, *args, **kwargs):
    logger, manifest, state = logs

    if state.is_done(stage_name):
        logger.info(f"{stage_name} already done, skipping")
        return state.get_output(stage_name)

    try:
        logger.info(f"{stage_name} started")
        manifest.stage_start(stage_name)
        state.mark_running(stage_name)

        result = func(*args, **kwargs)

        state.mark_done(stage_name)
        manifest.stage_done(stage_name)
        logger.info(f"{stage_name} completed")

    except Exception as e:
        state.mark_failed(stage_name)
        manifest.stage_failed(stage_name, e)
        logger.exception(f"{stage_name} failed")
        manifest.finalize(success=False)
        raise

    return result