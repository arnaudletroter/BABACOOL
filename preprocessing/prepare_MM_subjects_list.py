#!/usr/bin/env python3

import argparse
import os
import pandas as pd
import csv
import sys
import glob

def find_image(bids_root, deriv_subdir, subject, session, modality):
    """
    Search for an image or mask file in derivatives/<deriv_subdir>/<subject>/<session>/anat
    matching *label-{modality}_mask.nii.gz
    """
    anat_dir = os.path.join(
        bids_root, "derivatives", deriv_subdir,
        subject, session
    )

    if not os.path.isdir(anat_dir):
        print(f"[WARNING] Anat folder does not exist: {anat_dir}")
        return ""

    pattern = f"*_{modality}.nii.gz"
    candidates = glob.glob(os.path.join(anat_dir, pattern))

    if not candidates:
        print(f"[WARNING] No file found for modality {modality} in {anat_dir}")
        return ""

    # Return first matching file
    return candidates[0]

def main():
    parser = argparse.ArgumentParser(
        description="Create CSV input list for ANTs template building (no header in output)"
    )
    parser.add_argument(
        "-i", "--input-csv", required=True,
        help="Input CSV with 'subject' and 'session' columns"
    )
    parser.add_argument(
        "--modalities", nargs="+", required=True,
        help="List of modalities to look for (e.g., T1w T2w WM)"
    )
    parser.add_argument(
        "-b", "--bids-root", required=True,
        help="BIDS root folder"
    )
    parser.add_argument(
        "--deriv-subdir", default="segmentation",
        help="Subdirectory under derivatives to look for files (default: segmentation)"
    )
    parser.add_argument(
        "-o", "--output-csv", default="output_list_for_MM_template.csv",
        help="Output CSV file (no header - compatible for antsMultivariateTemplateConstruction2.sh )"
    )
    args = parser.parse_args()

    # Load input CSV
    try:
        df = pd.read_csv(args.input_csv)
    except Exception as e:
        print(f"[ERROR] Could not read CSV: {e}")
        sys.exit(1)

    # Check that 'subject' and 'session' columns exist
    for col in ["subject", "session"]:
        if col not in df.columns:
            print(f"[ERROR] Input CSV is missing expected column: {col}")
            print(f"[INFO] Found columns: {list(df.columns)}")
            sys.exit(1)

    rows = []

    for idx, row in df.iterrows():
        subject = row["subject"]
        session = row["session"]

        if pd.isna(subject) or pd.isna(session):
            print(f"[WARNING] Missing sub or session at row {idx}. Skipping.")
            continue

        subject = str(subject).strip()
        session = str(session).strip()

        out_row = []

        # For each modality, find its path
        for modality in args.modalities:
            path = find_image(args.bids_root, args.deriv_subdir, subject, session, modality)
            out_row.append(path)

        rows.append(out_row)

    # Write output CSV (no header)
    with open(args.output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"[INFO] Wrote {len(rows)} rows to {args.output_csv}")

if __name__ == "__main__":
    main()