import subprocess

def run_obabel(input_file, flags=None):

    obabel_cmd = ["obabel", "-i", input_file, "-O", input_file.replace(".pdb", ".mol2")]
    if flags:
        obabel_cmd.extend(flags)
        
    result = subprocess.run(obabel_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"obabel failed: {result.stderr}\n{result.stdout}")
    else:
        return True