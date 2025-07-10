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
    args = parser.parse_args()

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

    ants_script_path = os.path.join("postprocessing", "antsMultivariateTemplateConstruction2.sh")
    print(ants_script_path)

    ite=1
    stage1_cmd = (
        f"{ants_script_path} "
        f"-d 3 -i {ite} -k 3 -c 2 -j {args.jobs} "
        f"-f 4x2x1 -s 2x1x0vox -q 10x0x0 "
        f"-w 0.5x0.5x1 -t SyN -A 1 -n 0 -m CC "
        f"-o {tmp_LR}/MY {args.input_list}"
    )
    #run_command(stage1_cmd, workdir='./')

    # Resampling Stage 1 templates to 0.4mm isotropic
    print("[INFO] Resampling Stage 1 outputs to higher resolution")
    for i in range(3):
        in_file = os.path.join(tmp_LR, "intermediateTemplates", f"SyN_iteration{ite-1}_MYtemplate{i}.nii.gz")
        out_file = os.path.join(tmp_HR, f"{args.subject}_{args.session}_SyN_iteration{ite-1}_MYtemplate{i}.nii.gz")
        convert_cmd = (
            f"mri_convert -i {in_file} -o {out_file} -vs 0.4 0.4 0.4"
        )
        #run_command(convert_cmd)

    # Stage 2: high-resolution template building using resampled priors
    print("[INFO] Starting Stage 2: High-resolution template construction")
    paths = [
        os.path.join(
            tmp_HR,
            f"{args.subject}_{args.session}_SyN_iteration{ite - 1}_MYtemplate{i}.nii.gz"
        )
        for i in range(3)
    ]

    z_opts = " ".join([f"-z {p}" for p in paths])

    stage2_input_glob = args.input_list

    ants_script_path = os.path.join("postprocessing", "antsMultivariateTemplateConstruction2.sh")
    print(ants_script_path)

    ite2=1
    stage2_cmd = (
        f"{ants_script_path} "
        f"-d 3 -i {ite2} -k 3 -c 2 -j {args.jobs} "
        #f"-f 4x2x1 -s 2x1x0vox -q 50x30x15 "
        f"-f 4x2x1 -s 2x1x0vox -q 4x0x0 "
        f"-t SyN -w 1x1x1 {z_opts} -A 1 -n 0 -m CC "
        f"-o {tmp_HR}/MY {stage2_input_glob}"
    )
    run_command(stage2_cmd, workdir='./')

    # Copy final outputs with BIDS-style names
    print("[INFO] Copying final templates to BIDS-style outputs")
    mapping = {
        0: f"sub-{args.subject}_{args.session}_desc-symmetric-sharpen_T1w.nii.gz",
        1: f"sub-{args.subject}_{args.session}_desc-symmetric-sharpen_T2w.nii.gz",
        2: f"sub-{args.subject}_{args.session}_desc-symmetric-sharpen_label-WM_probseg.nii.gz"
    }

    for i in range(3):
        src = os.path.join(tmp_HR, "intermediateTemplates", f"SyN_iteration{ite2-1}_MYtemplate{i}.nii.gz")
        dst = os.path.join(final_dir, mapping[i])
        run_command(f"cp -f {src} {dst}")

    print(f"[INFO] Template construction complete! Results in {final_dir}")

if __name__ == "__main__":
    main()
