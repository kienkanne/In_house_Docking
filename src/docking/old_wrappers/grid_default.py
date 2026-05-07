import subprocess

def run_grid_default():

    grid_cmd = ["grid", "-i", "grid.in", "-o", "grid.out"]
    result = subprocess.run(grid_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"grid failed: {result.stderr}\n{result.stdout}")
    else:
        return True