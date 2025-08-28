import os
import argparse
import subprocess
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation as R


def decompose_transformation(txt_file):
    """
    Decompose a 4x4 transformation matrix into translation and rotation (Euler angles)
    Returns rotation angles (rx, ry, rz) in degrees
    """
    T = np.loadtxt(txt_file)
    R_mat = T[:3, :3]
    rot = R.from_matrix(R_mat)
    rx, ry, rz = rot.as_euler('xyz', degrees=True)
    tx, ty, tz = T[0, 3], T[1, 3], T[2, 3]
    print("transformation matrix 4x4 :\n", T)
    print(f"Translation (x, y, z) : {tx:.6f}, {ty:.6f}, {tz:.6f}")
    print(f"Rotation (rx Pitch, ry Roll, rz Yaw) in degree : {rx:.3f}°, {ry:.3f}°, {rz:.3f}°")
    return np.array([rx, ry, rz])


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


def flip_anatomical_image(anat_path, flipped_path, dry_run):
    print(f"Flipping: {anat_path}")
    run_command(["fslswapdim", anat_path, "-x", "y", "z", flipped_path], dry_run=dry_run)
    run_command(["CopyImageHeaderInformation", anat_path, flipped_path, flipped_path, "1", "1", "1"], dry_run=dry_run)


def average_images(img1, img2, output, dry_run):
    #run_command(["fslmaths", img1, "-add", img2, "-div", "2", output], dry_run=dry_run)
    run_command(["AverageImages", "3", output, "0" ,img1, img2 ], dry_run=dry_run)


def run_flirt(in_img, ref_img, out_img, mat_file, dry_run, flirt_opts):
    """
    Compute a new transformation (registration) using FSL flirt.
    """
    cmd = ["flirt", "-in", in_img, "-ref", ref_img, "-o", out_img, "-omat", mat_file] + flirt_opts
    run_command(cmd, dry_run=dry_run)


def apply_flirt(in_img, ref_img, out_img, mat_file, dry_run):
    """
    Apply an existing flirt transformation matrix to an image.
    """
    cmd = ["flirt", "-in", in_img, "-ref", ref_img, "-applyxfm", "-init", mat_file, "-out", out_img]
    run_command(cmd, dry_run=dry_run)


def insert_symmetric_before_modality(filename: str, suffix: str = None) -> str:
    """
    Insert 'symmetric' before the last token in the filename (before modality)
    Optionally append a suffix like 'flipped' or 'warped'.
    """
    if not filename.endswith(".nii.gz"):
        return filename
    stem = filename.replace(".nii.gz", "")
    parts = stem.split("_")
    parts.insert(-1, "symmetric")
    if suffix:
        #parts.append(suffix)
        parts.insert(-1, suffix)

    return "_".join(parts) + ".nii.gz"


