import subprocess

def run_chimera(input_file):

    chimera_cmd = ["env", 
                   "LD_PRELOAD=/usr/lib64/libz.so.1:/usr/lib64/libfreetype.so.6", 
                   "LD_LIBRARY_PATH=/usr/local/chem.sw/chimera/chimera-1.8/lib",
                   "chimera", "--nogui", input_file]
    
    result = subprocess.run(chimera_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"chimera failed: {result.stderr}\n{result.stdout}")
    else:
        return True