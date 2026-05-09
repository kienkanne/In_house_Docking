from docking.wrappers.vina_generate_box import vina_generate_box
from string import Template
from pathlib import Path

class VinaBoxWorkflow:
    def __init__(self, cfg, working_dir, prepared_receptor) -> Path:
        self.cfg = cfg
        self.working_dir = working_dir
        self.prepared_receptor = prepared_receptor

        with open(Path(__file__).resolve().parents[1] / "templates" / "vina_config_template.txt") as f:
            self.charge_receptor_template = f.read()

    def run(self):
        self.pocket_name = self.cfg.common.pocket_name

        if self.cfg.vina.pocket_option == "res":
            self.input = self.working_dir / self.prepared_receptor
            self.selection = self.cfg.vina.residue_selection

        elif self.cfg.vina.pocket_option == "lig":
            self.input = self.cfg.vina.reference
            self.selection = f"byres ({self.cfg.vina.reference})" # should select all of the given reference

        self.padding = self.cfg.vina.padding
        self.cpu = self.cfg.vina.cpu
        self.exhaustiveness = self.cfg.vina.exhaustiveness
        self.num_modes = self.cfg.vina.num_modes

        # Also outputs a pdb file of the box with pocket name
        center, size = vina_generate_box(
            self.input, 
            self.selection, 
            self.padding, 
            self.working_dir / self.pocket_name)

        vina_config = Template(self.charge_receptor_template).substitute(
            receptor=self.prepared_receptor,
            center_x=center[0],
            center_y=center[1],
            center_z=center[2],
            size_x=size[0],
            size_y=size[1],
            size_z=size[2],
            cpu=self.cpu,
            exhaustiveness=self.exhaustiveness,
            num_modes=self.num_modes
            )

        with open(self.working_dir / "vina_config.txt", "w") as file:
            file.write(vina_config)

        return "vina_config.txt", f"{self.pocket_name}.pdb"

        