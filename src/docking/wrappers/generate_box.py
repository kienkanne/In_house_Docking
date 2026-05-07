#!/usr/bin/env python3

import argparse
import numpy as np
from pymol import cmd
import pymol2


def write_box_pdb(center, size, outfile):
    """
    Write docking box as a PDB with 8 corner atoms.
    """

    cx, cy, cz = center
    sx, sy, sz = size

    hx = sx / 2
    hy = sy / 2
    hz = sz / 2

    corners = [
        (cx - hx, cy - hy, cz - hz),  # 1
        (cx + hx, cy - hy, cz - hz),  # 2
        (cx + hx, cy - hy, cz + hz),  # 3
        (cx - hx, cy - hy, cz + hz),  # 4
        (cx - hx, cy + hy, cz - hz),  # 5
        (cx + hx, cy + hy, cz - hz),  # 6
        (cx + hx, cy + hy, cz + hz),  # 7
        (cx - hx, cy + hy, cz + hz),  # 8
    ]

    atom_names = ["DUA", "DUB", "DUC", "DUD",
                  "DUE", "DUF", "DUG", "DUH"]

    conect = [
        (1, 2, 4, 5),
        (2, 1, 3, 6),
        (3, 2, 4, 7),
        (4, 1, 3, 8),
        (5, 1, 6, 8),
        (6, 2, 5, 7),
        (7, 3, 6, 8),
        (8, 4, 5, 7),
    ]

    with open(f"{outfile}.pdb", "w") as f:

        f.write("HEADER    CORNERS OF BOX\n")
        f.write(
            f"REMARK    CENTER (X Y Z)"
            f"{cx:10.3f}{cy:8.3f}{cz:8.3f}\n"
        )

        f.write(
            f"REMARK    DIMENSIONS (X Y Z)"
            f"{sx:10.3f}{sy:8.3f}{sz:8.3f}\n"
        )

        for i, ((x, y, z), atom_name) in enumerate(zip(corners, atom_names), start=1):

            line = (
                f"ATOM  {i:5d} {atom_name:<4} BOX A   1    "
                f"{x:8.3f}{y:8.3f}{z:8.3f}"
                f"  1.00  0.00\n"
            )

            f.write(line)

        for c in conect:
            line = "CONECT" + "".join(f"{x:5d}" for x in c)
            f.write(line + "\n")


def vina_box_from_selection(pdb_file,
                            selection,
                            padding,
                            output_box):

    with pymol2.PyMOL() as pymol:
        pymol.start()
        pymol.cmd.load(pdb_file, "receptor")
        stored = {"xyz": []}
        pymol.cmd.iterate_state(
            1,
            f"({selection}) and not hydro",
            "xyz.append([x,y,z])",
            space=stored
        )

        coords = np.array(stored["xyz"])

        if len(coords) == 0:
            raise ValueError(
                f"No atoms matched selection:\n{selection}"
            )

        minv = coords.min(axis=0)
        maxv = coords.max(axis=0)
        size = (maxv - minv) + padding
        center = (minv + maxv) / 2

        write_box_pdb(center, size, output_box)

        return center, size
