#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import subprocess
import sys
import csv

def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch denoise BIDS T1w/T2w images using ANTs DenoiseImage, saving outputs in BIDS derivatives folder."
    )
    parser.add_argument(
        "-i", "--input-csv", required=True,
        help="CSV file (e.g. subjects_sessions.csv) with columns subject,session"
    )
    parser.add_argument(
        "-b", "--bids-root", required=True,
        help="Path to BIDS dataset root"
    )
    parser.add_argument(
        "-o", "--output-csv", required=True,
        help="Path to CSV file listing output T1w and T2w denoised images"
    )
    parser.add_argument(
        "--threads", type=int, default=12,
        help="Number of threads for ITK/ANTs (default: 12)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print commands without executing them"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    csv_path = args.input_csv
    bids_root = args.bids_root
    threads = args.threads
    dry_run = args.dry_run
    output_csv_path = args.output_csv

    # Check input files/folders
    if not os.path.isfile(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    if not os.path.isdir(bids_root):
        print(f"Error: BIDS root folder not found: {bids_root}")
        sys.exit(1)

    # Read CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)

    required_cols = {"subject", "session"}
    if not required_cols.issubset(df.columns):
        print(f"Error: CSV must contain columns: {required_cols}")
        sys.exit(1)

    print(f"Found {len(df)} subject-session rows in {csv_path}")
    print(f"Using {threads} threads for ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS")

    # Base output derivatives folder
    derivatives_base = os.path.join(bids_root, "derivatives", "denoised")

    # Collect lines for CSV output
    csv_lines = []

    for idx, row in df.iterrows():
        subj = row["subject"]
        sess = row["session"]

        anat_input_dir = os.path.join(bids_root, subj, sess, "anat")
        if not os.path.isdir(anat_input_dir):
            print(f"Skipping missing folder: {anat_input_dir}")
            continue

        anat_output_dir = os.path.join(derivatives_base, subj, sess, "anat")
        os.makedirs(anat_output_dir, exist_ok=True)

        print(f"Processing: {anat_input_dir}")
        print(f"Output folder: {anat_output_dir}")

        denoised_T1w = ""
        denoised_T2w = ""

        for fname in sorted(os.listdir(anat_input_dir)):
            if fname.endswith("_T1w.nii.gz") or fname.endswith("_T2w.nii.gz"):
                in_path = os.path.join(anat_input_dir, fname)

                # Build output filename with suffix '_desc-denoised' before modality and extension
                parts = fname.split("_")
                modality_part = parts[-1]  # e.g. T1w.nii.gz
                modality = modality_part.replace(".nii.gz", "")
                out_fname = "_".join(parts[:-1] + [f"desc-denoised_{modality}.nii.gz"])

                out_path = os.path.join(anat_output_dir, out_fname)

                cmd = [
                    "DenoiseImage",
                    "-d", "3",
                    "-i", in_path,
                    "-o", out_path,
                    "-r", "3x3x3",
                    "-v"
                ]

                cmd_str = " ".join(cmd)
                env = os.environ.copy()
                env["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = str(threads)

                if dry_run:
                    print(f"[DRY RUN] {cmd_str} (threads={threads})")
                else:
                    print(f"Running: {cmd_str} (threads={threads})")
                    try:
                        subprocess.run(cmd, check=True, env=env)
                        print(f"Denoised saved: {out_path}")

                        if "_T1w" in fname:
                            denoised_T1w = out_path
                        elif "_T2w" in fname:
                            denoised_T2w = out_path

                    except subprocess.CalledProcessError as e:
                        print(f"Error running DenoiseImage on {in_path}: {e}")

        # Add a line even if one of the two is missing
        csv_lines.append([denoised_T1w, denoised_T2w])

    # Write the CSV output
    print(f"\nWriting CSV log to {output_csv_path}")
    with open(output_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["T1w_denoised", "T2w_denoised"])
        for line in csv_lines:
            writer.writerow(line)

    print("\nProcessing complete.")
    print(f"Total processed subject-session pairs: {len(csv_lines)}")
    print(f"CSV log written to: {output_csv_path}")

if __name__ == "__main__":
    main()
