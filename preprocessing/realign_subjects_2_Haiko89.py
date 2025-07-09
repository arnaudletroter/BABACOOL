import os
import argparse
import subprocess
import pandas as pd

def run_command(cmd, dry_run=False, env=None):
    print("Running:", " ".join(map(str, cmd)))
    if not dry_run:
        subprocess.run(cmd, check=True, env=env)

def update_subjects_list(csv_path):
    df = pd.read_csv(csv_path)
    return list(df[['subject', 'session']].itertuples(index=False, name=None))

def main():
    parser = argparse.ArgumentParser(description="Register BIDS subjects T1w/T2w to Haiko89 template using ANTs")
    parser.add_argument('--bids_root', required=True, help="Root directory of BIDS dataset")
    parser.add_argument('--sym', action='store_true', help='Use symmetric Haiko89 template (default: asymmetric)')
    parser.add_argument('--subjects_csv', required=True, help="CSV file with columns 'subject' and 'session'")
    parser.add_argument('--output_derivatives', default=None, help="Output derivatives directory, default: bids_root/derivatives")
    parser.add_argument('--padding', action='store_true', help="Generate padded Haiko template with ImageMath ANTS")
    parser.add_argument('--pad_size', type=int, default=50, help="Padding size in pixels (default: 50)")
    parser.add_argument('--generate_brainmask', action='store_true', help="Generate brainmask TPM from Haiko TPMs")
    parser.add_argument('--flipping_LR', action='store_true', default=False, help="Flip warped T1w/T2w images Left-Right (default: False)")
    parser.add_argument('--dry-run', action="store_true", help="Print commands without executing them")
    parser.add_argument('--threads', type=int, default=12, help="Number of threads for ITK/ANTs (default: 12)")

    args = parser.parse_args()

    dry_run = args.dry_run
    threads = args.threads
    bids_root = args.bids_root
    pad_size = args.pad_size

    derivatives_dir = args.output_derivatives or os.path.join(bids_root, "derivatives")
    haiko_sub_dir = os.path.join(derivatives_dir, "atlas", "sub-Haiko89", "ses-Adult", "anat")

    if args.sym:
        prefix = "sub-Haiko89_ses-Adult_desc-symmetric"
    else:
        prefix = "sub-Haiko89_ses-Adult_desc-asymmetric"

    haiko_template = os.path.join(haiko_sub_dir, f"{prefix}_T1w.nii.gz")
    haiko_template_pad = os.path.join(haiko_sub_dir, f"{prefix}-padded_T1w.nii.gz")
    haiko_csf = os.path.join(haiko_sub_dir, f"{prefix}_label-CSF_probseg.nii.gz")
    haiko_gm = os.path.join(haiko_sub_dir, f"{prefix}_label-GM_probseg.nii.gz")
    haiko_wm = os.path.join(haiko_sub_dir, f"{prefix}_label-WM_probseg.nii.gz")
    haiko_brainmask = os.path.join(haiko_sub_dir, f"{prefix}_label-BM_probseg.nii.gz")

    print("Using Haiko89 template files:")
    print(f"Template T1w: {haiko_template}")
    print(f"Padded Template T1w: {haiko_template_pad}")
    print(f"CSF TPM: {haiko_csf}")
    print(f"GM TPM: {haiko_gm}")
    print(f"WM TPM: {haiko_wm}")
    print(f"Brainmask TPM: {haiko_brainmask}")

    if args.padding:
        print("Generating padded Haiko template...")
        run_command([
            "ImageMath", "3",
            haiko_template_pad,
            "PadImage",
            haiko_template,
            str(pad_size)
        ], dry_run)
    else:
        if not os.path.exists(haiko_template_pad):
            raise FileNotFoundError(f"Padded template not found: {haiko_template_pad}. Use --padding to create it.")

    if args.generate_brainmask:
        print("Generating Haiko brainmask TPM by combining CSF, GM, WM and thresholding...")
        run_command([
            "fslmaths", haiko_csf,
            "-add", haiko_gm,
            "-add", haiko_wm,
            "-thr", "0.5",
            "-bin", haiko_brainmask
        ], dry_run)
    else:
        if not os.path.exists(haiko_brainmask):
            print(f"Warning: Brainmask not found: {haiko_brainmask}. Use --generate_brainmask to create it.")

    subjects = update_subjects_list(args.subjects_csv)

    if not subjects:
        print("No subjects/sessions to process.")
        return

    for sub, ses in subjects:
        print(f"Processing {sub} {ses}")

        anat_dir = os.path.join(derivatives_dir, "denoised", f"{sub}", f"{ses}", "anat")
        t1w_denoised = os.path.join(anat_dir, f"{sub}_{ses}_desc-denoised_T1w.nii.gz")
        t2w_denoised = os.path.join(anat_dir, f"{sub}_{ses}_desc-denoised_T2w.nii.gz")

        if not os.path.exists(t1w_denoised) or not os.path.exists(t2w_denoised):
            print(f"Warning: Missing denoised T1w or T2w for {sub} {ses}, skipping.")
            continue

        # SUBJECT BRAINMASK (must exist)
        subject_brainmask = os.path.join(bids_root, "derivatives", "segmentation",
            sub, ses, "anat", f"{sub}_{ses}_space-orig_desc-brain_mask.nii.gz"
        )

        if not os.path.exists(subject_brainmask):
            print(f"Warning: Brainmask not found for {sub} {ses}: {subject_brainmask}. Skipping.")
            continue

        transforms_dir = os.path.join(derivatives_dir, "transforms", f"{sub}", f"{ses}")
        os.makedirs(transforms_dir, exist_ok=True)

        output_dir = os.path.join(derivatives_dir, "warped", f"{sub}", f"{ses}")
        os.makedirs(output_dir, exist_ok=True)

        transfo_prefix = os.path.join(transforms_dir, f"{sub}_{ses}_from-native_to-Haiko89_rigid")

        output_t1w = os.path.join(output_dir, f"{sub}_{ses}_space-Haiko89_desc-warped_T1w.nii.gz")
        output_t2w = os.path.join(output_dir, f"{sub}_{ses}_space-Haiko89_desc-warped_T2w.nii.gz")

        t1w_denoised_masked = os.path.join(anat_dir, f"{sub}_{ses}_desc-masked_T1w.nii.gz")

        if args.generate_brainmask:
            print("Generating Haiko brainmask TPM by combining CSF, GM, WM and thresholding...")
            run_command([
                "fslmaths", t1w_denoised,
                "-mul", subject_brainmask,
                t1w_denoised_masked
            ], dry_run)


        antsreg_cmd = [
            "antsRegistration",
            "--verbose", "1",
            "--dimensionality", "3",
            "--initial-moving-transform" ,f"[{haiko_template_pad},{t1w_denoised_masked},1]",
            "--float", "0",
            "--collapse-output-transforms", "1",
            "--output", f"[{transfo_prefix}]",
            "--interpolation", "Linear",
            "--use-histogram-matching", "0",
            "--winsorize-image-intensities", "[0.005,0.995]",
            "--transform", "Rigid[0.1]",
            "--metric", f"MI[{haiko_template_pad},{t1w_denoised_masked},1,32,Regular,0.25 ]",
            "--convergence", "[1000x500x250x0,1e-6,10]",
            "--shrink-factors", "8x4x2x1",
            "--smoothing-sigmas", "3x2x1x0vox"
        ]

        env = os.environ.copy()
        env["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = str(threads)

        run_command(antsreg_cmd, dry_run, env)

        antsapply_cmd = [
            "antsApplyTransforms",
            "-d", "3",
            "-i", t1w_denoised,
            "-r", haiko_template_pad,
            "-o", output_t1w,
            "-t", f"{transfo_prefix}0GenericAffine.mat",
            "--interpolation", "Linear"
        ]

        run_command(antsapply_cmd, dry_run, env)

        antsapply_cmd = [
            "antsApplyTransforms",
            "-d", "3",
            "-i", t2w_denoised,
            "-r", haiko_template_pad,
            "-o", output_t2w,
            "-t", f"{transfo_prefix}0GenericAffine.mat",
            "--interpolation", "Linear"
        ]

        run_command(antsapply_cmd, dry_run, env)

        # SUBJECT 3 TISSUES (must exist)
        subject_wm = os.path.join(bids_root, "derivatives", "segmentation",
            sub, ses, "anat", f"{sub}_{ses}_space-orig_label-WM_mask.nii.gz"
        )
        if not os.path.exists(subject_wm):
            print(f"Warning: wm mask not found for {sub} {ses}: {subject_wm}. Skipping.")
            continue
        subject_gm = os.path.join(bids_root, "derivatives", "segmentation",
            sub, ses, "anat", f"{sub}_{ses}_space-orig_label-GM_mask.nii.gz"
        )
        if not os.path.exists(subject_gm):
            print(f"Warning: wm mask not found for {sub} {ses}: {subject_gm}. Skipping.")
            continue
        subject_csf = os.path.join(bids_root, "derivatives", "segmentation",
            sub, ses, "anat", f"{sub}_{ses}_space-orig_label-CSF_mask.nii.gz"
        )
        if not os.path.exists(subject_csf):
            print(f"Warning: csf mask not found for {sub} {ses}: {subject_csf}. Skipping.")
            continue

        output_wm = os.path.join(output_dir, f"{sub}_{ses}_space-Haiko89_desc-warped_label-WM_mask.nii.gz")
        output_gm = os.path.join(output_dir, f"{sub}_{ses}_space-Haiko89_desc-warped_label-GM_mask.nii.gz")
        output_csf = os.path.join(output_dir, f"{sub}_{ses}_space-Haiko89_desc-warped_label-CSF_mask.nii.gz")

        antsapply_cmd = [
            "antsApplyTransforms", "-d", "3",
            "-i", subject_wm, "-r", haiko_template_pad, "-o", output_wm,
            "-t", f"{transfo_prefix}0GenericAffine.mat", "--interpolation", "NearestNeighbor"
        ]
        run_command(antsapply_cmd, dry_run, env)
        antsapply_cmd = [
            "antsApplyTransforms", "-d", "3",
            "-i", subject_gm, "-r", haiko_template_pad, "-o", output_gm,
            "-t", f"{transfo_prefix}0GenericAffine.mat", "--interpolation", "NearestNeighbor"
        ]
        run_command(antsapply_cmd, dry_run, env)
        antsapply_cmd = [
            "antsApplyTransforms", "-d", "3",
            "-i", subject_csf, "-r", haiko_template_pad, "-o", output_csf,
            "-t", f"{transfo_prefix}0GenericAffine.mat", "--interpolation", "NearestNeighbor"
        ]
        run_command(antsapply_cmd, dry_run, env)

        # -----------------------------
        # Optionally flip Left/Right
        # -----------------------------
        if args.flipping_LR:
            print("Flipping outputs Left-Right...")

            flipped_t1w = os.path.join(output_dir, f"{sub}_{ses}_space-Haiko89_desc-flipped_T1w.nii.gz")
            flipped_t2w = os.path.join(output_dir, f"{sub}_{ses}_space-Haiko89_desc-flipped_T2w.nii.gz")

            # T1w flip
            run_command([
                "fslswapdim", output_t1w, "-x", "y", "z", flipped_t1w
            ], dry_run)

            run_command([
                "CopyImageHeaderInformation",
                output_t1w,
                flipped_t1w,
                flipped_t1w,
                "1","1","1"
            ], dry_run)

            # T2w flip
            run_command([
                "fslswapdim", output_t2w, "-x", "y", "z", flipped_t2w
            ], dry_run)

            run_command([
                "CopyImageHeaderInformation",
                output_t2w,
                flipped_t2w,
                flipped_t2w,
                "1"
            ], dry_run)

            flipped_WM = os.path.join(output_dir, f"{sub}_{ses}_space-Haiko89_desc-flipped_label-WM_mask.nii.gz")
            run_command([
                "fslswapdim", output_wm, "-x", "y", "z", flipped_WM
            ], dry_run)

            run_command([
                "CopyImageHeaderInformation",
                output_wm,
                flipped_WM,
                flipped_WM,
                "1", "1", "1"
            ], dry_run)

            print(f"Flipped images saved: {flipped_t1w}, {flipped_t2w} {flipped_WM}")

if __name__ == "__main__":
    main()
