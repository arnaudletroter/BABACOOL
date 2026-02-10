#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import subprocess
import sys
import csv
import glob

def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch Debias BIDS T1w/T2w images using HCP script, saving outputs in BIDS derivatives folder."
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
        help="Path to CSV file listing output T1w and T2w unbiased images"
    )
    parser.add_argument(
        "--threads", type=int, default=12,
        help="Number of threads for ITK/ANTs (default: 12)"
    )

    parser.add_argument("--brain_mask_suffix",
                        help="Suffix for the binary brain mask filename (e.g., `desc-brain_mask`)"
                        )
    parser.add_argument("--s_value", type=int, default=2,
                        help="size of gauss kernel in mm when performing mean filtering (default=2).")
    parser.add_argument("--k", action="store_true",
                        help="Will keep temporary files (adds the -k flag).")
    
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print commands without executing them"
    )
    return parser.parse_args()

def find_input_mask(mask_input_dir, sub, ses, mask):
    pattern = f"{sub}_{ses}_{mask}.nii.gz"
    files = glob.glob(os.path.join(mask_input_dir, pattern))
    return files[0] if files else None

def main():
    args = parse_args()

    csv_path = args.input_csv
    bids_root = args.bids_root

    brainmask = args.brain_mask_suffix

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
    derivatives_base = os.path.join(bids_root, "derivatives", "unbiased")
    derivatives_seg = os.path.join(bids_root, "derivatives","segmentation")

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

        unbiased_T1w = ""
        unbiased_T2w = ""

        for fname in sorted(os.listdir(anat_input_dir)):
            if fname.endswith("_T1w.nii.gz"):

                T1w = os.path.join(anat_input_dir, fname)
                T2w = T1w.replace("T1w.nii.gz", "T2w.nii.gz")


                parts = fname.split("_")
                modality_part = parts[-1]  # e.g. T1w.nii.gz
                modality = modality_part.replace(".nii.gz", "")

                out_fname_T1w = "_".join(parts[:-1] + [f"desc-unbiased_{modality}.nii.gz"])
                out_fname_T2w = out_fname_T1w.replace("T1w.nii.gz", "T2w.nii.gz")

                unbiased_T1w = os.path.join(anat_output_dir, out_fname_T1w)
                unbiased_T2w = os.path.join(anat_output_dir, out_fname_T2w)


                out_tmp_T1w = "_".join(parts[:-1] + [f"debiased_{modality}.nii.gz"])
                out_tmp_T2w = out_tmp_T1w.replace("T1w.nii.gz", "T2w.nii.gz")
                unbiased_tmp_T1w = os.path.join(anat_input_dir, out_tmp_T1w)
                unbiased_tmp_T2w = os.path.join(anat_input_dir, out_tmp_T2w)
                
                print(f"\nintputs\n")
                print(unbiased_tmp_T1w, unbiased_tmp_T2w)
                print(f"\noutputs\n")
                print(unbiased_T1w, unbiased_T2w)

                cmd = [
                    "postprocessing/T1xT2BiasFieldCorrection.sh",
                    "-t1", T1w,
                    "-t2", T2w,
                    "-s", str(args.s_value),
                    "-os", "_debiased"
                ]

                if args.brain_mask_suffix:
                    input_mask = os.path.join(derivatives_seg, subj, sess,"anat",f"{subj}_{sess}_{brainmask}.nii.gz")

                    # brain_mask = f"{args.brain_mask_suffix}.nii.gz"
                    #print(derivatives_seg,subj, sess, brainmask)
                    #input_mask = find_input_mask(derivatives_seg, subj, sess, brainmask)
                    print(input_mask)
                    if os.path.exists(input_mask):
                        cmd.extend(["-b", input_mask])
                    else:
                        print(f"Warning: Brain mask file not found for session {sess}: {brain_mask}")
                        print("Skipping -b option for this session.")

                if args.k:
                    cmd.append("-k")

                print(f"\nRunning command for {sess}:\n{' '.join(cmd)}\n")

                cmd_mv_T1w = ["mv", unbiased_tmp_T1w, unbiased_T1w]
                cmd_mv_T2w = ["mv", unbiased_tmp_T2w, unbiased_T2w]

                if not dry_run:
                    subprocess.run(cmd, check=True)

                    subprocess.run(cmd_mv_T1w, check=True)
                    subprocess.run(cmd_mv_T2w, check=True)



        # Add a line even if one of the two is missing
        csv_lines.append([unbiased_T1w, unbiased_T2w])

    # Write the CSV output
    print(f"\nWriting CSV log to {output_csv_path}")
    with open(output_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["unbiased_T1w", "unbiased_T2w"])
        for line in csv_lines:
            writer.writerow(line)

    print("\nProcessing complete.")
    print(f"Total processed subject-session pairs: {len(csv_lines)}")
    print(f"CSV log written to: {output_csv_path}")

if __name__ == "__main__":
    main()
