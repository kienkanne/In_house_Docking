from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path

class LibsConfig(BaseModel):
    chimerax: Path
    obabel: Path
    vina: Path
    dock6: Path
    prepare_receptor: str
    prepare_ligand: str

class CommonConfig(BaseModel):
    receptor: Path
    lig_option: str
    ligand: Path
    lig_name: str
    output_dir: Path
    pocket_name: str

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
    padding: Optional[float] = 5.0
    pocket_selection: List[int] = None

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