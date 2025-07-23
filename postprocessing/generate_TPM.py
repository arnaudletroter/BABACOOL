import os
import argparse
import subprocess
import pandas as pd
import glob

def run_command(cmd, dry_run=False, env=None):
    print("Running:", " ".join(map(str, cmd)))
    if not dry_run:
        subprocess.run(cmd, check=True, env=env)

def update_subjects_list(csv_path):
    df = pd.read_csv(csv_path)
    return list(df[['subject', 'session']].itertuples(index=False, name=None))

def main():
    parser = argparse.ArgumentParser(description="generate Tissue probability maps to template space")
    parser.add_argument('--bids_root', required=True, help="Root directory of BIDS dataset")
    parser.add_argument('--subjects_csv', required=True, help="CSV file with columns 'subject' and 'session'")
    parser.add_argument('--template_name', required=True, help="Template name (e.g. BaBa21)")
    parser.add_argument('--template_session', required=True, help="Template session (e.g. ses-0)")
    parser.add_argument('--patterns', required=True, nargs='+', help="List of patterns to try for transform filenames (e.g. warped flipped)")
    parser.add_argument('--output_derivatives', default=None, help="Output derivatives directory, default: bids_root/derivatives")
    parser.add_argument('--mask_subfolder', default="warped", help="Subfolder under derivatives where masks are stored (default: warped)")
    parser.add_argument('--modalities', nargs='+', required=True,
                        help="List of modalities/masks to warp (e.g. label-WM_mask label-GM_mask brain_mask)")
    parser.add_argument('--dry-run', action="store_true", help="Print commands without executing them")

    args = parser.parse_args()

    dry_run = args.dry_run
    bids_root = args.bids_root

    derivatives_dir = args.output_derivatives or os.path.join(bids_root, "derivatives")

    # Template image
    template_image = os.path.join(
        bids_root,
        "derivatives",
        "template",
        f"sub-{args.template_name}",
        f"{args.template_session}",
        "final",
        f"sub-{args.template_name}_{args.template_session}_desc-symmetric-sharpen_T1w.nii.gz"
    )
    if not os.path.exists(template_image):
        print(f"ERROR: Template image not found: {template_image}")
        return

    # Transforms folder
    transform_dir = os.path.join(
        bids_root,
        "derivatives",
        "template",
        f"sub-{args.template_name}",
        f"{args.template_session}",
        "tmp_HR"
    )
    if not os.path.exists(transform_dir):
        print(f"ERROR: Transform directory not found: {transform_dir}")
        return

    subjects = update_subjects_list(args.subjects_csv)
    if not subjects:
        print("No subjects/sessions to process.")
        return

    for sub, ses in subjects:
        print(f"\n=== Processing {sub} {ses} ===")

        # Input masks to warp
        mask_input_dir = os.path.join(derivatives_dir, args.mask_subfolder, sub, ses)
        if not os.path.exists(mask_input_dir):
            print(f"WARNING: Mask folder does not exist: {mask_input_dir}")
            continue

        # Make sure output dir exists
        output_dir = os.path.join(derivatives_dir, args.mask_subfolder, sub, ses)
        os.makedirs(output_dir, exist_ok=True)

        for modality in args.modalities:
            for pattern in args.patterns:

                print(f"----{pattern}-----")
                warp_transform = None
                affine_transform = None

                warp_candidates = glob.glob(
                    os.path.join(transform_dir, f"*{sub}_{ses}_space-*_desc-{pattern}_T1w-1Warp.nii.gz")
                )
                affine_candidates = glob.glob(
                    os.path.join(transform_dir, f"*{sub}_{ses}_space-*_desc-{pattern}_T1w-0GenericAffine.mat")
                )

                if warp_candidates and affine_candidates:
                    warp_transform = warp_candidates[0]
                    affine_transform = affine_candidates[0]
                    print(f"Found transform for pattern '{pattern}':")
                    print(f"  Warp: {warp_transform}")
                    print(f"  Affine: {affine_transform}")

                if warp_transform is None or affine_transform is None:
                    print(
                        f"ERROR: No transform found for {sub} {ses} with any of the patterns {args.patterns} in {transform_dir}")
                    continue

                input_mask = os.path.join(mask_input_dir, f"{sub}_{ses}_space-Haiko89_desc-{pattern}_{modality}.nii.gz")
                if not os.path.exists(input_mask):
                    print(f"  WARNING: Input mask not found for modality '{modality}': {input_mask}. Skipping.")
                    continue

                output_mask = os.path.join(
                    output_dir,
                    f"{sub}_{ses}_space-{args.template_name}_desc-{pattern}_{modality}_probseg.nii.gz"
                )

                cmd = [
                    "antsApplyTransforms", "-d", "3",
                    "-i", input_mask,
                    "-r", template_image,
                    "-o", output_mask,
                    "-t", warp_transform,
                    "-t", affine_transform,
                    "--interpolation", "Linear",
                    "--verbose", "1"
                ]
                run_command(cmd, dry_run)

    print("\n=== Averaging images across subjects ===")
    for modality in args.modalities:

        all_warped_images = []
        for sub, ses in subjects:
            output_dir = os.path.join(
                derivatives_dir,
                args.mask_subfolder,
                sub,
                ses
            )
            for pattern in args.patterns:
                pattern_glob = f"{sub}_{ses}_space-{args.template_name}_desc-{pattern}_{modality}_probseg.nii.gz"
                found = glob.glob(os.path.join(output_dir, pattern_glob))
                all_warped_images.extend(found)

        if not all_warped_images:
            print(f"  No warped images found for modality '{modality}', skipping average.")
            continue

        average_output = os.path.join(
            bids_root,
            "derivatives",
            "template",
            f"sub-{args.template_name}",
            f"{args.template_session}",
            "final",
            f"sub-{args.template_name}_{args.template_session}_desc-symmetric_{modality}_probseg.nii.gz"
        )

        cmd = ["AverageImages", "3", average_output, "0"] + all_warped_images
        print(f"  Averaging {len(all_warped_images)} images for modality '{modality}'")
        run_command(cmd, dry_run)

if __name__ == "__main__":
    main()
