#!/usr/bin/env python3

import argparse
import os
import pandas as pd
import csv
import sys
import glob

def find_image(bids_root, deriv_subdir, subject, session, desc, modality):
    """
    Search for a file in derivatives/<deriv_subdir>/<subject>/<session>
    matching *desc-{desc}_{modality}.nii.gz
    """
    anat_dir = os.path.join(
        bids_root, "derivatives", deriv_subdir,
        subject, session
    )

    if not os.path.isdir(anat_dir):
        print(f"[WARNING] Folder does not exist: {anat_dir}")
        return ""

    pattern = f"*desc-{desc}_{modality}.nii.gz"
    candidates = glob.glob(os.path.join(anat_dir, pattern))

    if not candidates:
        print(f"[WARNING] No file found for desc={desc}, modality={modality} in {anat_dir}")
        return ""

    return candidates[0]

def main():
    parser = argparse.ArgumentParser(
        description="Create CSV with one line per pattern per subject (e.g., flipped / warped)"
    )
    parser.add_argument(
        "-i", "--input-csv", required=True,
        help="Input CSV with 'subject' and 'session' columns"
    )
    parser.add_argument(
        "--modalities", nargs="+", required=True,
        help="List of modalities to look for (e.g., T1w T2w label-WM_mask)"
    )
    parser.add_argument(
        "--pattern", nargs="+", required=True,
        help="List of desc patterns to include (e.g., flipped warped)"
    )
    parser.add_argument(
        "-b", "--bids-root", required=True,
        help="BIDS root folder"
    )
    parser.add_argument(
        "--deriv-subdir", default="warped",
        help="Subdirectory under derivatives (default: warped)"
    )
    parser.add_argument(
        "-o", "--output-csv", default="output_list.csv",
        help="Output CSV file (no header)"
    )
    args = parser.parse_args()

    # Load input CSV
    try:
        df = pd.read_csv(args.input_csv)
    except Exception as e:
        print(f"[ERROR] Could not read CSV: {e}")
        sys.exit(1)

    for col in ["subject", "session"]:
        if col not in df.columns:
            print(f"[ERROR] Input CSV is missing column: {col}")
            print(f"[INFO] Found columns: {list(df.columns)}")
            sys.exit(1)

    rows = []

    for idx, row in df.iterrows():
        subject = str(row["subject"]).strip()
        session = str(row["session"]).strip()

        if not subject or not session:
            print(f"[WARNING] Missing subject or session at row {idx}. Skipping.")
            continue

        for desc in args.pattern:
            out_row = []
            for modality in args.modalities:
                path = find_image(
                    args.bids_root, args.deriv_subdir,
                    subject, session, desc, modality
                )
                out_row.append(path)
            rows.append(out_row)

    # Write output CSV (no header)
    with open(args.output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"[INFO] Wrote {len(rows)} rows to {args.output_csv}")

if __name__ == "__main__":
    main()
