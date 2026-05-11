"""
parser.py
---------
Extracts binding free energy (delta G) and cluster size from
an AutoDock4 .dlg log file.
"""


import os
import re
from typing import List



def extract_energies(dlg_path: str) -> List[float]:
    """
    Extract all 'Estimated Free Energy of Binding' values from a .dlg file.
    Returns a list of floats (one per GA run), sorted lowest to highest.
    """
    if not os.path.isfile(dlg_path):
        raise FileNotFoundError(f".dlg file not found: {dlg_path}")

    energies = []
    pattern  = re.compile(
        r"Estimated Free Energy of Binding\s*=\s*([-\d.]+)"
    )
    with open(dlg_path, "r", encoding="ascii", errors="replace") as fh:
        for line in fh:
            match = pattern.search(line)
            if match:
                energies.append(float(match.group(1)))

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



def interpret_energy(delta_g: float) -> str:
    if delta_g < -10:
        return "Very strong binding"
    if delta_g < -7:
        return "Strong binding (exceeds drug-like threshold)"
    if delta_g < -5:
        return "Moderate binding"
    return "Weak or non-specific binding"



def summarise(dlg_path: str) -> dict:
    """
    Full summary of a .dlg result file.

    Returns
    -------
    dict with keys:
        best_energy    : float  - lowest (most negative) delta G
        all_energies   : list   - all extracted energies, sorted
        cluster_size   : int    - population of top cluster (-1 if unknown)
        interpretation : str    - human-readable binding strength label
    """
    energies     = extract_energies(dlg_path)
    best         = energies[0]
    cluster_size = extract_top_cluster_size(dlg_path)

    return {
        "best_energy":    best,
        "all_energies":   energies,
        "cluster_size":   cluster_size,
        "interpretation": interpret_energy(best),
    }
