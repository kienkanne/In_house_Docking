from string import Template
from pathlib import Path

from docking.wrappers.dock6_tools import Dock6Wrapper

class Dock6Preparation():
    def __init__(self, cfg, working_dir, charged_receptor, charged_ligand, flex_name="flex.in"):
        self.cfg = cfg
        self.working_dir = working_dir
        self.charged_receptor = charged_receptor
        self.charged_ligand = charged_ligand
        self.flex_name = flex_name

        with open(Path(__file__).resolve().parents[1] / "templates" / "dock6_flex_template.txt") as f:
            self.dock6_flex_template = f.read()

    def run(self):
        receptor_name = Path(self.charged_receptor).stem.replace("_charged", "")
        ligand_name = Path(self.charged_ligand).stem.replace("_charged", "") 
        output_prefix = f"{receptor_name}_{ligand_name}"

        max_orientations = self.cfg.dock6.max_orientations

        flex_input = Template(self.dock6_flex_template).substitute(
            charged_receptor=self.charged_receptor,
            charged_ligand=self.charged_ligand,
            max_orientations=max_orientations,
            output_prefix=output_prefix
        )

        with open(self.working_dir / self.flex_name, "w") as file:
            file.write(flex_input)

        dock6_wrapper = Dock6Wrapper(
            binary_path=self.cfg.libs.dock6,
            working_dir=self.working_dir,
            flex=self.flex_name
        )

        docking_results = dock6_wrapper.run()

        output_file = Path(f"{output_prefix}_scored.mol2")
        log_file = output_file.with_suffix(".log")

        with open(self.working_dir / log_file, "w") as file:
            file.write(docking_results)

        return output_file, log_file
