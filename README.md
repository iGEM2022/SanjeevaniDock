# SanjeevaniDock

Automated bare heavy-metal ion docking to metallothionein proteins
using AutoDock 4.2.6.

Developed by the **IISER Thiruvananthapuram iGEM 2026 Dry Lab** as part of
**Project Sanjeevani** — a moss-based heavy metal bioremediation system.

---

## What it does

Given a protein PDB file and a target metal, SanjeevaniDock automatically:

1. Writes `AD4_metals.dat` with calibrated Lennard-Jones parameters
2. Converts the protein to PDBQT using MGLTools `prepare_receptor4.py`
3. Writes a bare metal ion `.pdbqt` ligand file manually
4. Computes the CYS SG centroid for focused docking
5. Generates the `.gpf` and `.dpf` parameter files
6. Runs AutoGrid4 and AutoDock4 in the background
7. Parses the `.dlg` output and prints a results table
8. Optionally exports everything to a `.csv` file

---

## Supported metals

| Metal   | Code | Charge | Role                       |
|---------|------|--------|----------------------------|
| Cadmium | CD   | +2     | Primary MT substrate       |
| Copper  | CU   | +2     | Primary MT substrate       |
| Mercury | HG   | +2     | Primary MT substrate       |
| Iron    | FE   | +2     | Negative control           |
| Zinc    | ZN   | +2     | Physiological MT substrate |
| Lead    | PB   | +2     | Environmental contaminant  |

---

## Prerequisites

1. **Python 3.8+**
2. **MGLTools 1.5.7** — https://ccsb.scripps.edu/mgltools/downloads/
3. **AutoDock 4.2.6** — https://autodock.scripps.edu/download-autodock4/

Both `autogrid4` and `autodock4` must be on your system PATH.
See Pipeline B Step 1 of the Project Sanjeevani handout.

---

## Installation

```bash
git clone https://github.com/YOUR-TEAM/sanjeevani-dock.git
cd sanjeevani-dock
pip3 install -e .
```

---

## Usage

```bash
# Single protein, single metal
python3 run_dock.py --pdb proteins/smtA.pdb --metal CD

# Single protein, all metals
python3 run_dock.py --pdb proteins/smtA.pdb --all-metals

# Focused docking
python3 run_dock.py --pdb proteins/smtA.pdb --all-metals --focused

# All proteins, all metals, save to CSV
python3 run_dock.py --pdb-dir proteins/ --all-metals --csv results.csv

# Custom GA runs
python3 run_dock.py --pdb proteins/smtA.pdb --metal CD --ga-runs 100
```

---

## Output folder structure

Each protein-metal pair gets its own subfolder inside `AutoDock_Runs/`:

    AutoDock_Runs/
    └── smtA_CD/
        ├── AD4_metals.dat
        ├── smtA.pdbqt
        ├── cd.pdbqt
        ├── smtA_cd.gpf
        ├── smtA_cd.dpf
        ├── smtA_cd.glg
        └── smtA_cd.dlg

The `.glg` file is the AutoGrid log. The `.dlg` file is the AutoDock
results file and is the one SanjeevaniDock parses for binding energies.

---

## Interpreting results

| dG (kcal/mol) | Interpretation                       |
|---------------|--------------------------------------|
| < -10         | Very strong binding                  |
| -10 to -7     | Strong (exceeds drug-like threshold) |
| -7 to -5      | Moderate binding                     |
| > -5          | Weak or non-specific binding         |

Fe2+ is used as a negative control. Its dG should always be weaker
(less negative) than Cd2+, Cu2+, and Hg2+. A strong Fe2+ score
indicates non-specific electrostatic attraction, not real coordination.

---

## Citation

> IISER Thiruvananthapuram iGEM 2026 Dry Lab. *SanjeevaniDock: Automated
> heavy metal ion docking to metallothioneins using AutoDock 4.2.6.*
> GitHub, 2026.

---

## License

MIT License.