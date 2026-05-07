import subprocess

def run_prepare_receptor4(input_file):

    chimera_cmd = ["pythonsh", 
                   "prepare_ligand4.py",
                   "-l", input_file,
                   "-o", input_file.replace(".pdb", "_prepared.pdbqt")
                   ]

    result = subprocess.run(chimera_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"prepare_receptor4 failed: {result.stderr}\n{result.stdout}")
    else:
        return True