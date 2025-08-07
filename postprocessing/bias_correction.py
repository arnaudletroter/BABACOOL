import argparse
import subprocess
import os

def main():
    parser = argparse.ArgumentParser(description="Run T1xT2BiasFieldCorrection for selected sessions.")
    parser.add_argument("--bids_root", required=True,
                        help="Path to the root of the BIDS dataset (required).")
    parser.add_argument("--sessions", nargs="+", required=True,
                        help="List of session identifiers (e.g., ses-0 ses-3).")
    parser.add_argument("--template_name", default="BaBa21",
                        help="Template name (used in filenames), default is BaBa21.")
    parser.add_argument("--template_type", default="desc-symmetric-sharpen",
                        help="Template type (e.g., desc-symmetric-sharpen).")
    parser.add_argument("--brain_mask_suffix",
                        help="Suffix for the brain mask filename (e.g., `desc-symmetric_brain_mask_probseg`). Optional.")
    parser.add_argument("--k", action="store_true",
                        help="Will keep temporary files (adds the -k flag).")
    parser.add_argument("--s_value", type=int, default=2,
                        help="size of gauss kernel in mm when performing mean filtering (default=2).")

    args = parser.parse_args()

    for ses in args.sessions:
        path_template = f"{args.bids_root}/derivatives/template/sub-{args.template_name}/{ses}/final"

        t1 = f"{path_template}/sub-{args.template_name}_{ses}_{args.template_type}_T1w.nii.gz"
        t2 = f"{path_template}/sub-{args.template_name}_{ses}_{args.template_type}_T2w.nii.gz"

        if not os.path.exists(t1):
            print(f"Error: T1w file not found for session {ses}: {t1}")
            print(f"Skipping session {ses}.")
            continue
        if not os.path.exists(t2):
            print(f"Error: T2w file not found for session {ses}: {t2}")
            print(f"Skipping session {ses}.")
            continue

        cmd = [
            "postprocessing/T1xT2BiasFieldCorrection.sh",
            "-t1", t1,
            "-t2", t2,
            "-s", str(args.s_value),
            "-os", "_desc-debiased"
        ]

        if args.brain_mask_suffix:
            brain_mask = f"{path_template}/sub-{args.template_name}_{ses}_{args.brain_mask_suffix}.nii.gz"
            if os.path.exists(brain_mask):
                cmd.extend(["-b", brain_mask])
            else:
                print(f"Warning: Brain mask file not found for session {ses}: {brain_mask}")
                print("Skipping -b option for this session.")

        if args.k:
            cmd.append("-k")

        print(f"\nRunning command for {ses}:\n{' '.join(cmd)}\n")
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
