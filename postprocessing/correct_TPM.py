import os
import argparse
import subprocess
import json

def run_command(cmd, dry_run=False, env=None):
    print("Running:", " ".join(map(str, cmd)))
    if not dry_run:
        subprocess.run(cmd, check=True, env=env)


def write_tpm_json(mask_files_thr, mask_files, threshold, thr_str, dry_run=False):
    """
    Write a BIDS-compliant JSON sidecar for each thresholded TPM, with dry-run option.
    """
    for tissue, filepath in mask_files_thr.items():
        # Replace NIfTI extension by JSON
        json_path = filepath.replace(".nii.gz", ".json")

        # Get the source probability map for this tissue
        source_path = mask_files.get(tissue, None)
        source_fname = os.path.basename(source_path) if source_path else "unknown"

        # Build JSON content
        json_content = {
            "TissueClass": tissue,
            "Description": f"Binary mask derived from {tissue} tissue probability map.",
            "SourceImage": source_fname,
            "Derivation": f"Threshold applied at probability > {threshold}",
            "ThresholdLabel": thr_str,
            "ValueType": "binary"
        }

        if dry_run:
            # Dry-run: print what would be written
            print(f"--- DRY-RUN: JSON for {json_path} ---")
            print(json.dumps(json_content, indent=4))
        else:
            # Write JSON to disk
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_content, f, indent=4)
            print(f"JSON file written: {json_path}")

