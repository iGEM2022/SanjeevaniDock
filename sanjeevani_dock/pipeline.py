"""
pipeline.py
-----------
Orchestrates a full SanjeevaniDock run for one protein + one metal.
Calls modules in this order:
    cys_finder -> file_writer -> runner -> parser
"""

import os
from sanjeevani_dock.cys_finder  import compute_sg_centroid
from sanjeevani_dock.file_writer import (
    write_metals_dat,
    write_metal_pdbqt,
    write_gpf,
    write_dpf,
)
from sanjeevani_dock.runner import (
    prepare_receptor,
    run_autogrid,
    run_autodock,
)
from sanjeevani_dock.parser import summarise


def run_pipeline(
    pdb_path:   str,
    metal_code: str,
    output_dir: str,
    ga_runs:    int  = 50,
    blind:      bool = True,
) -> dict:
    """
    Run the full docking pipeline for one protein + one metal.

    Parameters
    ----------
    pdb_path   : str  - path to the protein .pdb file
    metal_code : str  - one of: CD, CU, HG, FE, ZN, PB
    output_dir : str  - folder where all output files will be written
    ga_runs    : int  - number of Lamarckian GA runs (default 50)
    blind      : bool - True  = blind docking (60x60x60, gridcenter auto)
                        False = focused docking (20x20x20, Cys SG centroid)

    Returns
    -------
    dict with keys: best_energy, all_energies, cluster_size
    """
    metal_code   = metal_code.upper()
    protein_stem = os.path.splitext(os.path.basename(pdb_path))[0]
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  SanjeevaniDock | {protein_stem} + {metal_code}")
    print(f"  Mode    : {'Blind' if blind else 'Focused'}")
    print(f"  GA runs : {ga_runs}")
    print(f"  Output  : {output_dir}")
    print(f"{'='*60}")

    # ------------------------------------------------------------------
    # Step 1 — Write AD4_metals.dat
    # ------------------------------------------------------------------
    print("\n[Step 1/8] Writing metal parameter file (AD4_metals.dat)...")
    write_metals_dat(output_dir)

    # ------------------------------------------------------------------
    # Step 2 — Prepare receptor PDBQT
    # ------------------------------------------------------------------
    pdbqt_path = os.path.join(output_dir, f"{protein_stem}.pdbqt")
    if not os.path.isfile(pdbqt_path):
        print("\n[Step 2/8] Preparing receptor PDBQT...")
        prepare_receptor(pdb_path, pdbqt_path)
    else:
        print("\n[Step 2/8] Receptor PDBQT already exists, skipping.")

    # ------------------------------------------------------------------
    # Step 3 — Write metal ion ligand PDBQT
    # ------------------------------------------------------------------
    print(f"\n[Step 3/8] Writing {metal_code} ligand PDBQT...")
    write_metal_pdbqt(output_dir, metal_code)

    # ------------------------------------------------------------------
    # Step 4 — Determine grid center
    # ------------------------------------------------------------------
    if blind:
        center   = ("auto", "", "")
        box_size = (60, 60, 60)
        print("\n[Step 4/8] Grid mode: Blind (60x60x60, auto center).")
    else:
        print("\n[Step 4/8] Grid mode: Focused — computing centroid of all CYS SG atoms...")
        cx, cy, cz = compute_sg_centroid(pdb_path)
        center     = (cx, cy, cz)
        box_size   = (20, 20, 20)

    # ------------------------------------------------------------------
    # Step 5 — Write GPF
    # ------------------------------------------------------------------
    print("\n[Step 5/8] Writing GPF (AutoGrid parameter file)...")
    gpf_path = write_gpf(
        output_dir, protein_stem, metal_code, center,
        grid_config={"box_size": box_size, "spacing": 0.375}
    )

    # ------------------------------------------------------------------
    # Step 6 — Write DPF
    # ------------------------------------------------------------------
    print("\n[Step 6/8] Writing DPF (AutoDock parameter file)...")
    dpf_path = write_dpf(output_dir, protein_stem, metal_code, ga_runs)

    # ------------------------------------------------------------------
    # Step 7 — Pre-run sanity check
    # ------------------------------------------------------------------
    print("\n[Step 7/8] Pre-run sanity check...")
    required_files = [
        os.path.join(output_dir, f"{protein_stem}.pdbqt"),
        os.path.join(output_dir, f"{metal_code.lower()}.pdbqt"),
        os.path.join(output_dir, "AD4_metals.dat"),
        gpf_path,
        dpf_path,
    ]
    all_ok = True
    for f in required_files:
        exists = os.path.isfile(f)
        status = "OK     " if exists else "MISSING"
        print(f"  [{status}] {os.path.basename(f)}")
        if not exists:
            all_ok = False

    if not all_ok:
        raise RuntimeError(
            "One or more required files are missing. "
            "Check the errors above before proceeding."
        )
    print("  All files present. Proceeding to docking.")

    # ------------------------------------------------------------------
    # Step 8 — Run AutoGrid then AutoDock
    # ------------------------------------------------------------------
    stem     = f"{protein_stem}_{metal_code.lower()}"
    glg_path = os.path.join(output_dir, f"{stem}.glg")
    dlg_path = os.path.join(output_dir, f"{stem}.dlg")

    print("\n[Step 8/8] Running AutoGrid4...")
    run_autogrid(gpf_path, glg_path)

    print("\n[Step 8/8] Running AutoDock4 (this may take 5-20 minutes)...")
    run_autodock(dpf_path, dlg_path)

    # ------------------------------------------------------------------
    # Parse and return results
    # ------------------------------------------------------------------
    print("\n[Results] Parsing .dlg output file...")
    results = summarise(dlg_path)

    print(f"\n{'='*60}")
    print(f"  RESULTS : {protein_stem} + {metal_code}")
    print(f"  Best dG        : {results['best_energy']} kcal/mol")
    print(f"  Top cluster    : {results['cluster_size']} runs")
    print(f"{'='*60}\n")

    return results
