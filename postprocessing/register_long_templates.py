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
    parser = argparse.ArgumentParser(description="Check templates and register across sessions")
    parser.add_argument("--bids_root", required=True, help="Root BIDS directory")
    parser.add_argument("--template_name", required=True, help="Template subject name")
    parser.add_argument("--sessions", nargs='+', required=True, help="List of sessions (ordered)")
    parser.add_argument("--template_type", default="desc-symmetric-sharpen", help="Template type")
    parser.add_argument("--template_modalities", nargs='+', required=True, help="Modalities to use for registration")
    parser.add_argument("--brain_mask_suffix", help="Brain mask suffix")
    parser.add_argument("--segmentation_mask_suffix", help="Segmentation mask suffix")
    parser.add_argument("--template_path", default="norm", help="Subfolder for template")
    parser.add_argument("--TPM_path", default="final", help="Subfolder for TPMs")
    parser.add_argument("--brainmask_path", default="final", help="Subfolder for brain masks")
    parser.add_argument("--TPM_modalities", nargs='*', help="Optional TPM modalities")
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
            brain_mask_path = ses_dir / args.brainmask_path / brain_mask_name
            if check_file(brain_mask_path, "Brain mask", missing_files, bids_root):
                brainmasks[ses] = brain_mask_path

        if args.TPM_modalities:
            for modality in args.TPM_modalities:
                tpm_name = f"sub-{args.template_name}_{ses}_{modality}.nii.gz"
                tpm_path = ses_dir / args.TPM_path / tpm_name
                check_file(tpm_path, f"TPM {modality}", missing_files, bids_root)

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
        out_prefix.parent.mkdir(parents=True, exist_ok=True)

        fixed_brainmask = brainmasks[ses_to]
        moving_brainmask = brainmasks[ses_from]
        fixed_T1w = templates[ses_to].get("T1w")
        moving_T1w = templates[ses_from].get("T1w")
        fixed_T2w = templates[ses_to].get("T2w")
        moving_T2w = templates[ses_from].get("T2w")

        if not (fixed_brainmask and moving_brainmask and fixed_T2w and moving_T2w and fixed_T1w and moving_T1w):
            print(f"Skipping registration {ses_from} → {ses_to} due to missing files")
            continue

        cmd = [
            "antsRegistration", "--verbose", "1", "--dimensionality", "3", "--float", "0",
            "--collapse-output-transforms", "1",
            "--output",
            f"{relpath_from_cwd(out_prefix)}",
            "--interpolation", "Linear", "--use-histogram-matching", "0",
            "--winsorize-image-intensities", "[0.005,0.995]",
            "--initial-moving-transform",
            f"[{relpath_from_cwd(fixed_brainmask)},{relpath_from_cwd(moving_brainmask)},1]",
            "--transform", "Rigid[0.1]",
            "--metric",
            f"MI[{relpath_from_cwd(fixed_brainmask)},{relpath_from_cwd(moving_brainmask)},1,32,Regular,0.25]",
            f"MI[{relpath_from_cwd(fixed_T2w)},{relpath_from_cwd(moving_T2w)},1,32,Regular,0.25]",
            # f"MI[{relpath_from_cwd(fixed_T1w)},{relpath_from_cwd(moving_T1w)},1,32,Regular,0.25]",
            "--convergence", "[1000x500x250x100,1e-6,10]",
            "--shrink-factors", "12x8x4x2",
            "--smoothing-sigmas", "4x3x2x1vox"
            # "--transform", "SyN[0.1,3,0]",
            # "--metric",
            # f"MI[{relpath_from_cwd(fixed_T1w)},{relpath_from_cwd(moving_T1w)},1,32,Regular,0.25]",
            # f"MI[{relpath_from_cwd(fixed_T2w)},{relpath_from_cwd(moving_T2w)},1,32,Regular,0.25]",
            # "--convergence", "[30x20x10,1e-6,10]",
            # "--shrink-factors", "8x4x2",
            # "--smoothing-sigmas", "3x2x1vox"
        ]
        run_command(cmd, dry_run=args.dry_run)

    if args.segmentation_mask_suffix:
        print("\n=== Propagating segmentation mask ===")

        ref_ses = args.sessions[0]
        seg_fname_ref = f"sub-{args.template_name}_{ref_ses}_{args.segmentation_mask_suffix}.nii.gz"
        seg_path = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ref_ses / args.brainmask_path / seg_fname_ref

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
                #warp = transform_prefix.with_name(transform_prefix.name + "1Warp.nii.gz")

                #if not (affine.exists() and warp.exists()):
                if not (affine.exists()):
                    print(f"❌ Missing transforms for {current_source} → {ses_to}")
                    break

                # Prepend warp, then affine (ANTs expects last transform applied first)
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
                        / args.brainmask_path
                        / seg_fname_out
                )
                ref_T2w = templates[ses_to].get("T2w")

                if not ref_T2w:
                    print(f"No T2w for session {ses_to}, skipping.")
                    continue

                out_seg.parent.mkdir(parents=True, exist_ok=True)

                cmd = [
                    "antsApplyTransforms", "-d", "3",
                    "-i", relpath_from_cwd(seg_path),
                    "-r", relpath_from_cwd(ref_T2w),
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

        from_mask = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses_from / args.brainmask_path / f"sub-{args.template_name}_{ses_from}_{args.segmentation_mask_suffix}.nii.gz"
        to_mask = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses_to / args.brainmask_path / f"sub-{args.template_name}_{ses_to}_{args.segmentation_mask_suffix}.nii.gz"

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
            "-searchry", "-5", "5",
            "-searchrz", "-5", "5",
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
        ants_out = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses_from / args.brainmask_path / f"sub-{args.template_name}_{ses_from}_space-BaBa21-CACP_desc-3axis-mask.nii.gz"

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
    reference_mask = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / reference_ses / args.brainmask_path / f"sub-{args.template_name}_{reference_ses}_space-BaBa21-CACP_desc-3axis-mask.nii.gz"

    for src_ses in args.sessions[1:]:
        src_idx = args.sessions.index(src_ses)
        inverse_transforms = []

        # On compose les inverses de src_ses jusqu'à reference_ses
        for i in reversed(range(0, src_idx)):
            src_i = args.sessions[i + 1]
            tgt_i = args.sessions[i]
            mat_path = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / "long" / f"{tgt_i}_to_{src_i}_flirt_ants_rig.mat"
            inverse_transforms.append(f"[{str(mat_path)},1]")

        for modality in args.template_modalities:
            src_img = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / src_ses / args.template_path / f"sub-{args.template_name}_{src_ses}_{args.template_type}_{modality}.nii.gz"
            out_img = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / src_ses / args.template_path / f"sub-{args.template_name}_{src_ses}_space-CACP_{args.template_type}_{modality}.nii.gz"

            print(f"\nPropagating modality '{modality}' from {src_ses} to {reference_ses}")
            print(f"  ➤ Source image : {relpath_from_cwd(src_img)}")
            print(f"  ➤ Target space : {relpath_from_cwd(reference_mask)}")
            print(f"  ➤ Output       : {relpath_from_cwd(out_img)}")
            print(f"  ➤ Applied inverse transforms:")
            for tfm in inverse_transforms:
                print(f"     - {tfm}")

            cmd = [
                "antsApplyTransforms", "-d", "3","-i", str(src_img),"-o", str(out_img),"-r", str(reference_mask),"--verbose", "1"
            ]
            for tfm in inverse_transforms:
                cmd += ["-t", tfm]

            run_command(cmd, dry_run=args.dry_run)

        for modality in args.TPM_modalities:

            src_img = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / src_ses / args.TPM_path / f"sub-{args.template_name}_{src_ses}_{modality}.nii.gz"
            out_img = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / src_ses / args.TPM_path / f"sub-{args.template_name}_{src_ses}_space-CACP_{modality}.nii.gz"

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