def main():
    parser = argparse.ArgumentParser(description="Correct TPM BM=(CSF+GM+WM)=1 and  for selected sessions.")
    parser.add_argument("--bids_root", required=True,
                        help="Path to the root of the BIDS dataset.")
    parser.add_argument("--sessions", nargs="+", required=True,
                        help="List of session identifiers (e.g., ses-0 ses-1 ses-2 ses-3).")
    parser.add_argument("--template_name", default="BaBa21",
                        help="Template name (default: BaBa21).")
    parser.add_argument("--TPM_suffix",
                        help="Suffix for TPM mask files (if not set, equals desc-average_probseg).")
    parser.add_argument("--template_folder", default="final",
                        help="Folder under template where input images are found and outputs will be saved (default: final).")
    parser.add_argument("--TPM_threshold", type=float, default=0.2,
                        help="Threshold used to binarize the TPM before correction (default: 0.2).")
    parser.add_argument("--pad", action="store_true",
                        help="If set, generate TPM padded.")
    parser.add_argument("--pad_size", type=int, default=25,
                        help="padding size (in pixel for each border) (default: 25).")
    parser.add_argument(
        '--dry-run', action="store_true",
        help="Print commands without executing them"
    )
    args = parser.parse_args()

    TPM_suffix = args.TPM_suffix
    dry_run = args.dry_run

    for ses in args.sessions:

        template_path = os.path.join(
            args.bids_root, "derivatives", "template",
            f"sub-{args.template_name}", ses, args.template_folder)

        mask_files = {
            "CSF": os.path.join(template_path,f"sub-{args.template_name}_{ses}_label-CSF_{TPM_suffix}.nii.gz"),
            "WM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-WM_{TPM_suffix}.nii.gz"),
            "GM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-GM_{TPM_suffix}.nii.gz")
        }

        for key, mask_path in mask_files.items():
            if not os.path.exists(mask_path):
                print(f"ERROR: {key} mask not found: {mask_path}. Skipping session {ses}.")
                continue

        brainmask_files = {
            "BM": os.path.join(template_path,
                               f"sub-{args.template_name}_{ses}_label-BM_{TPM_suffix}.nii.gz")
        }
        cmd = ["fslmaths", f"{mask_files['CSF']}", "-add", f"{mask_files['GM']}", "-add",
               f"{mask_files['WM']}", f"{brainmask_files['BM']}"]
        run_command(cmd, dry_run)

        print(f"threshold TPM ")

        thr_str = f"thr{str(args.TPM_threshold).replace('.', 'p')}"

        mask_files_thr = {
            "CSF": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-CSF_desc-{thr_str}_probseg.nii.gz"),
            "WM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-WM_desc-{thr_str}_probseg.nii.gz"),
            "GM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-GM_desc-{thr_str}_probseg.nii.gz")
        }

        mask_files_corrected = {
            "CSF": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-CSF_desc-corr_probseg.nii.gz"),
            "WM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-WM_desc-corr_probseg.nii.gz"),
            "GM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-GM_desc-corr_probseg.nii.gz")
        }

        cmd = ["fslmaths", f"{mask_files['GM']}", "-thr", f"{args.TPM_threshold}", f"{mask_files_thr['GM']}"]
        run_command(cmd, dry_run)
        cmd = ["fslmaths", f"{mask_files['CSF']}", "-thr", f"{args.TPM_threshold}", f"{mask_files_thr['CSF']}"]
        run_command(cmd, dry_run)
        cmd = ["fslmaths", f"{mask_files['WM']}", "-thr", f"{args.TPM_threshold}", f"{mask_files_thr['WM']}"]
        run_command(cmd, dry_run)

        print(f"compute corrected brainmask")

        brainmask_files_filled = {
            "BM": os.path.join(template_path,
                               f"sub-{args.template_name}_{ses}_label-BM_desc-{thr_str}_mask.nii.gz")
        }

        print(f"generate WM TPM from BM,GM,CSG where WM+CSF+GM=1 in BM ")
        cmd = ["fslmaths", f"{mask_files_thr['CSF']}", "-add",  f"{mask_files_thr['GM']}", "-add",  f"{mask_files_thr['WM']}", "-fillh26", "-bin" , f"{brainmask_files_filled['BM']}"]
        run_command(cmd, dry_run)

        cmd = ["fslmaths", f"{brainmask_files_filled['BM']}", "-sub", f"{mask_files_thr['GM']}", "-sub", f"{mask_files_thr['CSF']}", f"{mask_files_thr['WM']}"]
        run_command(cmd, dry_run)
        cmd = ["fslmaths", f"{mask_files['WM']}", "-mul", f"{brainmask_files_filled['BM']}", f"{mask_files_corrected['WM']}"]
        run_command(cmd, dry_run)
        cmd = ["fslmaths", f"{mask_files['GM']}", "-mul", f"{brainmask_files_filled['BM']}", f"{mask_files_corrected['GM']}"]
        run_command(cmd, dry_run)
        cmd = ["fslmaths", f"{mask_files['CSF']}", "-mul", f"{brainmask_files_filled['BM']}", f"{mask_files_corrected['CSF']}"]
        run_command(cmd, dry_run)

        print(f"threshold TPM ")

        cmd = ["fslmaths", f"{mask_files_corrected['GM']}", "-thr", f"{args.TPM_threshold}", f"{mask_files_thr['GM']}"]
        run_command(cmd, dry_run)
        cmd = ["fslmaths", f"{mask_files_corrected['CSF']}", "-thr", f"{args.TPM_threshold}", f"{mask_files_thr['CSF']}"]
        run_command(cmd, dry_run)
        cmd = ["fslmaths", f"{mask_files_corrected['WM']}", "-thr", f"{args.TPM_threshold}", f"{mask_files_thr['WM']}"]
        run_command(cmd, dry_run)

        write_tpm_json(mask_files_thr, mask_files, args.TPM_threshold, thr_str, dry_run=args.dry_run)

        mask_files_pad = {
            "CSF": os.path.join(template_path,f"sub-{args.template_name}_{ses}_label-CSF_desc-{thr_str}_padded_probseg.nii.gz"),
            "WM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-WM_desc-{thr_str}_padded_probseg.nii.gz"),
            "GM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-GM_desc-{thr_str}_padded_probseg.nii.gz")
        }
        brainmask_files_padded = {
            "BM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-BM_desc-{thr_str}_padded_mask.nii.gz")
        }

        if args.pad:
            cmd = ["ImageMath", "3", f"{mask_files_pad['WM']}", "PadImage", f"{mask_files_thr['WM']}", f"{args.pad_size}"]
            run_command(cmd, dry_run)
            cmd = ["ImageMath", "3", f"{mask_files_pad['GM']}", "PadImage", f"{mask_files_thr['GM']}", f"{args.pad_size}"]
            run_command(cmd, dry_run)
            cmd = ["ImageMath", "3", f"{mask_files_pad['CSF']}", "PadImage", f"{mask_files_thr['CSF']}",f"{args.pad_size}"]
            run_command(cmd, dry_run)
            cmd = ["ImageMath", "3", f"{brainmask_files_padded['BM']}", "PadImage", f"{brainmask_files_filled['BM']}",f"{args.pad_size}"]
            run_command(cmd, dry_run)
        print(f"done")

if __name__ == "__main__":
    main()
