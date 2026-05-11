"""
runner.py
---------
Calls the AutoDock4 executables (autogrid4, autodock4) via subprocess,
captures stdout/stderr, and checks for the "Successful Completion"
string in the AutoGrid log.


IMPORTANT: All subprocess calls use the MGLTools Python 2.7 interpreter
explicitly when preparing the receptor, to avoid the Python 2 vs. 3
conflict (prepare_receptor4.py uses Python 2 print syntax and will
raise SyntaxError if run under Python 3).
"""


import subprocess
import os
import sys


# Default paths --- users can override via environment variables
MGLTOOLS_DIR = os.environ.get(
    "MGLTOOLS_DIR",
    r"C:\Program Files (x86)\MGLTools-1.5.7"
)
MGLTOOLS_PYTHON = os.path.join(MGLTOOLS_DIR, "python.exe")
PREPARE_RECEPTOR = os.path.join(
    MGLTOOLS_DIR,
    r"Lib\site-packages\AutoDockTools\Utilities24\prepare_receptor4.py"
)



def prepare_receptor(pdb_path: str, pdbqt_path: str) -> None:
    """
    Convert a protein PDB to PDBQT using MGLTools prepare_receptor4.py.

    Uses the MGLTools-bundled Python 2.7 interpreter explicitly.
    A non-integral charge warning is expected for metal-binding proteins
    and does NOT indicate an error.

    Parameters
    ----------
    pdb_path   : str - path to input .pdb file
    pdbqt_path : str - path to output .pdbqt file
    """
    print(f"\n[runner] Preparing receptor: {pdb_path} -> {pdbqt_path}")
    print("[runner] NOTE: 'Non-integral charge' warnings are expected "
          "for metal-binding proteins. They do not invalidate the run.")

    cmd = [
        MGLTOOLS_PYTHON,
        PREPARE_RECEPTOR,
        "-r", pdb_path,
        "-o", pdbqt_path,
        "-A", "checkhydrogens"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    # Print warnings (non-fatal) but don't suppress them
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"[runner] STDERR: {result.stderr}", file=sys.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"prepare_receptor4.py failed with return code {result.returncode}.\n"
            f"STDERR: {result.stderr}"
        )
    print("[runner] Receptor preparation complete.")



def run_autogrid(gpf_path: str, glg_path: str) -> None:
    """
    Run AutoGrid4 on a .gpf file and write log to .glg.
    Verifies that the log contains "Successful Completion".

    Parameters
    ----------
    gpf_path : str - path to the .gpf file
    glg_path : str - path for the output .glg log file
    """
    # Run from the directory containing the GPF file so that
    # AutoGrid4 can find AD4_metals.dat in the same folder
    working_dir = os.path.dirname(os.path.abspath(gpf_path))
    gpf_name    = os.path.basename(gpf_path)
    glg_name    = os.path.basename(glg_path)

    print(f"\n[runner] Running AutoGrid4: {gpf_path}")
    cmd    = ["autogrid4", "-p", gpf_name, "-l", glg_name]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=working_dir
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"AutoGrid4 failed (return code {result.returncode}).\n"
            f"STDERR: {result.stderr}\n"
            f"Check the log file: {glg_path}"
        )

    # Verify successful completion in the log
    if os.path.isfile(glg_path):
        with open(glg_path, "r", encoding="ascii", errors="replace") as fh:
            log_content = fh.read()
        if "Successful Completion" not in log_content:
            raise RuntimeError(
                f"AutoGrid4 did not report 'Successful Completion'.\n"
                f"Check the log file for errors: {glg_path}"
            )
    print("[runner] AutoGrid4 completed successfully.")



def run_autodock(dpf_path: str, dlg_path: str = None) -> None:
    """
    Run AutoDock4 on a .dpf file and write log to .dlg.

    Parameters
    ----------
    dpf_path : str - path to the .dpf file
    dlg_path : str - reserved for future result validation
    """
    # dlg_path reserved for future result validation
    _ = dlg_path

    # Run from the directory containing the DPF file so that
    # AutoDock4 can find all map files in the same folder
    working_dir = os.path.dirname(os.path.abspath(dpf_path))
    dpf_name    = os.path.basename(dpf_path)

    print(f"\n[runner] Running AutoDock4: {dpf_path}")
    print("[runner] This may take 5-20 minutes depending on the system and parameters.")
    cmd    = ["autodock4", "-p", dpf_name]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=working_dir
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"AutoDock4 failed (return code {result.returncode}).\n"
            f"STDERR: {result.stderr}"
        )
    print("[runner] AutoDock4 completed successfully.")
