import os
import argparse
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import json

def save_histogram(data, gm_mask, wm_mask, bm_mask, modality, session, output_dir,suffix,min,max,bin):
    plt.figure(figsize=(8,4))
    bins = np.linspace(min, max, bin)
    plt.hist(data[bm_mask > 0.5], bins=bins, alpha=0.2, label='Brain Mask')
    plt.hist(data[wm_mask > 0.5], bins=bins, alpha=0.5, label='WM')
    plt.hist(data[gm_mask > 0.5], bins=bins, alpha=0.5, label='GM')
    plt.title(f"{modality} histogram for session {session}")
    plt.legend()
    plt.tight_layout()
    filename = os.path.join(output_dir, f"{modality}_{session}_histogram_{suffix}.pdf")
    plt.savefig(filename)

    print(f"{filename} saved")
    plt.close()

def write_anat_json(modality, source_fname, filepath, a, b):
    """
    Write a BIDS-compliant JSON sidecar for each thresholded TPM, with dry-run option.
    """
    json_path = filepath.replace(".nii.gz", ".json")

    # Build JSON content
    json_content = {
        "Modality": "MR",
        "PulseSequenceType": modality,
        "Description": f"{modality} anatomical image after affine normalization, contrast normalization, and cropping.",
        "SourceImage": f"{source_fname}",
        "Derivation": [
            "Rigid+Affine+SyN transformation applied for spatial normalization.",
            "Intensity histogram matched for contrast normalization.",
            "Image cropped using brainmask"
        ],
        "SpatialNormalization": {
            "Type": "Rigid+Affine+SyN",
            "Reference": "Haiko Template"
        },
        "IntensityNormalization": {
            "Method": "Histogram matching",
            "Details": f"normalized_value = a * original_value + b where a = {a:.4f}, b = {b:.4f} "
        },
        "Cropping": {
            "Method": "multiplication by binary brainmask",
            "Details": "Cropping applied to remove background outside brain"
        },
        "ValueType": "intensity"
    }

    # Write JSON to disk
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_content, f, indent=4)
    print(f"JSON file written: {json_path}")


