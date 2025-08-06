import os
import argparse
import subprocess
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation as R


def decompose_transformation(txt_file):
    T = np.loadtxt(txt_file)
    # Translation
    tx, ty, tz = T[0, 3], T[1, 3], T[2, 3]
    # Rotation (3x3)
    R_mat = T[:3, :3]
    rot = R.from_matrix(R_mat)
    rx, ry, rz = rot.as_euler('xyz', degrees=True)  # 'xyz' = roll-pitch-yaw
    print("transformation matrix 4x4 :\n", T)
    print(f"Translation (x, y, z) : {tx:.6f}, {ty:.6f}, {tz:.6f}")
    print(f"Rotation (rx Pitch, ry Roll, rz Yaw) in degree : {rx:.3f}°, {ry:.3f}°, {rz:.3f}°")

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


from pathlib import Path

def flip_anatomical_image(anat_path, flipped_path, dry_run):
    print(f"Flipping: {anat_path}")
    run_command(["fslswapdim", anat_path, "-x", "y", "z", flipped_path], dry_run=dry_run)
    run_command(["CopyImageHeaderInformation", anat_path, flipped_path, flipped_path, "1", "1", "1"], dry_run=dry_run)

def average_images(anat_path, flipped_path, sym_output_path, dry_run):
    run_command(["fslmaths", anat_path, "-add", flipped_path, "-div", "2", sym_output_path], dry_run=dry_run)

def apply_flirt(in_img, ref_img, out_img, mat_file, dry_run):
    cmd = [
        "flirt", "-in", in_img, "-ref", ref_img,
        "-o", out_img, "-omat", mat_file,
        "-dof", "6",
        "-searchrx", "-5", "5",
        "-searchry", "-5", "5",
        "-searchrz", "-5", "5",
    ]
    run_command(cmd, dry_run=dry_run)

def average_images(img1, img2, output, dry_run):
    run_command(["fslmaths", img1, "-add", img2, "-div", "2", output], dry_run=dry_run)

def propagate_symmetrization(template_name, ses_current, template_path, contrasts, bids_root, args, keep_tmp=False):

    out_prefix = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / ses_current
    transfo_prefix = out_prefix / f"{ses_current}_flirt"

    anat2sym_mat = f"{transfo_prefix}_anat2sym.mat"
    flip2sym_mat = f"{transfo_prefix}_flip2sym.mat"

    for modality in contrasts:
        print(f"\nPropagating modality '{modality}' for session {ses_current}")

        # Chemins
        base_dir = bids_root / "derivatives" / "template" / f"sub-{template_name}" / ses_current / template_path
        src_img = base_dir / f"sub-{template_name}_{ses_current}_{modality}.nii.gz"

        flipped_img = base_dir / f"sub-{template_name}_{ses_current}_desc-flipped_space-CACP_{modality}.nii.gz"
        warped_img = base_dir / f"sub-{template_name}_{ses_current}_desc-warped_space-CACP_{modality}.nii.gz"
        warped_flipped_img = base_dir / f"sub-{template_name}_{ses_current}_desc-flipped-warped_space-CACP_{modality}.nii.gz"
        sym_avg_img = base_dir / f"sub-{template_name}_{ses_current}_desc-sym_{modality}.nii.gz"

        # 1. Flip image
        run_command(["fslswapdim", str(src_img), "-x", "y", "z", str(flipped_img)], dry_run=args.dry_run)
        run_command(["CopyImageHeaderInformation", str(src_img), str(flipped_img), str(flipped_img), "1", "1", "1"], dry_run=args.dry_run)

        # 2. Apply transforms
        run_command([
            "flirt", "-in", str(src_img), "-ref", str(src_img),
            "-applyxfm", "-init", anat2sym_mat, "-out", str(warped_img)
        ], dry_run=args.dry_run)

        run_command([
            "flirt", "-in", str(flipped_img), "-ref", str(src_img),
            "-applyxfm", "-init", flip2sym_mat, "-out", str(warped_flipped_img)
        ], dry_run=args.dry_run)

        # 3. Average
        run_command([
            "fslmaths", str(warped_img), "-add", str(warped_flipped_img), "-div", "2", str(sym_avg_img)
        ], dry_run=args.dry_run)

        print(f"  ➤ Source      : {relpath_from_cwd(src_img)}")
        print(f"  ➤ Flipped     : {relpath_from_cwd(flipped_img)}")
        print(f"  ➤ Warped      : {relpath_from_cwd(warped_img)}")
        print(f"  ➤ Warped flip : {relpath_from_cwd(warped_flipped_img)}")
        print(f"  ➤ Output sym  : {relpath_from_cwd(sym_avg_img)}")

        # 4. Clean up temporary files
        if not keep_tmp and not args.dry_run:
            for tmp_file in [flipped_img, warped_img, warped_flipped_img]:
                try:
                    tmp_file.unlink()
                    print(f"  ➤ Removed temporary file: {relpath_from_cwd(tmp_file)}")
                except FileNotFoundError:
                    pass

