## STEP1: B1 Bias correction

### bias_correction.py description

This script performs bias field correction on multiple sessions

| Option                | Description                                                                        |
| --------------------- |------------------------------------------------------------------------------------|
| `--bids_root`         | Path to the root of the BIDS dataset (required).                                   |
| `--sessions`          | List of session identifiers to process (e.g., `ses-0`, `ses-1`, `ses-2`, `ses-3`). |
| `--template_name`     | Template name used in filenames (default: `BaBa21`).                               |
| `--template_type`     | Template type used in filenames (default: `desc-sharpen`).                         |
| `--brain_mask_suffix` | Suffix for the brain mask filename (e.g., `label-BM_desc-thr0p2_mask`). Optional.         |
| `--k`                 | Flag to keep temporary files (adds the `-k` option to the processing command).     |
| `--s_value`           | size of gauss kernel in mm when performing mean filtering (default is 2)           |

_for all timepoints_
```bash
python postprocessing/bias_correction.py  --bids_root BaBa21_openneuro --sessions ses-0 ses-1 ses-2 ses-3
```

_for timepoint2 using padded templates_
```bash
# if needed pad binary brainmask (faster), to force that T1w, T2w and mask to have the same dimensions (else regenerate TPM using padded T1w as target)
mri_convert -i BaBa21_openneuro/derivatives/template/sub-BaBa21/ses-2/final/sub-BaBa21_ses-2_label-BM_desc-thr0p2_mask.nii.gz -o BaBa21_openneuro/derivatives/template/sub-BaBa21/ses-2/final/sub-BaBa21_ses-2_label-BM_desc-thr0p2_padded_mask.nii.gz -rl BaBa21_openneuro/derivatives/template/sub-BaBa21/ses-2/final/sub-BaBa21_ses-2_desc-average_padded_T1w.nii.gz 

python postprocessing/bias_correction.py  --bids_root BaBa21_openneuro --template_type desc-average_padded --brain_mask_suffix label-BM_desc-thr0p2_padded_mask --sessions ses-2
```

Example output structure
```
└── sub-BaBa21
    ├── ses-0
    │   └── final
    │       ├── sub-BaBa21_ses-0_desc-sharpen_debiased_cropped_T1w.nii.gz
    │       ├── sub-BaBa21_ses-0_desc-sharpen_debiased_cropped_T2w.nii.gz
    │       ├── sub-BaBa21_ses-0_desc-sharpen_debiased_T1w.nii.gz
    │       ├── sub-BaBa21_ses-0_desc-sharpen_debiased_T2w.nii.gz
    ├── ses-1
    │   └── final
    │       ├── sub-BaBa21_ses-1_desc-sharpen_debiased_cropped_T1w.nii.gz
    │       ├── sub-BaBa21_ses-1_desc-sharpen_debiased_cropped_T2w.nii.gz
    │       ├── sub-BaBa21_ses-1_desc-sharpen_debiased_T1w.nii.gz
    │       ├── sub-BaBa21_ses-1_desc-sharpen_debiased_T2w.nii.gz
    ├── ses-2
    │   └── final
    │       ├── sub-BaBa21_ses-2_desc-sharpen_debiased_cropped_T1w.nii.gz
    │       ├── sub-BaBa21_ses-2_desc-sharpen_debiased_cropped_T2w.nii.gz
    │       ├── sub-BaBa21_ses-2_desc-sharpen_debiased_T1w.nii.gz
    │       ├── sub-BaBa21_ses-2_desc-sharpen_debiased_T2w.nii.gz
    ├── ses-3
    │    └── final
    │       ├── sub-BaBa21_ses-3_desc-sharpen_debiased_cropped_T1w.nii.gz
    │       ├── sub-BaBa21_ses-3_desc-sharpen_debiased_cropped_T2w.nii.gz
    │       ├── sub-BaBa21_ses-3_desc-sharpen_debiased_T1w.nii.gz
    │       └── sub-BaBa21_ses-3_desc-sharpen_debiased_T2w.nii.gz
```
<table>

<tr> 
    <td align="center">T1w (before correction) </td> 
    <td align="center">T2w (before correction) </td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_padded_T1w.png" width="400" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_padded_T2w.png" width="400" />
    </td>
</tr>
<tr> 
    <td align="center">T1w (after correction) </td> 
    <td align="center">T2w (after correction) </td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_padded_debiased_cropped_T1w.png" width="400" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_padded_debiased_cropped_T2w.png" width="400" />
    </td>
</tr>
</table>

[return menu](../pipeline4D.md) [--> next STEP](../postprocessing/hist_normalization.md)