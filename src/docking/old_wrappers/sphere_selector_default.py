import subprocess

def run_sphere_selector_default(binding_site, radius):

    sphgen_cmd = ["sphere_selector", "rec.sph", binding_site, str(radius)]
    result = subprocess.run(sphgen_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"sphere_selector failed: {result.stderr}\n{result.stdout}")
    else:
        return True 