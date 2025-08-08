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

def interpolate_contrast(template_name, ses_from, ses_to, template_path, output_path, contrasts, bids_root, args, keep_tmp=False):

    out_prefix = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / "long" / f"{ses_from}_to_{ses_to}_so_"

    #transfo_prefix = out_prefix / f"{ses_current}_flirt"

    for modality in contrasts:
        print(f"\nPropagating modality '{modality}' from session {ses_from} to {ses_to}")

        # # Chemins
        # base_dir = bids_root / "derivatives" / "template" / f"sub-{template_name}" / ses_current / template_path
        # src_img = base_dir / f"sub-{template_name}_{ses_current}_{modality}.nii.gz"
        #
        # flipped_img = base_dir / f"sub-{template_name}_{ses_current}_desc-flipped_space-CACP_{modality}.nii.gz"
        # warped_img = base_dir / f"sub-{template_name}_{ses_current}_desc-warped_space-CACP_{modality}.nii.gz"
        # warped_flipped_img = base_dir / f"sub-{template_name}_{ses_current}_desc-flipped-warped_space-CACP_{modality}.nii.gz"
        # sym_avg_img = base_dir / f"sub-{template_name}_{ses_current}_desc-sym_{modality}.nii.gz"
        #
        # # 1. Flip image
        # run_command(["fslswapdim", str(src_img), "-x", "y", "z", str(flipped_img)], dry_run=args.dry_run)
        # run_command(["CopyImageHeaderInformation", str(src_img), str(flipped_img), str(flipped_img), "1", "1", "1"], dry_run=args.dry_run)
        #
        # # 2. Apply transforms
        # run_command([
        #     "flirt", "-in", str(src_img), "-ref", str(src_img),
        #     "-applyxfm", "-init", anat2sym_mat, "-out", str(warped_img)
        # ], dry_run=args.dry_run)
        #
        # run_command([
        #     "flirt", "-in", str(flipped_img), "-ref", str(src_img),
        #     "-applyxfm", "-init", flip2sym_mat, "-out", str(warped_flipped_img)
        # ], dry_run=args.dry_run)
        #
        # # 3. Average
        # run_command([
        #     "fslmaths", str(warped_img), "-add", str(warped_flipped_img), "-div", "2", str(sym_avg_img)
        # ], dry_run=args.dry_run)
        #
        # print(f"  ➤ Source      : {relpath_from_cwd(src_img)}")
        # print(f"  ➤ Flipped     : {relpath_from_cwd(flipped_img)}")
        # print(f"  ➤ Warped      : {relpath_from_cwd(warped_img)}")
        # print(f"  ➤ Warped flip : {relpath_from_cwd(warped_flipped_img)}")
        # print(f"  ➤ Output sym  : {relpath_from_cwd(sym_avg_img)}")
        #
        # # 4. Clean up temporary files
        # if not keep_tmp and not args.dry_run:
        #     for tmp_file in [flipped_img, warped_img, warped_flipped_img]:
        #         try:
        #             tmp_file.unlink()
        #             print(f"  ➤ Removed temporary file: {relpath_from_cwd(tmp_file)}")
        #         except FileNotFoundError:
        #             pass
        #

