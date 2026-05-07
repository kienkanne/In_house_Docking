import subprocess

def run_chimerax(input_file, logger):

    chimerax_cmd = ["ChimeraX", "--nogui"]
    result = subprocess.run(chimerax_cmd, input=input_file, capture_output=True, text=True)

    logger.info(f"ChimeraX command: {' '.join(chimerax_cmd)}")
    logger.info(f"ChimeraX input: {input_file}")
    logger.info(f"ChimeraX stdout: {result.stdout}")
    logger.info(f"ChimeraX stderr: {result.stderr}")

    if result.returncode != 0:
        raise RuntimeError(f"chimerax failed: {result.stderr}\n{result.stdout}")
    else:
        print (f"chimerax output: {result.stdout}, {result.stderr}")
        return True