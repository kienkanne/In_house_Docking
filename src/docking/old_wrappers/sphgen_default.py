import subprocess

def run_sphgen():

    sphgen_cmd = ["sphgen", "-i", "INPSH", "-o", "OUTSPH"]
    result = subprocess.run(sphgen_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"sphgen failed: {result.stderr}\n{result.stdout}")
    else:
        return True 