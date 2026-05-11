import argparse
import os
import csv
from sanjeevani_dock.pipeline import run_pipeline


SUPPORTED_METALS = ["CD", "CU", "HG", "FE", "ZN", "PB"]



def parse_args():
    parser = argparse.ArgumentParser(
        prog="SanjeevaniDock",
        description=(
            "Automated bare heavy-metal ion docking to metallothioneins "
            "using AutoDock 4.2.6. | IISER Thiruvananthapuram, iGEM 2026."
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--pdb",
        type=str,
        help="Path to a single .pdb file.\nExample: --pdb proteins/smtA.pdb"
    )
    input_group.add_argument(
        "--pdb-dir",
        type=str,
        help="Path to a folder of .pdb files.\nExample: --pdb-dir proteins/"
    )

    metal_group = parser.add_mutually_exclusive_group(required=True)
    metal_group.add_argument(
        "--metal",
        type=str,
        choices=SUPPORTED_METALS,
        help=f"Single metal to dock. Choices: {SUPPORTED_METALS}"
    )
    metal_group.add_argument(
        "--all-metals",
        action="store_true",
        help="Dock all supported metals: CD, CU, HG, FE, ZN, PB"
    )

    parser.add_argument(
        "--focused",
        action="store_true",
        help="Use focused grid (20x20x20) centered on CYS SG centroid.\nDefault is blind (60x60x60)."
    )
    parser.add_argument(
        "--ga-runs",
        type=int,
        default=50,
        help="Number of Lamarckian GA runs. Default: 50"
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="AutoDock_Runs",
        help="Root folder for all output files. Default: AutoDock_Runs/"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Optional: save all results to this CSV file.\nExample: --csv results.csv"
    )

    return parser.parse_args()



def print_summary_table(all_results):
    print(f"\n{'='*75}")
    print(f"  SANJEEVANI DOCK --- FINAL RESULTS SUMMARY")
    print(f"{'='*75}")
    print(
        f"  {'Protein':<18} {'Metal':<6} {'Best dG (kcal/mol)':<22}"
        f" {'Cluster Size':<15} Status"
    )
    print(f"  {'-'*70}")
    for r in all_results:
        dg = f"{r['best_dG']:.3f}" if r["best_dG"] is not None else "FAILED"
        cs = str(r["cluster_size"]) if r["cluster_size"] not in (None, -1) else "N/A"
        print(
            f"  {r['protein']:<18} {r['metal']:<6} {dg:<22}"
            f" {cs:<15} {r['status']}"
        )
    print(f"{'='*75}\n")



def save_csv(all_results, csv_path):
    fieldnames = [
        "protein", "metal", "best_dG",
        "cluster_size", "interpretation", "status"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_results)
    print(f"  Results saved to: {csv_path}\n")



def main():
    args   = parse_args()
    metals = SUPPORTED_METALS if args.all_metals else [args.metal.upper()]

    if args.pdb:
        if not os.path.isfile(args.pdb):
            print(f"ERROR: PDB file not found: {args.pdb}")
            return
        pdb_files = [args.pdb]
    else:
        if not os.path.isdir(args.pdb_dir):
            print(f"ERROR: Folder not found: {args.pdb_dir}")
            return
        pdb_files = [
            os.path.join(args.pdb_dir, f)
            for f in os.listdir(args.pdb_dir)
            if f.lower().endswith(".pdb")
        ]
        if not pdb_files:
            print(f"ERROR: No .pdb files found in {args.pdb_dir}")
            return

    total = len(pdb_files) * len(metals)
    print(f"\n{'='*75}")
    print(f"  SANJEEVANI DOCK --- STARTING")
    print(f"{'='*75}")
    print(f"  Proteins  : {len(pdb_files)}")
    print(f"  Metals    : {metals}")
    print(f"  Mode      : {'Focused (Cys SG centroid)' if args.focused else 'Blind (60x60x60)'}")
    print(f"  GA runs   : {args.ga_runs}")
    print(f"  Output    : {args.out_dir}/")
    print(f"  Total runs: {total}")
    print(f"{'='*75}")

    all_results = []

    for pdb_path in pdb_files:
        protein_name = os.path.splitext(os.path.basename(pdb_path))[0]
        for metal in metals:
            output_dir = os.path.join(args.out_dir, f"{protein_name}_{metal}")
            try:
                result = run_pipeline(
                    pdb_path   = pdb_path,
                    metal_code = metal,
                    output_dir = output_dir,
                    ga_runs    = args.ga_runs,
                    blind      = not args.focused,
                )
                all_results.append({
                    "protein":        protein_name,
                    "metal":          metal,
                    "best_dG":        result["best_energy"],
                    "cluster_size":   result["cluster_size"],
                    "interpretation": result["interpretation"],
                    "status":         "OK",
                })
            except Exception as e:
                print(f"\n[ERROR] {protein_name} + {metal} failed: {e}")
                all_results.append({
                    "protein":        protein_name,
                    "metal":          metal,
                    "best_dG":        None,
                    "cluster_size":   None,
                    "interpretation": "FAILED",
                    "status":         str(e),
                })

    print_summary_table(all_results)

    if args.csv:
        save_csv(all_results, args.csv)



if __name__ == "__main__":
    main()
