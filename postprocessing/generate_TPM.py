import os
import argparse
import subprocess
import pandas as pd
import glob

def run_command(cmd, dry_run=False, env=None):
    print("Running:", " ".join(map(str, cmd)))
    if not dry_run:
        subprocess.run(cmd, check=True, env=env)

def read_subjects(csv_path):
    df = pd.read_csv(csv_path)
    return list(df[['subject', 'session']].itertuples(index=False, name=None))

def build_desc_str(descriptions):
    if descriptions:
        return "_".join(descriptions)
    return None

def build_template_image(bids_root, template_name, template_session, template_folder, reference_suffix):
    return os.path.join(
        bids_root, "derivatives", "template",
        f"sub-{template_name}", template_session, template_folder,
        f"sub-{template_name}_{template_session}_{reference_suffix}.nii.gz"
    )

def build_output_filename(sub, ses, template_name, pattern, modality, map_type, desc_str=None):
    suffix = f"{desc_str}" if desc_str else ""
    if map_type == "mask":
        return f"{sub}_{ses}_space-{template_name}_{modality}_desc-{pattern}_{suffix}.nii.gz"
    elif map_type == "contrast":
        return f"{sub}_{ses}_space-{template_name}_desc-{pattern}_{suffix}_{modality}.nii.gz"
    else:
        raise ValueError(f"Type de map inconnu: {map_type}")

def build_final_average_filename(template_name, template_session, modality, map_type, desc_str=None):
    suffix = f"{desc_str}" if desc_str else ""
    if map_type == "mask":
        return f"sub-{template_name}_{template_session}_{modality}_desc-{suffix}.nii.gz"
    elif map_type == "contrast":
        return f"sub-{template_name}_{template_session}_desc-{suffix}_{modality}.nii.gz"
    else:
        raise ValueError(f"Type de map inconnu: {map_type}")

def find_transform(transform_dir, sub, ses, pattern):
    warp = glob.glob(os.path.join(transform_dir, f"*{sub}_{ses}_space-*_desc-{pattern}_T1w-1Warp.nii.gz"))
    affine = glob.glob(os.path.join(transform_dir, f"*{sub}_{ses}_space-*_desc-{pattern}_T1w-0GenericAffine.mat"))
    return (warp[0] if warp else None), (affine[0] if affine else None)

def find_input_mask(mask_input_dir, sub, ses, modality, map_type):
    pattern = f"{sub}_{ses}*{modality}_mask.nii.gz" if map_type == "mask" else f"{sub}_{ses}*{modality}.nii.gz"
    files = glob.glob(os.path.join(mask_input_dir, pattern))
    return files[0] if files else None

def apply_transform(pattern, input_mask, template_image, output_mask, warp, affine, transfo_prefix, sub, ses, dry_run):
    if pattern == "warped":
        transforms = [
            warp,
            affine,
            f"{transfo_prefix}/{sub}_{ses}_from-native_to-Haiko89_rigid0GenericAffine.mat"
        ]
    elif pattern == "flipped":
        transforms = [
            warp,
            affine,
            f"{transfo_prefix}/{sub}_{ses}_from-Haiko89_flip-x_ants.mat",
            f"{transfo_prefix}/{sub}_{ses}_from-native_to-Haiko89_rigid0GenericAffine.mat"
        ]
    else:
        return

    cmd = [
        "antsApplyTransforms", "-d", "3",
        "-i", input_mask,
        "-r", template_image,
        "-o", output_mask,
        *sum([["-t", t] for t in transforms], []),
        "--interpolation", "Linear",
        "--verbose", "1"
    ]
    run_command(cmd, dry_run)

