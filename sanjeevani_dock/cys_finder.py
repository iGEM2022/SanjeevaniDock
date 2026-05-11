"""
cys_finder.py
-------------
Parses a PDB file and returns the mean (x, y, z) coordinates of 
all Cysteine SG (sulfur gamma) atoms. This centroid is used as the 
focused docking grid center, because heavy metals coordinate directly
to cysteine sulfur atoms in metallothioneins.

NOTE: We use SG (sulfur) and NOT CA (alpha carbon) because the metal
coordination chemistry happens at the sulfur, not the backbone.
"""

import os
from typing import Tuple, List


def find_cys_sg_coordinates(pdb_path: str) -> List[Tuple[float, float, float]]:
    """
    Parse a PDB file and extract the (x, y, z) coordinates of all
    CYS SG atoms.

    Parameters
    ----------
    pdb_path : str
        Absolute or relative path to the protein .pdb file.

    Returns
    -------
    List of (x, y, z) tuples, one per CYS SG atom found.

    Raises
    ------
    FileNotFoundError : if the PDB file does not exist.
    ValueError        : if no CYS SG atoms are found in the file.
    """
    if not os.path.isfile(pdb_path):
        raise FileNotFoundError(f"PDB file not found: {pdb_path}")

    coords = []
    with open(pdb_path, "r", encoding="utf-8") as fh:
        for line in fh:
            # PDB ATOM/HETATM record, columns are fixed-width
            if not (line.startswith("ATOM") or line.startswith("HETATM")):
                continue
            atom_name = line[12:16].strip()
            res_name  = line[17:20].strip()
            if res_name == "CYS" and atom_name == "SG":
                try:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    coords.append((x, y, z))
                except ValueError:
                    # Malformed coordinate field; skip this line
                    continue

    if not coords:
        raise ValueError(
            f"No CYS SG atoms found in {pdb_path}. "
            "Check that the file contains CYS residues and is in "
            "standard PDB format."
        )
    return coords


def compute_sg_centroid(pdb_path: str) -> Tuple[float, float, float]:
    """
    Compute the mean (x, y, z) of all CYS SG atoms in a PDB file.
    This is used as the focused grid center for Round 2 docking.

    Parameters
    ----------
    pdb_path : str
        Path to the protein .pdb file.

    Returns
    -------
    (cx, cy, cz) : Tuple[float, float, float]
        The centroid of all Cys sulfur atoms, rounded to 3 decimal places.
    """
    coords = find_cys_sg_coordinates(pdb_path)
    n  = len(coords)
    cx = round(sum(c[0] for c in coords) / n, 3)
    cy = round(sum(c[1] for c in coords) / n, 3)
    cz = round(sum(c[2] for c in coords) / n, 3)

    print(f"  [cys_finder] Found {n} CYS SG atoms.")
    print(f"  [cys_finder] Centroid: ({cx}, {cy}, {cz})")
    return cx, cy, cz
