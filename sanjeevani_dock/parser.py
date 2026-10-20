"""
parser.py
---------
Extracts binding free energy (delta G) and cluster size from
an AutoDock4 .dlg log file.

Notes on interpretation
-----------------------
The values returned here are docking scores for ranking only. They are not
experimental free energies, and no absolute threshold separates "strong" from
"weak" binding for a bare metal ion with empirical parameters. Compare
proteins within the same metal and docking mode.

For a single-atom ligand every GA run converges to the same position, so the
top cluster normally contains all runs (for example 50 of 50). The cluster
size is therefore not a measure of reproducibility or site specificity.
"""


import os
import re
from typing import List


# Per-run energies are written as lines such as
#   "DOCKED: USER    Estimated Free Energy of Binding    =   -8.84 kcal/mol ..."
# The ranked cluster representative is repeated later in the file without the
# "DOCKED:" prefix, so matching only the prefixed lines counts each run once.
_RUN_ENERGY = re.compile(
    r"^DOCKED:\s+USER\s+Estimated Free Energy of Binding\s*=\s*(-?\d+(?:\.\d+)?)"
)
# Looser pattern, used only if the prefixed lines are not found.
_ANY_ENERGY = re.compile(
    r"Estimated Free Energy of Binding\s*=\s*(-?\d+(?:\.\d+)?)"
)



def extract_energies(dlg_path: str) -> List[float]:
    """
    Extract the 'Estimated Free Energy of Binding' of each GA run from a
    .dlg file. Returns a list of floats (one per GA run), sorted lowest to
    highest.
    """
    if not os.path.isfile(dlg_path):
        raise FileNotFoundError(f".dlg file not found: {dlg_path}")

    with open(dlg_path, "r", encoding="ascii", errors="replace") as fh:
        lines = fh.readlines()

    energies = [float(m.group(1)) for m in map(_RUN_ENERGY.match, lines) if m]

    if not energies:
        # Fallback for unusual dlg layouts: take every matching line.
        energies = [float(m.group(1)) for m in map(_ANY_ENERGY.search, lines) if m]

    if not energies:
        raise ValueError(
            f"No energy values found in {dlg_path}. "
            "Check that AutoDock ran to completion."
        )
    return sorted(energies)



def extract_top_cluster_size(dlg_path: str) -> int:
    """
    Find the population of Cluster 1 from the CLUSTERING HISTOGRAM
    section of the .dlg file.
    """
    with open(dlg_path, "r", encoding="ascii", errors="replace") as fh:
        lines = fh.readlines()

    in_histogram = False
    for line in lines:
        if "CLUSTERING HISTOGRAM" in line:
            in_histogram = True
            continue
        if in_histogram:
            stripped = line.strip()
            # Skip header lines and empty lines
            if not stripped or stripped.startswith("Clus") or stripped.startswith("-ter"):
                continue
            # First data line is Cluster 1
            # Format: "1   -4.64   38   -4.64   50"
            parts = stripped.split()
            if parts and parts[0] == "1":
                try:
                    return int(parts[4])
                except (IndexError, ValueError):
                    pass
            break

    # Fallback: look for "Number of conformations in this cluster"
    for line in lines:
        if "Number of conformations in this cluster" in line:
            parts = line.strip().split()
            try:
                return int(parts[-1])
            except (IndexError, ValueError):
                pass

    return -1



def summarise(dlg_path: str) -> dict:
    """
    Full summary of a .dlg result file.

    Returns
    -------
    dict with keys:
        best_energy  : float - lowest (most negative) docking score, kcal/mol
        all_energies : list  - one score per GA run, sorted
        cluster_size : int   - population of top cluster (-1 if unknown)
    """
    energies     = extract_energies(dlg_path)
    best         = energies[0]
    cluster_size = extract_top_cluster_size(dlg_path)

    return {
        "best_energy":  best,
        "all_energies": energies,
        "cluster_size": cluster_size,
    }
