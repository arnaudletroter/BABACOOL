import os
import argparse
import subprocess
from pathlib import Path

def relpath_from_cwd(filepath):
    filepath_abs = os.path.abspath(filepath)
    cwd_abs = os.path.abspath(os.getcwd())
    return os.path.relpath(filepath_abs, cwd_abs)


def check_file(filepath, label, missing_list, bids_root):
    if os.path.exists(filepath):
        print(f"  ✅ Found {label}: {relpath_from_cwd(filepath)}")
        return True
    else:
        print(f"  ❌ Missing {label}: {relpath_from_cwd(filepath)}")
        missing_list.append(relpath_from_cwd(filepath, bids_root))
        return False

def run_command(cmd, dry_run=False):
    print("Running:", " ".join(map(str, cmd)))
    if not dry_run:
        subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="Register templates across sessions in CA-CP space")
    parser.add_argument("--bids_root", required=True, help="Root BIDS directory")
    parser.add_argument("--template_name", required=True, help="Template subject name")
    parser.add_argument("--sessions", nargs='+', required=True, help="List of sessions (ordered)")
    parser.add_argument("--template_type", default="desc-symmetric-sharpen",required=True, help="Template type")
    parser.add_argument("--template_modalities", nargs='+', required=True, help="Modalities to use for registration")
    parser.add_argument("--template_path", default="final", help="Subfolder for template")
    parser.add_argument("--brain_mask_suffix", help="Brain mask suffix")
    parser.add_argument("--segmentation_mask_suffix", help="Segmentation mask suffix")
    parser.add_argument("--contrasts_to_warp", nargs='*', help="Contrasts to warp in CA-CP space (")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually run commands")

    args = parser.parse_args()
    #bids_root = Path(args.bids_root).resolve()
    bids_root = Path(args.bids_root)
    missing_files = []
    templates = {}
    brainmasks = {}

    print("\n=== Checking input files ===")
    for ses in args.sessions:
        ses_dir = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses
        templates[ses] = {}
        brainmasks[ses] = None

        for modality in args.template_modalities:
            fname = f"sub-{args.template_name}_{ses}_{args.template_type}_{modality}.nii.gz"
            fpath = ses_dir / args.template_path / fname
            check_file(fpath, f"Template {modality}", missing_files, bids_root)
            templates[ses][modality] = fpath if fpath.exists() else None

        if args.brain_mask_suffix:
            brain_mask_name = f"sub-{args.template_name}_{ses}_{args.brain_mask_suffix}.nii.gz"
            brain_mask_path = ses_dir / args.template_path / brain_mask_name
            if check_file(brain_mask_path, "Brain mask", missing_files, bids_root):
                brainmasks[ses] = brain_mask_path

        if args.contrasts_to_warp:
            for modality in args.contrasts_to_warp:
                tpm_name = f"sub-{args.template_name}_{ses}_{modality}.nii.gz"
                template_path = ses_dir / args.template_path / tpm_name
                check_file(template_path, f"TPM {modality}", missing_files, bids_root)

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
        out_prefix = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / "long" / f"{ses_from}_to_{ses_to}_"
        warped_prefix = f"{out_prefix}"+"desc-warped.nii.gz"
        out_prefix.parent.mkdir(parents=True, exist_ok=True)

        fixed_brainmask = brainmasks[ses_to]
        moving_brainmask = brainmasks[ses_from]

        # Retrieve fixed and moving images for each modality
        fixed_images = {}
        moving_images = {}
        missing_modalities = False

        for modality in args.template_modalities:
            fixed = templates[ses_to].get(modality)
            moving = templates[ses_from].get(modality)

            if not fixed or not moving:
                print(f"Missing modality {modality} for registration {ses_from} → {ses_to}")
                missing_modalities = True

            fixed_images[modality] = fixed
            moving_images[modality] = moving

        # Also check for brainmasks
        if not fixed_brainmask or not moving_brainmask or missing_modalities:
            print(f"Skipping registration {ses_from} → {ses_to} due to missing files")
            continue

        # Start building the ANTs command
        cmd = [
            "antsRegistration", "--verbose", "1", "--dimensionality", "3", "--float", "0",
            "--collapse-output-transforms", "1",
            "--output", f"[{relpath_from_cwd(out_prefix)},{relpath_from_cwd(warped_prefix)}]",
            "--interpolation", "Linear", "--use-histogram-matching", "0",
            "--winsorize-image-intensities", "[0.005,0.995]",
        ]

        # Use T1w as reference for initial transform if available
        ref_modality = "T1w" if "T1w" in fixed_images else args.template_modalities[0]

        cmd += [
            "--initial-moving-transform",
            f"[{relpath_from_cwd(fixed_images[ref_modality])},{relpath_from_cwd(moving_images[ref_modality])},1]"
        ]

        # Rigid stage
        cmd += ["--transform", "Rigid[0.1]"]
        for modality in args.template_modalities:
            cmd += [
                "--metric",
                f"MI[{relpath_from_cwd(fixed_images[modality])},{relpath_from_cwd(moving_images[modality])},1,32,Regular,0.25]"
            ]
        cmd += [
            "--convergence", "[1000x500x250x100,1e-6,10]",
            "--shrink-factors", "12x8x4x2",
            "--smoothing-sigmas", "4x3x2x1vox",
        ]

        # Affine stage
        cmd += ["--transform", "Affine[0.1]"]
        for modality in args.template_modalities:
            cmd += [
                "--metric",
                f"MI[{relpath_from_cwd(fixed_images[modality])},{relpath_from_cwd(moving_images[modality])},1,32,Regular,0.25]"
            ]
        cmd += [
            "--convergence", "[1000x500x250x100,1e-6,10]",
            "--shrink-factors", "12x8x4x2",
            "--smoothing-sigmas", "4x3x2x1vox",
        ]

        # Run the command
        run_command(cmd, dry_run=args.dry_run)

    if args.segmentation_mask_suffix:
        print("\n=== Propagating segmentation mask ===")

        ref_ses = args.sessions[0]
        seg_fname_ref = f"sub-{args.template_name}_{ref_ses}_{args.segmentation_mask_suffix}.nii.gz"
        seg_path = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ref_ses / args.template_path / seg_fname_ref

        if not seg_path.exists():
            print(f"Segmentation mask not found: {relpath_from_cwd(seg_path)}")
        else:
            cumulative_transforms = []
            current_source = ref_ses

            for ses_to in args.sessions[1:]:
                # Transform files location (in sub-BaBa21/long/)
                transform_prefix = (
                        bids_root
                        / "derivatives"
                        / "transforms"
                        / f"sub-{args.template_name}"
                        / "long"
                        / f"{current_source}_to_{ses_to}_"
                )

                affine = transform_prefix.with_name(transform_prefix.name + "0GenericAffine.mat")
                warp = transform_prefix.with_name(transform_prefix.name + "1Warp.nii.gz")

                #if not (affine.exists() and warp.exists()):
                if not (affine.exists()):
                    print(f"❌ Missing transforms for {current_source} → {ses_to}")
                    break

                #cumulative_transforms = [relpath_from_cwd(warp), relpath_from_cwd(affine)] + cumulative_transforms
                cumulative_transforms = [relpath_from_cwd(affine)] + cumulative_transforms

                # Output path → template/sub-XXX/ses-Y/paper/sub-XXX_ses-Y_....nii.gz
                seg_fname_out = f"sub-{args.template_name}_{ses_to}_{args.segmentation_mask_suffix}.nii.gz"
                out_seg = (
                        bids_root
                        / "derivatives"
                        / "template"
                        / f"sub-{args.template_name}"
                        / ses_to
                        / args.template_path
                        / seg_fname_out
                )
                ref_T1w = templates[ses_to].get("T1w")

                if not ref_T1w:
                    print(f"No T2w for session {ses_to}, skipping.")
                    continue

                out_seg.parent.mkdir(parents=True, exist_ok=True)

                cmd = [
                    "antsApplyTransforms", "-d", "3",
                    "-i", relpath_from_cwd(seg_path),
                    "-r", relpath_from_cwd(ref_T1w),
                    "-o", relpath_from_cwd(out_seg),
                    "--interpolation", "NearestNeighbor",
                    "--verbose", "1"
                ]

                for transform in cumulative_transforms:
                    cmd += ["-t", transform]

                run_command(cmd, dry_run=args.dry_run)

                # Next step: propagate from this target
                current_source = ses_to

    print("\n=== Stage 2: FLIRT rigid registration and ANTs transform ===")
    for i in range(len(args.sessions) - 1):
        ses_from = args.sessions[i]
        ses_to = args.sessions[i + 1]

        print(f"FLIRT registration {ses_from} → {ses_to}")

        from_mask = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses_from / args.template_path / f"sub-{args.template_name}_{ses_from}_{args.segmentation_mask_suffix}.nii.gz"
        to_mask = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses_to / args.template_path / f"sub-{args.template_name}_{ses_to}_{args.segmentation_mask_suffix}.nii.gz"

        flirt_mat = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / "long" / f"{ses_from}_to_{ses_to}_flirt.mat"
        flirt_mat.parent.mkdir(parents=True, exist_ok=True)

        flirt_out = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / "long" / f"{ses_from}_to_{ses_to}_flirt_warped.nii.gz"
        flirt_out.parent.mkdir(parents=True, exist_ok=True)

        # 1. FLIRT
        cmd_flirt = [
            "flirt", "-in", relpath_from_cwd(from_mask), "-ref",  relpath_from_cwd(to_mask),
            "-o", relpath_from_cwd(flirt_out), "-omat", relpath_from_cwd(flirt_mat),
            "-dof", "6",
            "-searchrx", "-30", "30",
            "-searchry", "0", "0",
            "-searchrz", "0", "0",
            "-v"
        ]
        run_command(cmd_flirt, dry_run=args.dry_run)

        # 2. Convert FLIRT matrix to ITK format
        ants_mat = flirt_mat.with_name(flirt_mat.stem.replace(".mat", "") + "_ants_rig.mat")
        cmd_c3d = [
            "c3d_affine_tool",
            "-ref", relpath_from_cwd(to_mask),
            "-src", relpath_from_cwd(from_mask),
            relpath_from_cwd(flirt_mat),
            "-fsl2ras",
            "-oitk", relpath_from_cwd(ants_mat)
        ]
        run_command(cmd_c3d, dry_run=args.dry_run)

        # 3. Apply transform using ANTs
        ants_out = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses_from / args.template_path / f"sub-{args.template_name}_{ses_from}_space-CACP_desc-3axis-mask.nii.gz"

        cmd_apply = [
            "antsApplyTransforms", "-d", "3",
            "-i", relpath_from_cwd(from_mask),
            "-o", relpath_from_cwd(ants_out),
            "-r", relpath_from_cwd(to_mask),
            "-t", relpath_from_cwd(ants_mat)
        ]
        run_command(cmd_apply, dry_run=args.dry_run)


    print("\n=== Stage 3: Propagate modalities into reference session using inverse transforms ===")
    reference_ses = args.sessions[0]
    reference_mask = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / reference_ses / args.template_path / f"sub-{args.template_name}_{reference_ses}_space-CACP_desc-3axis-mask.nii.gz"

    for src_ses in args.sessions[1:]:
        src_idx = args.sessions.index(src_ses)
        inverse_transforms = []

        for i in reversed(range(0, src_idx)):
            src_i = args.sessions[i + 1]
            tgt_i = args.sessions[i]
            mat_path = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / "long" / f"{tgt_i}_to_{src_i}_flirt_ants_rig.mat"
            inverse_transforms.append(f"[{str(mat_path)},1]")

        for modality in args.contrasts_to_warp:

            src_img = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / src_ses / args.template_path / f"sub-{args.template_name}_{src_ses}_{modality}.nii.gz"
            out_img = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / src_ses / args.template_path / f"sub-{args.template_name}_{src_ses}_space-CACP_{modality}.nii.gz"

            print(f"\nPropagating modality '{modality}' from {src_ses} to {reference_ses}")
            print(f"  ➤ Source image : {relpath_from_cwd(src_img)}")
            print(f"  ➤ Target space : {relpath_from_cwd(reference_mask)}")
            print(f"  ➤ Output       : {relpath_from_cwd(out_img)}")
            print(f"  ➤ Applied inverse transforms:")
            for tfm in inverse_transforms:
                print(f"     - {tfm}")

            cmd = [
                "antsApplyTransforms", "-d", "3", "-i", str(src_img), "-o", str(out_img), "-r", str(reference_mask),
                "--verbose", "1"
            ]
            for tfm in inverse_transforms:
                cmd += ["-t", tfm]

            run_command(cmd, dry_run=args.dry_run)

if __name__ == "__main__":
    main()