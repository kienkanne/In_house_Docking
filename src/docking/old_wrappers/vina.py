import subprocess

def run_vina(receptor, ligand, config, output, working_dir):

    vina_cmd = ["vina", "--receptor", receptor, "--ligand", ligand, "--config", config, "--out", output]
    result = subprocess.run(vina_cmd, capture_output=True, text=True)

    stdout = working_dir / output.replace(".pdbqt", ".log")

    if result.stdout is not None:
        with open (stdout, "w") as file:
            file.write(result.stdout)

    if result.returncode != 0:
        raise RuntimeError(f"vina failed: {result.stderr}\n{result.stdout}")
    else:
        return True