import os
import argparse
import subprocess
from pathlib import Path

def relpath_from_cwd(filepath):
    """Return path relative to current working directory."""
    filepath_abs = os.path.abspath(filepath)
    cwd_abs = os.path.abspath(os.getcwd())
    return os.path.relpath(filepath_abs, cwd_abs)

def check_file(filepath, label, missing_list, bids_root):
    """Check if a file exists and print status."""
    if os.path.exists(filepath):
        print(f"  ✅ Found {label}: {relpath_from_cwd(filepath)}")
        return True
    else:
        print(f"  ❌ Missing {label}: {relpath_from_cwd(filepath)}")
        missing_list.append(relpath_from_cwd(filepath))
        return False

def run_command(cmd, dry_run=False):
    """Run a shell command unless dry_run is True."""
    print("Running:", " ".join(map(str, cmd)))
    if not dry_run:
        subprocess.run(cmd, check=True)

# =====================
# Morphing stubs (Step 1)
# =====================

def compute_blending(n, numsteps):
    """Compute blending coefficients A and B, plus blend percentage name."""
    blending_a = round(n / numsteps, 2)
    blending_b = round(1 - blending_a, 2)
    blend_name = int(blending_a * 100)
    return blending_a, blending_b, blend_name

def morph_frame(n, ses_from, ses_to, args, bids_root, contrasts):
    """
    Generate a single intermediate morph frame for all contrasts in --contrasts_to_interpolate.
    Skip scaled warp calculation if files already exist.
    """
    blending_a, blending_b, blend_name = compute_blending(n, args.morph_numsteps)

    out_prefix = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}"
    long_dir = out_prefix / "long"
    tmpdir = long_dir / args.morph_tmpdir
    tmpdir.mkdir(parents=True, exist_ok=True)

    # Input warps (already computed if --compute-reg was used)
    warp_in = long_dir / f"{ses_from}_to_{ses_to}_{args.reg_long_type}_so_0Warp.nii.gz"
    invwarp_in = long_dir / f"{ses_from}_to_{ses_to}_{args.reg_long_type}_so_0InverseWarp.nii.gz"

    if not warp_in.exists() or not invwarp_in.exists():
        raise FileNotFoundError(
            f"Missing warp fields: {warp_in} or {invwarp_in}. "
            f"Run with --compute-reg first to generate them."
        )

    # Scaled warp outputs
    warp_scaled = tmpdir / f"{ses_from}_to_{ses_to}_{args.reg_long_type}_inter{blend_name}_0Warp.nii.gz"
    invwarp_scaled = tmpdir / f"{ses_from}_to_{ses_to}_{args.reg_long_type}_inter{blend_name}_0InverseWarp.nii.gz"

    # Scale warps only if they don't exist
    if not warp_scaled.exists():
        run_command(["MultiplyImages", "3", str(warp_in), str(blending_b), str(warp_scaled)], dry_run=args.dry_run)
    else:
        print(f"[morph_frame] Warp already exists, skipping: {warp_scaled}")

    if not invwarp_scaled.exists():
        run_command(["MultiplyImages", "3", str(invwarp_in), str(blending_a), str(invwarp_scaled)], dry_run=args.dry_run)
    else:
        print(f"[morph_frame] InverseWarp already exists, skipping: {invwarp_scaled}")

    morph_outputs = []

    for contrast in contrasts:
        # Temp images for this contrast
        temp_src = tmpdir / f"{contrast}_src_{blend_name}.nii.gz"
        temp_tgt = tmpdir / f"{contrast}_tgt_{blend_name}.nii.gz"

        # Input images
        fixed_img = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses_to / args.template_path / f"sub-{args.template_name}_{ses_to}_{contrast}.nii.gz"
        moving_img = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses_from / args.template_path / f"sub-{args.template_name}_{ses_from}_{contrast}.nii.gz"

        # Apply scaled warps
        run_command(["antsApplyTransforms", "-d", "3", "-i", str(moving_img), "-r", str(fixed_img),
                     "-o", str(temp_src), "-t", str(warp_scaled)], dry_run=args.dry_run)
        run_command(["antsApplyTransforms", "-d", "3", "-i", str(fixed_img), "-r", str(moving_img),
                     "-o", str(temp_tgt), "-t", str(invwarp_scaled)], dry_run=args.dry_run)

        # Intensity reweighting
        run_command(["ImageMath", "3", str(temp_src), "m", str(temp_src), str(blending_a)], dry_run=args.dry_run)
        run_command(["ImageMath", "3", str(temp_tgt), "m", str(temp_tgt), str(blending_b)], dry_run=args.dry_run)

        # Sum images
        morph_out = tmpdir / f"{contrast}_morph_{blend_name}.nii.gz"
        run_command(["ImageMath", "3", str(morph_out), "+", str(temp_src), str(temp_tgt)], dry_run=args.dry_run)

        print(f"[morph_frame] Generated {morph_out}")
        morph_outputs.append(morph_out)

    return morph_outputs