def main():
    parser = argparse.ArgumentParser(description="Normalize contrast for selected sessions.")
    parser.add_argument("--bids_root", required=True,
                        help="Path to the root of the BIDS dataset.")
    parser.add_argument("--sessions", nargs="+", required=True,
                        help="List of session identifiers (e.g., ses-0 ses-1 ses-2 ses-3).")
    parser.add_argument("--modality", choices=["T1w", "T2w"], required=True,
                        help="Contrast modality to normalize.")
    parser.add_argument("--wm-norm", type=float, required=True,
                        help="Target value for white matter.")
    parser.add_argument("--gm-norm", type=float, required=True,
                        help="Target value for gray matter.")
    parser.add_argument("--wm-p", type=int, required=True,
                        help="Percentile used for WM (e.g., 90 for T1w, 10 for T2w).")
    parser.add_argument("--gm-p", type=int, required=True,
                        help="Percentile used for GM (e.g., 10 for T1w, 90 for T2w).")
    parser.add_argument("--template_name", default="BaBa21",
                        help="Template name (default: BaBa21).")
    parser.add_argument("--template_suffix", default="desc-average_padded_debiased",
                        help="Template suffix for input template (e.g., desc-average_padded_debiased).")
    parser.add_argument("--TPM_suffix",
                        help="Suffix for TPM mask files (if not set, equals template_suffix).")
    parser.add_argument("--template_path", default="final",
                        help="Folder under template where input images are found and outputs will be saved (default: final).")
    parser.add_argument("--generate_cropped_template", action="store_true",
                        help="If set, generate cropped (masked) version of the normalized image.")
    parser.add_argument("--brainmask_threshold", type=float, default=0.5,
                        help="Threshold used to binarize the brainmask before cropping (default: 0.5).")
    parser.add_argument("--QC", action="store_true",
                        help="If set, generate QC histogram for the normalized images.")
    args = parser.parse_args()

    if args.TPM_suffix is None:
        TPM_suffix = args.template_suffix
    else:
        TPM_suffix = args.TPM_suffix

    for ses in args.sessions:
        template_path = os.path.join(args.bids_root, "derivatives", "template",
                                  f"sub-{args.template_name}", ses, args.template_path)

        img_in = os.path.join(template_path,
                              f"sub-{args.template_name}_{ses}_{args.template_suffix}_{args.modality}.nii.gz")

        if not os.path.exists(img_in):
            print(f"ERROR: Input image not found: {img_in}. Skipping session {ses}.")
            continue

        mask_files = {
            "WM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-WM_{TPM_suffix}_probseg.nii.gz"),
            "GM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-GM_{TPM_suffix}_probseg.nii.gz"),
            "CSF": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-CSF_{TPM_suffix}_probseg.nii.gz"),
            "BM": os.path.join(template_path, f"sub-{args.template_name}_{ses}_label-BM_{TPM_suffix}_mask.nii.gz")
        }

        for key, mask_path in mask_files.items():
            if not os.path.exists(mask_path):
                print(f"ERROR: {key} mask not found: {mask_path}. Skipping session {ses}.")
                continue

        print(f"Compute {args.modality} Normalization for {ses} session")

        # Get percentiles from fslstats
        mean_wm = float(os.popen(f"fslstats {img_in} -k {mask_files['WM']} -p {args.wm_p}").read())
        mean_gm = float(os.popen(f"fslstats {img_in} -k {mask_files['GM']} -p {args.gm_p}").read())

        a = (args.gm_norm - args.wm_norm) / (mean_gm - mean_wm)
        b = args.wm_norm - a * mean_wm

        print(f"Normalization linear transform: a = {a:.4f}, b = {b:.4f}")
        print(f"Equation: normalized_value = a * original_value + b")

        img_out = os.path.join(template_path,
                               f"sub-{args.template_name}_{ses}_{args.template_suffix}_norm_{args.modality}.nii.gz")

        os.system(f"fslmaths {img_in} -mul {a} -add {b} {img_out}")

        if args.generate_cropped_template:
            bm_bin = os.path.join(template_path, "tmp_brainmask_bin.nii.gz")
            os.system(f"fslmaths {mask_files['BM']} -thr {args.brainmask_threshold} -bin {bm_bin}")
            img_out_cropped = os.path.join(template_path,
                                           f"sub-{args.template_name}_{ses}_{args.template_suffix}_cropped_norm_{args.modality}.nii.gz")
            os.system(f"fslmaths {img_out} -mul {bm_bin} {img_out_cropped}")

            write_anat_json(args.modality, img_in, img_out_cropped, a, b)

            os.remove(bm_bin)

        if args.QC:
            norm_img_path = img_out
            if args.generate_cropped_template:
                norm_img_path = img_out_cropped

            img = nib.load(norm_img_path)
            data = img.get_fdata()

            gm_data = nib.load(mask_files['GM']).get_fdata()
            wm_data = nib.load(mask_files['WM']).get_fdata()
            bm_data = nib.load(mask_files['BM']).get_fdata()

            save_histogram(data, gm_data, wm_data, bm_data, args.modality, ses, template_path, "after_cor",-10, 110, 120)

            norm_img_path = img_in
            img = nib.load(norm_img_path)
            data = img.get_fdata()

            masked_data = data[bm_data > args.brainmask_threshold]
            min_val = masked_data.min()
            max_val = masked_data.max()

            print(f"Masked image values: min = {min_val:.4f}, max = {max_val:.4f}")

            save_histogram(data, gm_data, wm_data, bm_data, args.modality, ses, template_path, "before_cor",min_val,max_val, 100)

        print(f"done")

if __name__ == "__main__":
    main()
