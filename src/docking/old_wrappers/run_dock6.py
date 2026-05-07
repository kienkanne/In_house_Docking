import subprocess

def run_dock6(flex, output_prefix, working_dir):

    dock6_cmd = ["dock6", "-i", flex]
    result = subprocess.run(dock6_cmd, capture_output=True, text=True)

    stdout = working_dir / f"{output_prefix}.log"

    if result.stdout is not None:
        with open (stdout, "w") as file:
            file.write(result.stdout)

    if result.returncode != 0:
        raise RuntimeError(f"dock6 failed: {result.stderr}\n{result.stdout}")
    else:
        return True