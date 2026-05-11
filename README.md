# SanjeevaniDock

Automated docking of **bare heavy-metal ions** to **metallothionein proteins** using **AutoDock 4.2.6**.

Developed by the **IISER Thiruvananthapuram iGEM 2026 Dry Lab** as part of **Project Sanjeevani**, a moss-based heavy-metal bioremediation system.

---

## Overview

SanjeevaniDock automates the full AutoDock 4 workflow for **single metal ions** such as Cd²⁺, Cu²⁺, Hg²⁺, Fe²⁺, Zn²⁺, and Pb²⁺ docked against metallothionein proteins. It is specifically designed for **bare metal ions**, a case that standard GUI-based ligand preparation does not handle cleanly.

Given a protein `.pdb` file and a target metal, SanjeevaniDock automatically:

1. Writes `AD4_metals.dat` with custom heavy-metal parameters
2. Converts the protein to PDBQT using MGLTools `prepare_receptor4.py`
3. Writes the bare metal ion ligand `.pdbqt` file manually
4. Computes the centroid of all cysteine `SG` atoms for focused docking
5. Generates AutoGrid (`.gpf`) and AutoDock (`.dpf`) parameter files
6. Runs `autogrid4` and `autodock4`
7. Parses the `.dlg` output and prints a results table
8. Optionally exports results to `.csv`

---

## Supported metals

| Metal   | Code | Charge | Role |
|---------|------|--------|------|
| Cadmium | `CD` | +2 | Primary MT substrate |
| Copper  | `CU` | +2 | Primary MT substrate |
| Mercury | `HG` | +2 | Primary MT substrate |
| Iron    | `FE` | +2 | Negative control |
| Zinc    | `ZN` | +2 | Physiological MT substrate |
| Lead    | `PB` | +2 | Environmental contaminant |

---

## Quick start (Windows)

### 1. Install required software

Install the following first:

1. **Python 3.8 or newer**
2. **MGLTools 1.5.7**  
   https://ccsb.scripps.edu/mgltools/downloads/
3. **AutoDock 4.2.6**  
   https://autodock.scripps.edu/download-autodock4/

### 2. Make sure AutoDock executables are available

Open **PowerShell** or **Command Prompt** and check:

```bash
autodock4
autogrid4
```

Both commands should print a usage message. If either command is not recognized, AutoDock is not on your system `PATH`.

### 3. Clone the repository

```bash
git clone https://github.com/iGEM2022/SanjeevaniDock.git
cd SanjeevaniDock
```

### 4. Install the package

```bash
pip install -e .
```

> `-e` means **editable install**. This is useful because if the code is updated locally, you do not need to reinstall the package each time.

### 5. Run one test job

```bash
python run_dock.py --pdb proteins/smtA.pdb --metal CD
```

If the run succeeds, SanjeevaniDock will:
- create a folder inside `AutoDock_Runs/`
- generate `.pdbqt`, `.gpf`, `.dpf`, `.glg`, and `.dlg` files
- print a small results table in the terminal

---

## Why MGLTools is required

SanjeevaniDock does **not** use the AutoDock GUI. However, it still requires **MGLTools** because the command-line script `prepare_receptor4.py` is used to convert protein `.pdb` files into AutoDock-compatible `.pdbqt` format.

So even though this pipeline is fully CLI-based, **MGLTools is still essential**.

---

## Important assumptions

Before using the software, note the following:

- This tool is designed for **bare metal ions**, not organic ligands or metal complexes.
- Input proteins must already exist as valid `.pdb` structure files.
- Focused docking uses the centroid of **cysteine sulfur (`SG`) atoms**, not alpha carbons.
- AutoDock scores are used for **ranking and prioritization only**.
- Docking energies from this tool are **not experimental \(K_d\) values**.
- **Fe²⁺** is included as a negative control and should usually bind more weakly than Cd²⁺, Cu²⁺, and Hg²⁺.

---

## Installation details

If you have already cloned the repository, run:

```bash
cd SanjeevaniDock
pip install -e .
```

If you are using a virtual environment, activate it first.

---

## First successful run

Run this exact command first:

```bash
python run_dock.py --pdb proteins/smtA.pdb --metal CD
```

### What this command means

- `--pdb proteins/smtA.pdb` → use `smtA.pdb` as the receptor protein
- `--metal CD` → dock **cadmium**
- No other options → one protein, one metal, default docking mode

### Expected output files

This command should create a directory like:

```text
AutoDock_Runs/
└── smtA_CD/
    ├── AD4_metals.dat
    ├── smtA.pdbqt
    ├── cd.pdbqt
    ├── smtA_cd.gpf
    ├── smtA_cd.dpf
    ├── smtA_cd.glg
    └── smtA_cd.dlg
```

### Expected terminal output

The exact numbers will vary, but the final output should look something like this:

```text
Protein  Metal  Best_dG  Cluster_size
smtA     CD     -8.4     17
```