def symmetrize_session(ses_current, args, templates, bids_root,keep_tmp=False):
    print(f"\n=== Processing session {ses_current} ===")

    out_prefix = bids_root / "derivatives" / "transforms" / f"sub-{args.template_name}" / ses_current
    out_prefix.mkdir(parents=True, exist_ok=True)

    anat = templates[ses_current]
    anat_flipped = f"{out_prefix}/{ses_current}_desc-flipped.nii.gz"
    anat_sym_tmp = f"{out_prefix}/{ses_current}_desc-sym-tmp_mean.nii.gz"

    print(f"anat     : {anat}")
    print(f"flipped  : {anat_flipped}")

    flip_anatomical_image(anat, anat_flipped, args.dry_run)
    average_images(anat, anat_flipped, anat_sym_tmp, args.dry_run)

    transfo_prefix = out_prefix / f"{ses_current}_flirt"

    apply_flirt(
        anat, anat_sym_tmp,
        f"{transfo_prefix}_desc-warped.nii.gz",
        f"{transfo_prefix}_anat2sym.mat",
        args.dry_run
    )

    if not args.dry_run:
        decompose_transformation(f"{transfo_prefix}_anat2sym.mat")

    apply_flirt(
        anat_flipped, anat_sym_tmp,
        f"{transfo_prefix}_desc-flipped-warped.nii.gz",
        f"{transfo_prefix}_flip2sym.mat",
        args.dry_run
    )

    if not args.dry_run:
        decompose_transformation(f"{transfo_prefix}_anat2sym.mat")

    average_images(
        f"{transfo_prefix}_desc-warped.nii.gz",
        f"{transfo_prefix}_desc-flipped-warped.nii.gz",
        f"{transfo_prefix}_desc-sym_mean.nii.gz",
        args.dry_run
    )

    # Clean up temporary files
    if not keep_tmp and not args.dry_run:
        folder = Path(transfo_prefix).parent
        for filepath in folder.glob("*.nii.gz"):
            try:
                filepath.unlink()
                print(f"  ➤ Removed temporary file: {relpath_from_cwd(filepath)}")
            except FileNotFoundError:
                pass

def main():
    parser = argparse.ArgumentParser(description="Register templates across sessions in CA-CP space")
    parser.add_argument("--bids_root", required=True, help="Root BIDS directory")
    parser.add_argument("--template_name", required=True, help="Template subject name")
    parser.add_argument("--sessions", nargs='+', required=True, help="List of sessions (ordered)")
    parser.add_argument("--template_type", default="desc-symmetric-sharpen",required=True, help="Template type")
    parser.add_argument("--template_modality", required=True, help="single modality to use rigid flirt registration")
    parser.add_argument("--template_path", default="final", help="Subfolder for template")
    parser.add_argument("--contrasts_to_sym", nargs='*', help="Contrasts to symmetrize (")
    parser.add_argument("--keep-tmp", action="store_true", help="Keep temporary files (flipped/warped)")
    parser.add_argument("--compute-reg", action="store_true",default=False, help="compute registration")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually run commands")

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
            symmetrize_session(ses_current, args, templates, bids_root,keep_tmp=args.keep_tmp)
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