#!/usr/bin/env python3

import argparse
import os
import subprocess
import pandas as pd

def run_command(cmd, workdir=None):
    """Run a shell command with optional working directory."""
    print(f"[INFO] Running command: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=workdir)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {cmd}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Two-stage multivariate template construction with ANTs, BIDS-style outputs"
    )
    parser.add_argument(
        "-s", "--subject", required=True,
        help="Subject label (e.g. BaBa21)"
    )
    parser.add_argument(
        "-S", "--session", required=True,
        help="Session label (e.g. ses-0)"
    )
    parser.add_argument(
        "--input-list", required=True,
        help="CSV file with list of input NIfTI images for both stages"
    )
    parser.add_argument(
        "-b", "--bids-root", required=True,
        help="BIDS root folder"
    )
    parser.add_argument(
        "-j", "--jobs", type=int, default=12,
        help="Number of CPU cores to use (default: 12)"
    )
    parser.add_argument(
        "--modalities", nargs="+", required=True,
        help="List of modalities to look for (e.g., T1w T2w label-WM_mask)"
    )
    parser.add_argument(
        "--ite1", type=int, default=1,
        help="Number of iterations for Stage 1 (default: 1)"
    )
    parser.add_argument(
        "--q1", default="10x0x0",
        help="Steps for Stage 1 -q option (default: 10x0x0)"
    )
    parser.add_argument(
        "--w1", default="0.5x0.5x1",
        help="Weights for Stage 1 modalities (default: 0.5x0.5x1)"
    )
    parser.add_argument(
        "--ite2", type=int, default=1,
        help="Number of iterations for Stage 2 (default: 1)"
    )
    parser.add_argument(
        "--q2", default="50x30x15",
        help="Steps for Stage 2 -q option (default: 50x30x15)"
    )
    parser.add_argument(
        "--w2", default="1x1x1",
        help="Weights for Stage 2 modalities (default: 1x1x1)"
    )

    args = parser.parse_args()

    # Load CSV and determine modalities count
    df = pd.read_csv(args.input_list)
    modalities = list(df.columns)
    modalities_count = len(modalities)

    print(f"[INFO] Detected {modalities_count} modalities: {modalities}")

    # Define output directories under BIDS derivatives/template
    derivatives_dir = os.path.join(args.bids_root, "derivatives", "template")
    subject_dir = f"sub-{args.subject}"
    session_dir = args.session
    output_base = os.path.join(derivatives_dir, subject_dir, session_dir)
    tmp_LR = os.path.join(output_base, "tmp_LR")
    tmp_HR = os.path.join(output_base, "tmp_HR")
    final_dir = os.path.join(output_base, "final")

    for d in [tmp_LR, tmp_HR, final_dir]:
        os.makedirs(d, exist_ok=True)

    print(f"[INFO] All outputs will go to: {output_base}")

    # Stage 1: low-resolution template building
    print("[INFO] Starting Stage 1: Low-resolution template construction")

    ants_script_path = os.path.join("$ANTSPATH", "antsMultivariateTemplateConstruction2.sh")

    stage1_cmd = (
        f"{ants_script_path} "
        f"-d 3 -i {args.ite1} -k {modalities_count} -c 2 -j {args.jobs} "
        f"-f 4x2x1 -s 2x1x0vox -q {args.q1} "
        f"-w {args.w1} -t SyN -A 1 -n 0 -m CC "
        f"-o {tmp_LR}/MY {args.input_list}"
    )
    run_command(stage1_cmd, workdir='./')

    # Resampling Stage 1 templates to 0.4mm isotropic
    print("[INFO] Resampling Stage 1 outputs to higher resolution")
    for i in range(modalities_count):
        in_file = os.path.join(tmp_LR, "intermediateTemplates", f"SyN_iteration{args.ite1 - 1}_MYtemplate{i}.nii.gz")
        out_file = os.path.join(tmp_HR, f"{args.subject}_{args.session}_SyN_iteration{args.ite1 - 1}_MYtemplate{i}.nii.gz")
        convert_cmd = (
            f"mri_convert -i {in_file} -o {out_file} -vs 0.4 0.4 0.4"
        )
        run_command(convert_cmd)

    # Stage 2: high-resolution template building using resampled priors
    print("[INFO] Starting Stage 2: High-resolution template construction")
    paths = [
        os.path.join(
            tmp_HR,
            f"{args.subject}_{args.session}_SyN_iteration{args.ite1 - 1}_MYtemplate{i}.nii.gz"
        )
        for i in range(modalities_count)
    ]

    z_opts = " ".join([f"-z {p}" for p in paths])

    stage2_cmd = (
        f"{ants_script_path} "
        f"-d 3 -i {args.ite2} -k {modalities_count} -c 2 -j {args.jobs} "
        f"-f 4x2x1 -s 2x1x0vox -q {args.q2} "
        f"-t SyN -w {args.w2} {z_opts} -A 1 -n 0 -m CC "
        f"-o {tmp_HR}/MY {args.input_list}"
    )
    run_command(stage2_cmd, workdir='./')

    # Copy final outputs with BIDS-style names
    print("[INFO] Copying final templates to BIDS-style outputs")

    for modality in args.modalities:
        
        print(f"[INFO] modality {modality}")
        desc = f"desc-symmetric-sharpen_{modality}"

        dst_name = f"sub-{args.subject}_{args.session}_{desc}.nii.gz"
        src = os.path.join(tmp_HR, "intermediateTemplates", f"SyN_iteration{args.ite2 - 1}_MYtemplate{i}.nii.gz")
        dst = os.path.join(final_dir, dst_name)
        run_command(f"cp -f {src} {dst}")
        print(f"{dst}")

    print(f"[INFO] Template construction complete! Results in {final_dir}")

if __name__ == "__main__":
    main()
