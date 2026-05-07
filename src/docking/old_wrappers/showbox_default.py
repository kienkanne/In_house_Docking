import subprocess

def run_showbox_default(padding):

    showbox_cmd = ["showbox"]

    input_data = f"Y\n{padding}\nselected_spheres.sph\n1\nrec_box.pdb\n"

    result = subprocess.run(showbox_cmd, input=input_data, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"showbox failed: {result.stderr}\n{result.stdout}")
    else:
        return True