def morph_series(ses_from, ses_to, args, bids_root, contrasts):
    """
    Generate the full morphing series across steps for all contrasts.
    Returns a dictionary: {contrast: [morph_step1, morph_step2, ...]}
    """
    print(f"=== Morphing series {ses_from} → {ses_to} ===")

    morphs_per_contrast = {contrast: [] for contrast in contrasts}

    for n in range(0, args.morph_numsteps + 1, args.morph_step):
        print(f"\n--- Morph step {n} ---")
        morph_outputs = morph_frame(n, ses_from, ses_to, args, bids_root, contrasts)

        for contrast, morph_file in zip(contrasts, morph_outputs):
            morphs_per_contrast[contrast].append(morph_file)

    return morphs_per_contrast


def merge_4d(morph_files_dict, ses_from, ses_to, args, bids_root):
    """
    Merge intermediate morph frames into a 4D file per contrast using fslmerge.

    morph_files_dict: dict of {contrast: [morph_step1, morph_step2, ...]}
    ses_from, ses_to: session names
    """
    print(f"\n=== Merging 4D morphs {ses_from} → {ses_to} ===")
    out_prefix = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / "long"
    tmpdir = out_prefix / args.morph_tmpdir
    tmpdir.mkdir(parents=True, exist_ok=True)

    for contrast, files in morph_files_dict.items():
        # Ensure files exist
        existing_files = [str(f) for f in files if f.exists()]
        if not existing_files:
            print(f"⚠️ No morph files found for contrast {contrast}, skipping 4D merge.")
            continue

        # Output 4D file
        out_4d = out_prefix / f"{ses_from}_to_{ses_to}_{args.reg_long_type}_{contrast}_morph_4D.nii.gz"
        cmd = ["fslmerge", "-t", str(out_4d)] + existing_files
        run_command(cmd, dry_run=args.dry_run)

        print(f"[merge_4d] Created 4D morph: {out_4d}")


# =====================
# End Morphing stubs
# =====================

def parse_metrics_arg(modalities, metrics):
    """
    Parse the --registration_metrics argument and assign to each modality.
    Fill missing parameters with ANTs defaults:
      MI: [weight=1, numberOfBins=32, samplingStrategy=None, samplingPercentage=1, useGradientFilter=0]
      CC: [weight=1, radius=4, samplingStrategy=None, samplingPercentage=1, useGradientFilter=0]
    """
    if len(metrics) != len(modalities):
        raise ValueError("--registration_metrics must have same number of items as --registration_modalities")

    metrics_dict = {}
    for modality, metric in zip(modalities, metrics):
        metric_name = metric.split("[")[0]  # Extract MI or CC
        metric_params = []

        if "[" in metric:
            params_str = metric.split("[", 1)[1].rstrip("]")
            metric_params = [p.strip() for p in params_str.split(",") if p.strip()]

        # Defaults per metric type
        if metric_name == "MI":
            defaults = ["1", "32", "None", "1", "0"]
        elif metric_name == "CC":
            defaults = ["1", "4", "None", "1", "0"]
        else:
            raise ValueError(f"Unsupported metric type: {metric_name}")

        while len(metric_params) < len(defaults):
            metric_params.append(defaults[len(metric_params)])

        metrics_dict[modality] = (metric_name, metric_params)

    return metrics_dict

