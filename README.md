# SanjeevaniDock

Automated docking of **bare heavy-metal ions** to **metallothionein proteins** using **AutoDock 4.2.6**.

Developed by the **IISER Thiruvananthapuram iGEM 2026 Dry Lab** as part of **Project Sanjeevani**, a moss-based heavy-metal bioremediation system.

---

## Overview

SanjeevaniDock automates the full AutoDock 4 workflow for **single metal ions** such as Cd²⁺, Cu²⁺, Hg²⁺, Fe²⁺, Zn²⁺, and Pb²⁺ docked against metallothionein proteins. It is specifically designed for **bare metal ions**, a case that standard GUI-based ligand preparation does not handle cleanly.

Given a protein `.pdb` file and a target metal, SanjeevaniDock automatically:

1. Writes `AD4_metals.dat` with custom heavy-metal parameters (see [Metal parameters](#metal-parameters))
2. Converts the protein to PDBQT using MGLTools `prepare_receptor4.py`
3. Writes the bare metal ion ligand `.pdbqt` file manually
4. Computes the centroid of all cysteine `SG` atoms for focused docking
5. Generates AutoGrid (`.gpf`) and AutoDock (`.dpf`) parameter files
6. Runs `autogrid4` and `autodock4`
7. Parses the `.dlg` output and prints a results table
8. Optionally exports results to `.csv`

---

## Supported metals

| Metal   | Code | Charge | Notes |
|---------|------|--------|-------|
| Cadmium | `CD` | +2 | Target metal |
| Copper  | `CU` | +2 | Target metal (modelled as Cu²⁺) |
| Mercury | `HG` | +2 | MT substrate |
| Iron    | `FE` | +2 | Target metal |
| Zinc    | `ZN` | +2 | Physiological MT substrate |
| Lead    | `PB` | +2 | Environmental contaminant |

All metals are docked as bare +2 ions. See [Metal parameters](#metal-parameters) for what that does and does not mean.

---

## Quick start (Windows)

### 1. Install required software

Install the following first:

1. **Python 3.8 or newer**
2. **MGLTools 1.5.7**  
   https://ccsb.scripps.edu/mgltools/downloads/
3. **AutoDock 4.2.6**  
   https://autodock.scripps.edu/download-autodock4/

If MGLTools is not in its default location (`C:\Program Files (x86)\MGLTools-1.5.7`), set the `MGLTOOLS_DIR` environment variable to its install folder before running.

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

## Receptor structures

The `proteins/` folder holds the receptor files. Each structure, its UniProt accession, length, cysteine count and confidence is listed in [`proteins/README.md`](proteins/README.md).

The metallothionein models are unmodified **AlphaFold** predictions of the apo (metal-free) protein, with low-to-moderate confidence (mean pLDDT roughly 48-64). Metallothioneins fold around their bound metals, so treat these models as approximate cysteine-cluster geometries, not as resolved binding sites.

---

## Important assumptions and limitations

Before using the software, note the following:

- This tool is designed for **bare metal ions**, not organic ligands or metal complexes.
- Input proteins must already exist as valid `.pdb` structure files.
- AutoDock scores are used for **ranking and prioritization only**.
- Docking energies from this tool are **not experimental Kd values**.
- **Scores are not comparable between metals.** The metal parameters are empirical (see below), and the metal-to-metal ordering follows them. Compare proteins against each other **for the same metal**, not one metal against another.
- **A cluster size of 50/50 is expected for a single atom** and is not evidence of reproducibility (see [Interpreting results](#interpreting-results)).
- **Focused docking is only meaningful for single-domain proteins.** Its grid is centred on the centroid of *all* cysteine `SG` atoms. For a multi-domain metallothionein (for example the type 4 proteins, which have two cysteine-rich domains) that centroid lies between the domains, and part of the cysteine content falls outside the 20 Å box. For multi-domain proteins use the blind (default) mode, or dock each cysteine cluster separately.
- Copper is modelled as **Cu²⁺**. Metal-bound copper in metallothioneins is normally Cu(I)-thiolate, so Cu²⁺ results should not be read as a model of the biological state.

---

## Metal parameters

AutoDock 4 has no built-in parameters for most heavy metals, so SanjeevaniDock writes its own `AD4_metals.dat`. AutoDock loads its default library first, so this file works as an addition to it.

**These parameters are empirical.** They were set by the IISER TVM Dry Lab. They are **not** taken from a published force field and were **not** fitted to, or validated against, experimental binding data. The `ZN` `Rii` (1.48) equals AutoDock's built-in zinc value, but `epsii` and `vol` do not (AutoDock: 0.550 and 1.700). All `vol` values here (10-16) are much larger than AutoDock's own metal volumes (about 1.7-2.8), and their effect on scores has not been tested. For Cd, Cu, Hg and Pb the `Rii` value falls at roughly 0.8-0.9 × the Shannon (1976) six-coordinate ionic diameter, but this is an observation about the numbers, not a derivation.

| Code | Rii (Å) | epsii (kcal/mol) | vol (Å³) | solv | Charge |
|------|---------|------------------|----------|------|--------|
| `FE` | 1.20 | 0.050 | 11.000 | -0.00110 | +2 |
| `CU` | 1.30 | 0.050 | 10.000 | -0.00110 | +2 |
| `ZN` | 1.48 | 0.250 | 13.438 | -0.00110 | +2 |
| `CD` | 1.58 | 0.250 | 12.000 | -0.00110 | +2 |
| `HG` | 1.70 | 0.300 | 14.000 | -0.00110 | +2 |
| `PB` | 1.90 | 0.400 | 16.000 | -0.00110 | +2 |

Every ligand has `TORSDOF 0` and charge +2.000.

### What this means for the results

In our own runs on nine metallothionein structures, the metal order by docking score was **the same as the `Rii` order for every protein** (the smallest ion, Fe, scored most negative; the largest, Pb, least negative). Across proteins, the ranking was also very similar from one metal to the next. So:

- The metal-to-metal differences mainly reflect the chosen parameters (ion size and charge), not metal-specific coordination chemistry.
- Results for different metals on the same protein are **not independent** evidence.
- Pb scoring weakest and Fe scoring strongest are properties of these parameters. They should not be used to say anything about the real affinity of a protein for those metals.

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
- No other options → one protein, one metal, default (blind) docking mode

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

The exact numbers will vary (the genetic algorithm is seeded from the process ID and time). The final output looks like this, with illustrative values:

```text
  Protein            Metal  Best dG (kcal/mol)     Cluster Size    Status
  smtA               CD     -8.400                 50              OK
```

Interpretation:
- More negative `Best dG` = better predicted binding **for that metal**
- Cluster size: see [Interpreting results](#interpreting-results)

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

Read the focused-docking limitation under [Important assumptions and limitations](#important-assumptions-and-limitations) before using this on multi-domain proteins.

### All proteins in one directory, all metals, export CSV

```bash
python run_dock.py --pdb-dir proteins/ --all-metals --csv results.csv
```

### Custom number of GA runs

```bash
python run_dock.py --pdb proteins/smtA.pdb --metal CD --ga-runs 100
```

---

## Docking modes

| Mode | Flag | Grid |
|------|------|------|
| Blind (default) | none | 60 × 60 × 60 Å, `gridcenter auto`, spacing 0.375 Å |
| Focused | `--focused` | 20 × 20 × 20 Å centred on the centroid of all cysteine `SG` atoms, spacing 0.375 Å |

Both modes use the Lamarckian genetic algorithm, 50 runs by default.

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
| `--out-dir DIR` | Root folder for output files (default `AutoDock_Runs/`) |

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

SanjeevaniDock reports the lowest "Estimated Free Energy of Binding" across all GA runs, and the population of the top cluster.

### Docking score

- These values are **docking scores**, not experimental free energies, and there is no absolute threshold that separates "strong" from "weak" binding for a bare ion with empirical parameters.
- Use them to **rank proteins against each other for one metal**, in one docking mode.
- Do not compare a score for one metal with a score for another (see [Metal parameters](#metal-parameters)).
- Do not mix blind and focused scores into one number. Average and report them separately.
- Scores from separate runs of the same job can differ slightly, since the GA is seeded from time. Where possible, repeat runs and report mean ± standard deviation.

### Cluster size

For a **single-atom ligand**, the search converges trivially: in our runs every one of the 50 GA runs ended at the same grid position, giving a top cluster of 50/50. A large cluster size therefore does **not** show that the result is reproducible or that the site is specific. Do not use it as a quality filter for this tool.

---

## Troubleshooting

### `autodock4` is not recognized
AutoDock 4 is not on your system `PATH`. Reinstall AutoDock or add the folder containing `autodock4.exe` and `autogrid4.exe` to your system environment variables.

### `autogrid4` is not recognized
Same issue as above: AutoGrid is not on your system `PATH`.

### `prepare_receptor4.py` fails
Make sure **MGLTools 1.5.7** is installed correctly. SanjeevaniDock depends on the MGLTools receptor-preparation script even though it does not use the GUI. If MGLTools is installed outside the default folder, set `MGLTOOLS_DIR` (see Quick start).

### Python version problems
SanjeevaniDock itself uses **Python 3**, but MGLTools was historically distributed with older tooling. If receptor preparation fails, verify that the required preparation script path is valid on your machine.

### No cysteine `SG` atoms found
Focused docking depends on cysteine sulfur atoms. If your structure contains no `CYS` residues or the PDB file is malformed, focused docking will fail.

### `.dlg` file missing or empty
This usually means AutoDock did not finish successfully. Check:
- whether `autogrid4` completed successfully,
- whether the `.gpf` and `.dpf` files were written correctly,
- and whether the AutoDock executables are callable from the command line.

### One metal scores much better than the others across many proteins
Expected. Scores follow the metal parameters (mostly ion size), so a small ion such as Fe²⁺ will score more negatively than a large one such as Pb²⁺ on almost any protein. See [Metal parameters](#metal-parameters).

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

If you use the AlphaFold structures in `proteins/`, also cite the AlphaFold papers listed in [`proteins/README.md`](proteins/README.md).

---

## License

MIT License. See the `LICENSE` file.
