from pydantic import BaseModel
from typing import Optional
from pathlib import Path


class LibsConfig(BaseModel):
    chimerax: Path
    obabel: Path
    parallel: str = "parallel"

    vina: Path
    prepare_receptor: str
    prepare_ligand: str

    dock6: Path
    sphgen: Path
    sphere_selector: Path
    showbox: Path
    grid: Path


class CommonConfig(BaseModel):
    working_dir: Path
    receptor: Path
    ligand: Path
    lig_name: Optional[str] = None
    results_dir: Path
    pocket_name: str
    total_cpu: int = 1
    max_poses: int = 8


class VinaConfig(BaseModel):
    exhaustiveness: Optional[int] = 32
    num_modes: Optional[int] = 8
    cpu: Optional[int] = 1
    padding: Optional[float] = 5.0
    pocket_option: Optional[str] = "res"
    reference: Optional[Path] = None
    residue_selection: Optional[str] = None


class DOCK6Config(BaseModel):
    max_orientations: float = 5000
    radius: Optional[float] = 10.0
    padding: Optional[float] = 5.0
    residue_selection: Optional[str] = None


class RootConfig(BaseModel):
    libs: LibsConfig
    common: CommonConfig
    vina: VinaConfig
    dock6: DOCK6Config


def load_config(path):
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f)
    return RootConfig.model_validate(data)