def interpolate_contrast(template_name, ses_from, ses_to, fixed, moving, template_path, output_path, contrasts, bids_root, args, keep_tmp=False):

    out_prefix = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}"

    out_path = out_prefix / output_path
    out_path.mkdir(parents=True, exist_ok=True)

    warp_prefix = out_prefix / "long" / f"{ses_from}_to_{ses_to}_{args.reg_long_type}_so_0Warp.nii.gz"
    invwarp_prefix = out_prefix / "long" / f"{ses_from}_to_{ses_to}_{args.reg_long_type}_so_0InverseWarp.nii.gz"

    for modality in contrasts:
        print(f"\nPropagating modality '{modality}' from session {ses_from} to {ses_to}")

        ses_dir = bids_root / "derivatives" / "template" / f"sub-{args.template_name}"

        contrast_from = ses_dir / f"{ses_from}" / args.template_path / f"sub-{args.template_name}_{ses_from}_{modality}.nii.gz"
        contrast_to = ses_dir / f"{ses_to}" / args.template_path / f"sub-{args.template_name}_{ses_to}_{modality}.nii.gz"

        warped = out_path / f"{ses_from}_to_{ses_to}_{args.reg_long_type}_{modality}.nii.gz"
        inverse_warped = out_path / f"{ses_to}_to_{ses_from}_{args.reg_long_type}_{modality}.nii.gz"

        cmd = [
             "antsApplyTransforms", "-d", "3",
             "-i", relpath_from_cwd(contrast_from),
             "-r", relpath_from_cwd(fixed),
             "-o", relpath_from_cwd(warped),
             "-t", relpath_from_cwd(warp_prefix),
             "--interpolation", "Linear",
             "--verbose", "1"
         ]

        run_command(cmd, dry_run=args.dry_run)

        cmd = [
             "antsApplyTransforms", "-d", "3",
             "-i", relpath_from_cwd(contrast_to),
             "-r", relpath_from_cwd(moving),
             "-o", relpath_from_cwd(inverse_warped),
             "-t", relpath_from_cwd(invwarp_prefix),
             "--interpolation", "Linear",
             "--verbose", "1"
         ]

        run_command(cmd, dry_run=args.dry_run)