def main():
    parser = argparse.ArgumentParser(description="Register templates across sessions using SyN only deformations")
    parser.add_argument("--bids_root", required=True, help="Root BIDS directory")
    parser.add_argument("--template_name", required=True, help="Template subject name")
    parser.add_argument("--sessions", nargs='+', required=True, help="List of sessions (ordered)")
    parser.add_argument("--registration_modalities", nargs='+',
                        help="Modalities to use for registration, e.g. T2w T1w")
    parser.add_argument("--suffix_modalities", nargs='+', required=True,
                        help="Suffix for each registration modality, same order as --registration_modalities")
    parser.add_argument("--registration_metrics", nargs='+', required=True,
                        help="Metrics corresponding to registration_modalities, e.g. MI CC or MI[1,32] CC[1,4]")
    parser.add_argument("--template_path", default="final", help="Subfolder for template")
    parser.add_argument("--output_path", default="intermediate", help="Subfolder for template")
    parser.add_argument("--compute-reg", action="store_true",default=False, help="compute registration")
    parser.add_argument("--contrasts_to_interpolate", nargs='*', help="Contrasts to interpolate across timepoints")
    parser.add_argument("--keep-tmp", action="store_true", help="Keep temporary files")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually run commands")

    args = parser.parse_args()
    bids_root = Path(args.bids_root)
    missing_files = []
    templates = {}

    # Check suffix length matches modalities
    if len(args.suffix_modalities) != len(args.registration_modalities):
        raise ValueError("--suffix_modalities must have same number of items as --registration_modalities")

    # Parse metrics and match to modalities
    metrics_dict = parse_metrics_arg(args.registration_modalities, args.registration_metrics)

    print("\n=== Checking input files ===")
    for ses in args.sessions:
        ses_dir = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses
        templates[ses] = {}

        for modality, suffix in zip(args.registration_modalities, args.suffix_modalities):
            fname = f"sub-{args.template_name}_{ses}_{suffix}_{modality}.nii.gz"
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

    print("\n=== Registering sessions ===")
    for i in range(len(args.sessions) - 1):
        ses_from = args.sessions[i]
        ses_to = args.sessions[i + 1]

        print(f"Registering {ses_from} → {ses_to}")
        out_prefix = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / "long" / f"{ses_from}_to_{ses_to}_so_"
        warped_prefix = f"{out_prefix}" + "desc-warped.nii.gz"
        out_prefix.parent.mkdir(parents=True, exist_ok=True)

        fixed_images = {}
        moving_images = {}
        missing_modalities = False

        for modality in args.registration_modalities:
            fixed = templates[ses_to].get(modality)
            moving = templates[ses_from].get(modality)

            if not fixed or not moving:
                print(f"Missing modality {modality} for SyN only registration {ses_from} → {ses_to}")
                missing_modalities = True

            fixed_images[modality] = fixed
            moving_images[modality] = moving

        if missing_modalities:
            print(f"Skipping registration {ses_from} → {ses_to} due to missing files")
            continue

        cmd = [
            "antsRegistration", "--verbose", "1", "--dimensionality", "3", "--float", "0",
            "--collapse-output-transforms", "1",
            "--output", f"[{relpath_from_cwd(out_prefix)},{relpath_from_cwd(warped_prefix)}]",
            "--interpolation", "Linear", "--use-histogram-matching", "0",
            "--winsorize-image-intensities", "[0.005,0.995]",
        ]

        cmd += ["--transform", "SyN[0.1,3,0]"]

        for modality in args.registration_modalities:
            metric_name, metric_params = metrics_dict[modality]
            metric_cmd = f"{metric_name}[{relpath_from_cwd(fixed_images[modality])}," \
                         f"{relpath_from_cwd(moving_images[modality])}," \
                         f"{','.join(metric_params)}]"
            cmd += ["--metric", metric_cmd]

        cmd += [
            "--convergence", "[100x60x30x10,1e-6,10]",
            "--shrink-factors", "8x4x2x1",
            "--smoothing-sigmas", "3x2x1x0vox",
        ]

        if args.compute_reg:
            print("\n=== compute registration ===")
            run_command(cmd, dry_run=args.dry_run)
        else:
            print("\n=== skip registration ===")

        print("\n=== Propagate symmetrization on other contrasts ===")
        if args.contrasts_to_interpolate:
            interpolate_contrast(
                args.template_name,
                ses_from,ses_to,
                args.template_path,
                args.output_path,
                args.contrasts_to_interpolate,
                bids_root,
                args=args,
                keep_tmp=args.keep_tmp
        )

if __name__ == "__main__":
    main()