def symmetrize_session(ses_current, args, templates, bids_root, keep_tmp=False):
    """
    Symmetrize anatomical image iteratively until rotation angles are below threshold
    or maximum number of iterations is reached.
    """
    print(f"\n=== Processing session {ses_current} ===")
    out_prefix = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / ses_current
    out_prefix.mkdir(parents=True, exist_ok=True)
    transfo_prefix = out_prefix / f"{ses_current}_flirt"

    anat = templates[ses_current]
    anat_flipped = out_prefix / insert_symmetric_before_modality(
        f"sub-{args.template_name}_{ses_current}_{args.template_modality}.nii.gz", "flipped")
    anat_sym_tmp = out_prefix / insert_symmetric_before_modality(
        f"sub-{args.template_name}_{ses_current}_{args.template_modality}.nii.gz", "sym-tmp_mean")

    print(f"anat     : {anat}")
    print(f"flipped  : {anat_flipped}")

    # Step 0: initial flip + average
    flip_anatomical_image(anat, anat_flipped, args.dry_run)
    average_images(anat, anat_flipped, anat_sym_tmp, args.dry_run)

    iteration = 0
    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        # Step 1: compute transformations
        run_flirt(
            anat, anat_sym_tmp,
            str(out_prefix / insert_symmetric_before_modality(
                f"sub-{args.template_name}_{ses_current}_{args.template_modality}.nii.gz", "warped")),
            f"{transfo_prefix}_anat2sym.mat",
            args.dry_run,
            args.flirt_opts
        )

        run_flirt(
            anat_flipped, anat_sym_tmp,
            str(out_prefix / insert_symmetric_before_modality(
                f"sub-{args.template_name}_{ses_current}_{args.template_modality}.nii.gz", "flipped_warped")),
            f"{transfo_prefix}_flip2sym.mat",
            args.dry_run,
            args.flirt_opts
        )

        # Step 2: decompose transformations
        angles_anat = decompose_transformation(f"{transfo_prefix}_anat2sym.mat")
        angles_flip = decompose_transformation(f"{transfo_prefix}_flip2sym.mat")

        # Step 3: compute symmetry score
        symmetry_score = np.sum(np.abs(angles_anat + angles_flip))
        print(f"Symmetry score (sum of angle in degrees): {symmetry_score:.4f}")

        # Step 4: stopping conditions
        angles_below_threshold = symmetry_score < args.max_angle

        iter_exceeded = iteration >= args.max_iter

        # Step 5: average final warped images
        warped_img = out_prefix / insert_symmetric_before_modality(
            f"sub-{args.template_name}_{ses_current}_{args.template_modality}.nii.gz", "warped")
        warped_flipped_img = out_prefix / insert_symmetric_before_modality(
            f"sub-{args.template_name}_{ses_current}_{args.template_modality}.nii.gz", "flipped_warped")
        sym_final = out_prefix / insert_symmetric_before_modality(
            f"sub-{args.template_name}_{ses_current}_{args.template_modality}.nii.gz", f"ite{iteration}")

        average_images(warped_img, warped_flipped_img, sym_final, args.dry_run)

        if angles_below_threshold or iter_exceeded:
            if angles_below_threshold:
                print(f"symmetrical criteria {np.abs(angles_anat+angles_flip)} < ({args.max_angle}°). Stopping iterations.")
            if iter_exceeded:
                print(f"Maximum iterations reached ({args.max_iter}). Stopping iterations.")

            # Step 6: clean up temporary files
            if not keep_tmp and not args.dry_run:
                for tmp_file in [anat_flipped, warped_img, warped_flipped_img]:
                    try:
                        tmp_file.unlink()
                        print(f"  ➤ Removed temporary file: {relpath_from_cwd(tmp_file)}")
                    except FileNotFoundError:
                        pass
            break
        else:
            print("Angles above threshold, repeating iteration...")

        # change registration target for the next iteration
        anat_sym_tmp = sym_final


def propagate_symmetrization(template_name, ses_current, template_path, contrasts, bids_root, args, keep_tmp=False):
    out_prefix = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / ses_current
    transfo_prefix = out_prefix / f"{ses_current}_flirt"

    anat2sym_mat = f"{transfo_prefix}_anat2sym.mat"
    flip2sym_mat = f"{transfo_prefix}_flip2sym.mat"

    for modality in contrasts:
        print(f"\nPropagating modality '{modality}' for session {ses_current}")

        base_dir = bids_root / "derivatives" / "template" / f"sub-{template_name}" / ses_current / template_path
        src_img = base_dir / f"sub-{template_name}_{ses_current}_{modality}.nii.gz"

        flipped_img = base_dir / insert_symmetric_before_modality(f"sub-{template_name}_{ses_current}_{modality}.nii.gz", "flipped")
        warped_img = base_dir / insert_symmetric_before_modality(f"sub-{template_name}_{ses_current}_{modality}.nii.gz", "warped")
        warped_flipped_img = base_dir / insert_symmetric_before_modality(f"sub-{template_name}_{ses_current}_{modality}.nii.gz", "flipped_warped")
        sym_avg_img = base_dir / insert_symmetric_before_modality(f"sub-{template_name}_{ses_current}_{modality}.nii.gz")

        # Apply transformations
        apply_flirt(str(src_img), str(src_img), str(warped_img), anat2sym_mat, args.dry_run)

        flip_anatomical_image(src_img, flipped_img, args.dry_run)

        apply_flirt(str(flipped_img), str(src_img), str(warped_flipped_img), flip2sym_mat, args.dry_run)

        # Average
        average_images(warped_img, warped_flipped_img, sym_avg_img, args.dry_run)

        print(f"  ➤ Source      : {relpath_from_cwd(src_img)}")
        print(f"  ➤ Flipped     : {relpath_from_cwd(flipped_img)}")
        print(f"  ➤ Warped      : {relpath_from_cwd(warped_img)}")
        print(f"  ➤ Warped flip : {relpath_from_cwd(warped_flipped_img)}")
        print(f"  ➤ Output sym  : {relpath_from_cwd(sym_avg_img)}")

        if not keep_tmp and not args.dry_run:
            for tmp_file in [flipped_img, warped_img, warped_flipped_img]:
                try:
                    tmp_file.unlink()
                    print(f"  ➤ Removed temporary file: {relpath_from_cwd(tmp_file)}")
                except FileNotFoundError:
                    pass