def main():
    parser = argparse.ArgumentParser(description="Register templates across sessions using SyN only deformations")
    parser.add_argument("--bids_root", required=True, help="Root BIDS directory")
    parser.add_argument("--template_name", required=True, help="Template subject name")
    parser.add_argument("--sessions", nargs='+', required=True, help="List of sessions (ordered)")
    parser.add_argument("--registration_modalities", nargs='+',
                        help="Modalities to use for registration, e.g. T2w T1w")
    parser.add_argument("--template_prefix", required=True,
                        help="Template prefix used for registration (space-CACP_desc-average_padded_debiased_cropped_norm_symmetric)")
    parser.add_argument("--registration_metrics", nargs='+', required=True,
                        help="Metrics corresponding to registration_modalities, e.g. MI CC or MI[1,32] CC[1,4]")
    parser.add_argument("--template_path", default="final", help="Subfolder for template")
    parser.add_argument("--reg_long_type", default="CACP_MM", help="name of registration type")
    parser.add_argument("--output_path", default="intermediate", help="Subfolder for template")
    parser.add_argument("--compute-reg", action="store_true",default=False, help="compute registration")
    parser.add_argument("--contrasts_to_interpolate", nargs='*', default=[],
                        help="Contrasts to interpolate across timepoints")
    parser.add_argument("--keep-tmp", action="store_true", help="Keep temporary files")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually run commands")

    # --- Morphing options (Step 1) ---
    parser.add_argument("--morph-enable", action="store_true",
                        help="Enable morphing between two sessions")
    parser.add_argument("--morph-numsteps", type=int, default=10,
                        help="Number of morphing steps (default=10)")
    parser.add_argument("--morph-step", type=int, default=1,
                        help="Morphing increment (default=1)")
    parser.add_argument("--morph-tmpdir", default="tmp",
                        help="Temporary directory for morphing images")
    parser.add_argument("--morph-merge4d", action="store_true",
                        help="Merge all morphs into one 4D file with fslmerge")

    args = parser.parse_args()
    bids_root = Path(args.bids_root)
    missing_files = []
    templates = {}

    # Parse metrics and match to modalities
    metrics_dict = parse_metrics_arg(args.registration_modalities, args.registration_metrics)

    print("\n=== Checking input files ===")
    for ses in args.sessions:
        ses_dir = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses
        templates[ses] = {}

        for modality in args.registration_modalities:
            prefix = args.template_prefix
            fname = f"sub-{args.template_name}_{ses}_{prefix}_{modality}.nii.gz"
            fpath = ses_dir / args.template_path / fname
            check_file(fpath, f"Template {modality}", missing_files, bids_root)
            templates[ses][modality] = fpath if fpath.exists() else None

        if args.contrasts_to_interpolate:
            for modality in args.contrasts_to_interpolate:
                contrast_name = f"sub-{args.template_name}_{ses}_{modality}.nii.gz"
                template_path = ses_dir / args.template_path / contrast_name
                check_file(template_path, f"Contrast {modality}", missing_files, bids_root)

    if missing_files:
        print("\nSummary: Missing files detected:")
        for f in missing_files:
            print(" -", f)
        exit(1)
    else:
        print("\nAll required files found!")

    print("\n=== Registration sessions ===")

    # --- Pipeline complet sécurisé ---
    for i in range(len(args.sessions) - 1):
        ses_from = args.sessions[i]
        ses_to = args.sessions[i + 1]

        print(f"\n=== Processing {ses_from} → {ses_to} ===")

        # Check if templates exist for these sessions
        if ses_from not in templates or ses_to not in templates:
            print(f"⚠️ Templates for sessions {ses_from} or {ses_to} not found. Skipping registration.")
            continue

        out_prefix = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / "long"
        out_prefix.mkdir(parents=True, exist_ok=True)

        # --- Check registration modalities ---
        fixed_images = {}
        moving_images = {}
        missing_modalities = False

        for modality in args.registration_modalities:
            fixed = templates[ses_to].get(modality)
            moving = templates[ses_from].get(modality)

            if fixed is None or moving is None:
                print(f"⚠️ Modality {modality} missing for {ses_from} → {ses_to}")
                missing_modalities = True

            fixed_images[modality] = fixed
            moving_images[modality] = moving

        if missing_modalities:
            print(f"Skipping registration {ses_from} → {ses_to} due to missing modalities")
            continue

        # --- Registration step ---
        warp_file = out_prefix / f"{ses_from}_to_{ses_to}_{args.reg_long_type}_so_0Warp.nii.gz"
        invwarp_file = out_prefix / f"{ses_from}_to_{ses_to}_{args.reg_long_type}_so_0InverseWarp.nii.gz"

        if args.compute_reg or not (warp_file.exists() and invwarp_file.exists()):
            print("\n=== Computing registration ===")
            reg_out_prefix = out_prefix / f"{ses_from}_to_{ses_to}_{args.reg_long_type}_so_"
            cmd = [
                "antsRegistration", "--verbose", "1", "--dimensionality", "3", "--float", "0",
                "--collapse-output-transforms", "1",
                "--output", f"{relpath_from_cwd(reg_out_prefix)}",
                "--interpolation", "Linear", "--use-histogram-matching", "0",
                "--winsorize-image-intensities", "[0.005,0.995]",
                "--transform", "SyN[0.1,3,0]",
            ]
            for modality in args.registration_modalities:
                metric_name, metric_params = metrics_dict[modality]
                metric_cmd = f"{metric_name}[{relpath_from_cwd(fixed_images[modality])}," \
                             f"{relpath_from_cwd(moving_images[modality])}," \
                             f"{','.join(metric_params)}]"
                cmd += ["--metric", metric_cmd]

            cmd += [
                #"--convergence", "[100x60x30x10,1e-6,10]",
                "--convergence", "[100x60x0x0,1e-6,10]",
                "--shrink-factors", "8x4x2x1",
                "--smoothing-sigmas", "3x2x1x0vox",
            ]
            run_command(cmd, dry_run=args.dry_run)
        else:
            print("Registration skipped (Warp/InverseWarp already exist)")

        # --- Morphing step ---
        if args.morph_enable:
            if not args.contrasts_to_interpolate:
                print("⚠️ --morph_enable is set but no contrasts provided. Skipping morphing.")
            else:
                print("\n=== Morphing enabled ===")
                morph_files_dict = morph_series(ses_from, ses_to, args, bids_root, args.contrasts_to_interpolate)

                # --- Merge 4D if requested ---
                if args.morph_merge4d:
                    merge_4d(morph_files_dict, ses_from, ses_to, args, bids_root)
        else:
            print("=== Morphing disabled ===")



if __name__ == "__main__":
    main()