Interpretation:
- More negative `Best_dG` = stronger predicted binding
- Larger `Cluster_size` = better convergence across docking runs

---

## Usage

### Single protein, single metal

```bash
python run_dock.py --pdb proteins/smtA.pdb --metal CD
```

### Single protein, all supported metals

```bash
python run_dock.py --pdb proteins/smtA.pdb --all-metals
```

### Focused docking around cysteine sulfur centroid

```bash
python run_dock.py --pdb proteins/smtA.pdb --all-metals --focused
```

### All proteins in one directory, all metals, export CSV

```bash
python run_dock.py --pdb-dir proteins/ --all-metals --csv results.csv
```

### Custom number of GA runs

```bash
python run_dock.py --pdb proteins/smtA.pdb --metal CD --ga-runs 100
```

---

## Command-line options

| Flag | Meaning |
|------|---------|
| `--pdb FILE` | Dock one protein structure file |
| `--pdb-dir DIR` | Dock all `.pdb` files in a directory |
| `--metal CODE` | Dock one specific metal only |
| `--all-metals` | Dock all supported metals |
| `--focused` | Use focused docking centered on the cysteine `SG` centroid |
| `--csv FILE` | Save parsed results to a CSV file |
| `--ga-runs N` | Set the number of AutoDock GA runs manually |

### Supported metal codes

Use one of the following with `--metal`:

- `CD`
- `CU`
- `HG`
- `FE`
- `ZN`
- `PB`

---

## Output folder structure

Each protein–metal pair gets its own subfolder inside `AutoDock_Runs/`:

```text
AutoDock_Runs/
└── smtA_CD/
    ├── AD4_metals.dat
    ├── smtA.pdbqt
    ├── cd.pdbqt
    ├── smtA_cd.gpf
    ├── smtA_cd.dpf
    ├── smtA_cd.glg
    └── smtA_cd.dlg
```

### What the main files mean

- `AD4_metals.dat` → custom AutoDock metal parameters
- `*.pdbqt` → AutoDock-formatted receptor and ligand files
- `*.gpf` → AutoGrid parameter file
- `*.dpf` → AutoDock parameter file
- `*.glg` → AutoGrid log file
- `*.dlg` → AutoDock docking log file containing the docking results

The `.dlg` file is the main output that SanjeevaniDock parses to extract binding energies and cluster sizes.

---

## Interpreting results

| dG (kcal/mol) | Interpretation |
|---------------|----------------|
| `< -10` | Very strong binding |
| `-10 to -7` | Strong binding |
| `-7 to -5` | Moderate binding |
| `> -5` | Weak or non-specific binding |

### Notes on interpretation

- These values are **docking scores**, not experimental free energies.
- Use them to **rank candidates**, not to make absolute thermodynamic claims.
- A good metallothionein candidate should usually bind **Cd²⁺, Cu²⁺, or Hg²⁺** more strongly than **Fe²⁺**.
- If Fe²⁺ docks unusually well, treat that as a possible non-specific electrostatic artifact rather than real coordination chemistry.

---

## Troubleshooting

### `autodock4` is not recognized
AutoDock 4 is not on your system `PATH`. Reinstall AutoDock or add the folder containing `autodock4.exe` and `autogrid4.exe` to your system environment variables.

### `autogrid4` is not recognized
Same issue as above: AutoGrid is not on your system `PATH`.

### `prepare_receptor4.py` fails
Make sure **MGLTools 1.5.7** is installed correctly. SanjeevaniDock depends on the MGLTools receptor-preparation script even though it does not use the GUI.

### Python version problems
SanjeevaniDock itself uses **Python 3**, but MGLTools was historically distributed with older tooling. If receptor preparation fails, verify that the required preparation script path is valid on your machine.

### No cysteine `SG` atoms found
Focused docking depends on cysteine sulfur atoms. If your structure contains no `CYS` residues or the PDB file is malformed, focused docking will fail.

### `.dlg` file missing or empty
This usually means AutoDock did not finish successfully. Check:
- whether `autogrid4` completed successfully,
- whether the `.gpf` and `.dpf` files were written correctly,
- and whether the AutoDock executables are callable from the command line.

### Strange Fe²⁺ results
Fe²⁺ is a negative control. If Fe²⁺ appears stronger than Cd²⁺, Cu²⁺, or Hg²⁺ across many proteins, inspect the result manually before accepting it.

---

## Recommended volunteer workflow

For new users, the safest workflow is:

1. Clone the repo
2. Install dependencies
3. Run one known test job on `proteins/smtA.pdb`
4. Confirm the expected output folder is created
5. Only then move to batch docking of multiple proteins

This prevents large batch failures caused by installation or path problems.

---

## Citation

If you use SanjeevaniDock in presentations, reports, or the iGEM wiki, cite it as:

> IISER Thiruvananthapuram iGEM 2026 Dry Lab. *SanjeevaniDock: Automated bare heavy-metal ion docking to metallothioneins using AutoDock 4.2.6.* GitHub, 2026.

---

## License

MIT License.