def main():
    parser = argparse.ArgumentParser(
        description="Generate mean volumes (TPM or average contrast) to template space"
    )

    parser.add_argument(
        '--bids_root', required=True,
        help="Root directory of BIDS dataset (required)"
    )
    parser.add_argument(
        '--subjects_csv', required=True,
        help="CSV file with columns 'subject' and 'session' (required)"
    )
    parser.add_argument(
        '--template_name', required=True,
        help="Template name (e.g. BaBa21) (required)"
    )
    parser.add_argument(
        '--template_session', required=True,
        help="Template session (e.g. ses-0) (required)"
    )
    parser.add_argument(
        '--reference_suffix', default="desc-sharpen_T1w", required=True,
        help="Reference suffix volume for warping input images (e.g. desc-sharpen) (required)"
    )
    parser.add_argument(
        '--patterns', required=True, nargs='+',
        help="List of patterns selected for merging (e.g. warped flipped) (required)"
    )
    parser.add_argument(
        '--input_folder', default="",
        help="Folder where input images are located (default: bids_root)"
    )
    parser.add_argument(
        '--output_tmp_folder', default="warped",
        help="Folder under derivatives where warped volumes are saved (default: warped)"
    )
    parser.add_argument(
        '--template_folder', default="final",
        help="Folder under template where final template images are located (default: final)"
    )
    parser.add_argument(
        '--modalities', nargs='+', required=True,
        help="List of modalities/masks to warp (e.g. label-WM label-GM desc-brain) (required)"
    )
    parser.add_argument(
        '--map_type', required=True,
        help="Type of map, BIDS-compatible (e.g. mask for TPM or contrast for other maps like T1w)"
    )
    parser.add_argument(
        '--bids_description', nargs='+',
        help="Optional list of BIDS descriptions to include in output filenames (e.g. average padded)"
    )
    parser.add_argument(
        '--dry-run', action="store_true",
        help="Print commands without executing them"
    )

    args = parser.parse_args()

    dry_run = args.dry_run
    bids_root = args.bids_root
    derivatives_dir = os.path.join(bids_root, "derivatives")
    input_dir = os.path.join(bids_root, args.input_folder)
    desc_str = build_desc_str(args.bids_description)

    # Template & transform dirs
    template_image = build_template_image(bids_root, args.template_name, args.template_session, args.template_folder, args.reference_suffix)
    transform_dir = os.path.join(bids_root, "derivatives", "template", f"sub-{args.template_name}", args.template_session, "tmp_HR")

    if not os.path.exists(template_image):
        print(f"ERROR: Template image not found: {template_image}")
        return
    if not os.path.exists(transform_dir):
        print(f"ERROR: Transform directory not found: {transform_dir}")
        return

    subjects = read_subjects(args.subjects_csv)
    if not subjects:
        print("No subjects to process.")
        return

    # --- WARPS ---
    for sub, ses in subjects:
        print(f"\n=== Processing {sub} {ses} ===")
        mask_input_dir = os.path.join(input_dir, sub, ses, "anat")
        if not os.path.exists(mask_input_dir):
            print(f"WARNING: Mask folder does not exist: {mask_input_dir}")
            continue

        output_dir = os.path.join(derivatives_dir, args.output_tmp_folder, sub, ses)
        os.makedirs(output_dir, exist_ok=True)

        for modality in args.modalities:
            for pattern in args.patterns:
                warp, affine = find_transform(transform_dir, sub, ses, pattern)
                if not warp or not affine:
                    print(f"ERROR: No transform for {sub} {ses} pattern {pattern}")
                    continue

                input_mask = find_input_mask(mask_input_dir, sub, ses, modality, args.map_type)
                if not input_mask:
                    print(f"ERROR: No image {modality} found for {sub} {ses}")
                    continue

                output_mask = os.path.join(output_dir, build_output_filename(sub, ses, args.template_name, pattern, modality, args.map_type, desc_str))
                transfo_prefix = os.path.join(derivatives_dir, "transforms", sub, ses)

                apply_transform(pattern, input_mask, template_image, output_mask, warp, affine, transfo_prefix, sub, ses, dry_run)

    # --- AVERAGING ---
    print("\n=== Averaging images across subjects ===")
    for modality in args.modalities:
        all_warped_images = []
        for sub, ses in subjects:
            output_dir = os.path.join(derivatives_dir, args.output_tmp_folder, sub, ses)
            for pattern in args.patterns:
                pattern_glob = build_output_filename(sub, ses, args.template_name, pattern, modality, args.map_type, desc_str)
                all_warped_images.extend(glob.glob(os.path.join(output_dir, pattern_glob)))

        if not all_warped_images:
            print(f"No warped images for modality '{modality}', skipping average.")
            continue

        final_output = os.path.join(
            bids_root, "derivatives", "template",
            f"sub-{args.template_name}", args.template_session, args.template_folder,
            build_final_average_filename(args.template_name, args.template_session, modality, args.map_type, desc_str)
        )

        cmd = ["AverageImages", "3", final_output, "0"] + all_warped_images
        print(f"Averaging {len(all_warped_images)} images for modality '{modality}'")
        run_command(cmd, dry_run)


if __name__ == "__main__":
    main()
