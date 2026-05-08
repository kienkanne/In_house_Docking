import sys
import pymol2

def generate_site(input_file, selection_string, output_file):

    with pymol2.PyMOL() as pymol:
        pymol.start()
        pymol.cmd.load(input_file, "target")
        pymol.cmd.select("to_delete", f"target and not ({selection_string})")
        pymol.cmd.remove("to_delete")
        pymol.cmd.save(output_file, "target")

    return output_file
