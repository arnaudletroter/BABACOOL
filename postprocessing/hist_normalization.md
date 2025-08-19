## STEP2: Histogram-Based Normalization 

This script performs intensity normalization of T1w or T2w MRI templates across multiple sessions in a BIDS-compliant dataset. 
It uses tissue probability masks (WM, GM, CSF) and percentile-based scaling to normalize contrast, and can optionally generate a cropped version of the normalized image using a brainmask.

### normalize_contrasts.py description
| Option                        | Description                                                                        |
|-------------------------------|------------------------------------------------------------------------------------|
| `--bids_root`                 | Path to the root of the BIDS dataset (required).                                   |
| `--sessions`                  | List of session identifiers (e.g., `ses-0`, `ses-1`, `ses-2`, `ses-3`).            |
| `--modality`                  | Image modality to normalize: `T1w` or `T2w`.                                       |
| `--wm-norm`                   | Target intensity value for white matter after normalization (e.g., 70).            |
| `--gm-norm`                   | Target intensity value for gray matter after normalization (e.g., 30).             |
| `--wm-p`                      | Percentile to estimate white matter intensity from the WM mask (e.g., 90 for T1w). |
| `--gm-p`                      | Percentile to estimate gray matter intensity from the GM mask (e.g., 10 for T1w).  |
| `--template_name`             | Template subject name (default: `BaBa21`).                                         |
| `--template_suffix`           | Template suffix (e.g., `desc-average_padded_debiased`).                            |
| `--TPM_suffix`                | Suffix used for mask files (e.g., `desc-thr0p2_padded_probseg`).                   |
| `--input_template_path`       | Folder under each session where the input template is located (default: `final`).  |
| `--output_template_path`      | Folder under each session where the normalized image is saved (default: `norm`).   |
| `--generate_cropped_template` | Add this flag to generate a cropped version of the normalized image.               |
| `--brainmask_threshold`       | Threshold to binarize the brain mask before cropping (default: `0.5`).             |
| `--QC`                        | generate QC histogram before and after normalization for each tissues              |

Normalize T1w for all sessions
```bash
python postprocessing/normalize_contrasts.py \
  --bids_root BaBa21_openneuro \
  --sessions ses-0 ses-1 ses-2 ses-3 \
  --modality T1w \
  --wm-norm 70 \
  --gm-norm 30 \
  --wm-p 90 \
  --gm-p 10 \
  --template_name BaBa21 \
  --template_suffix desc-average_padded_debiased \
  --TPM_suffix desc-thr0p2_padded \
  --template_path final \
  --generate_cropped_template \
  --brainmask_threshold 0.5 \
  --QC 
```
Normalize T2w for all sessions
```bash
python postprocessing/normalize_contrasts.py \
  --bids_root BaBa21_openneuro \
  --sessions ses-0 ses-1 ses-2 ses-3 \
  --modality T2w \
  --wm-norm 30 \
  --gm-norm 70 \
  --wm-p 10 \
  --gm-p 90 \
  --template_name BaBa21 \
  --template_suffix desc-average_padded_debiased \
  --TPM_suffix desc-thr0p2_padded \
  --template_path final \
  --generate_cropped_template \
  --brainmask_threshold 0.5 \
  --QC 
```
Example output structure
```
BaBa21_openneuro/
└── derivatives/
    └── template/
        └── sub-BaBa21/
            └── ses-2/
                └── final/
                    ├── sub-BaBa21_ses-2_desc-average_padded_debiased_norm_T1w.nii.gz
                    ├── sub-BaBa21_ses-2_desc-average_padded_debiased_norm_T2w.nii.gz
                    ├── sub-BaBa21_ses-2_desc-average_padded_debiased_cropped_norm_T1w.nii.gz
                    ├── sub-BaBa21_ses-2_desc-average_padded_debiased_cropped_norm_T1w.json
                    ├── sub-BaBa21_ses-2_desc-average_padded_debiased_cropped_norm_T2w.nii.gz
                    ├── sub-BaBa21_ses-2_desc-average_padded_debiased_cropped_norm_T2w.json  
                    ├── T1w_ses-2_histogram_after_cor.pdf # QC OPTION
                    ├── T1w_ses-2_histogram_before_cor.pdf # QC OPTION
                    ├── T2w_ses-2_histogram_after_cor.pdf # QC OPTION
                    └── T2w_ses-2_histogram_before_cor.pdf # QC OPTION        

```

[<-- previous STEP](bias_correction.md) [return menu](../pipeline4D.md) [--> next STEP](longitudinal_registration.md)