def main():
    parser = argparse.ArgumentParser(description="Register templates across sessions in CA-CP space")
    parser.add_argument("--bids_root", required=True, help="Root BIDS directory")
    parser.add_argument("--template_name", required=True, help="Template subject name")
    parser.add_argument("--sessions", nargs='+', required=True, help="List of sessions (ordered)")
    parser.add_argument("--template_type", default="desc-average_padded_debiased_cropped_norm", required=True, help="Template type")
    parser.add_argument("--template_modality", required=True, default="T1w", help="Single modality for rigid registration")
    parser.add_argument("--template_path", default="final", help="Subfolder for template")
    parser.add_argument("--contrasts_to_sym", nargs='*', help="List of contrasts/maps to symmetrize")
    parser.add_argument("--keep-tmp", action="store_true", help="Keep temporary files (flipped/warped)")
    parser.add_argument("--compute-reg", action="store_true", default=False, help="Compute registration")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually run commands")
    parser.add_argument(
        "--flirt-opts",
        nargs=argparse.REMAINDER,
        default=["-dof", "6", "-searchrx", "-5", "5", "-searchry", "-5", "5", "-searchrz", "-5", "5"],
        help="Options to pass to FSL flirt (default rigid 6 dof, limited search)"
    )
    parser.add_argument("--max-angle", type=float, default=1.0, help="Maximum sum of Euler rotation angle (degrees) to stop iteration")
    parser.add_argument("--max-iter", type=int, default=10, help="Maximum number of iterations for symmetrization")

    args = parser.parse_args()
    bids_root = Path(args.bids_root)
    missing_files = []
    templates = {}

    print("\n=== Checking input files ===")
    for ses in args.sessions:
        ses_dir = bids_root / "derivatives" / "template" / f"sub-{args.template_name}" / ses
        templates[ses] = {}

        if args.template_modality:
            fname = f"sub-{args.template_name}_{ses}_{args.template_type}_{args.template_modality}.nii.gz"
            fpath = ses_dir / args.template_path / fname
            check_file(fpath, f"Template {args.template_modality}", missing_files, bids_root)
            templates[ses] = fpath if fpath.exists() else None

        if args.contrasts_to_sym:
            for modality in args.contrasts_to_sym:
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
    for ses_current in args.sessions:
        if args.compute_reg:
            print("\n=== compute registration ===")
            symmetrize_session(ses_current, args, templates, bids_root, keep_tmp=args.keep_tmp)
        else:
            print("\n=== skip registration ===")

        print("\n=== Propagate symmetrization on other contrasts ===")
        if args.contrasts_to_sym:
            propagate_symmetrization(
                args.template_name,
                ses_current,
                args.template_path,
                args.contrasts_to_sym,
                bids_root,
                args=args,
                keep_tmp=args.keep_tmp
            )


if __name__ == "__main__":
    main()
