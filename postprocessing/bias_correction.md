## STEP1: B1 Bias correction (on template)

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
python postprocessing/bias_correction.py  \
  --bids_root BaBa21_openneuro \
  --sessions ses-0 ses-1 ses-2 ses-3
```

_for timepoint2 using padded templates_
```bash
# if needed pad binary brainmask (faster), to force that T1w, T2w and mask to have the same dimensions (else regenerate TPM using padded T1w as target)
# ImageMath BaBa21_openneuro/derivatives/template/sub-BaBa21/ses-2/final/sub-BaBa21_ses-2_label-BM_desc-thr0p2_padded_mask.nii.gz \
# Padding \
# BaBa21_openneuro/derivatives/template/sub-BaBa21/ses-2/final/sub-BaBa21_ses-2_label-BM_desc-thr0p2_mask.nii.gz \
# 25

python postprocessing/bias_correction.py  \
  --bids_root BaBa21_openneuro \
  --template_type desc-average_padded \
  --brain_mask_suffix label-BM_desc-thr0p2_padded_mask \
  --sessions ses-2
```

Example output structure
```
└── sub-BaBa21
    ├── ses-0
    │   └── final
    │       ├── sub-BaBa21_ses-0_desc-average_padded_debiased_cropped_T1w.nii.gz
    │       ├── sub-BaBa21_ses-0_desc-average_padded_debiased_cropped_T2w.nii.gz
    │       ├── sub-BaBa21_ses-0_desc-average_padded_debiased_T1w.nii.gz
    │       ├── sub-BaBa21_ses-0_desc-average_padded_debiased_T2w.nii.gz
    ├── ses-1
    │   └── final
    │       ├── sub-BaBa21_ses-1_desc-average_padded_debiased_cropped_T1w.nii.gz
    │       ├── sub-BaBa21_ses-1_desc-average_padded_debiased_cropped_T2w.nii.gz
    │       ├── sub-BaBa21_ses-1_desc-average_padded_debiased_T1w.nii.gz
    │       ├── sub-BaBa21_ses-1_desc-average_padded_debiased_T2w.nii.gz
    ├── ses-2
    │   └── final
    │       ├── sub-BaBa21_ses-2_desc-average_padded_debiased_cropped_T1w.nii.gz
    │       ├── sub-BaBa21_ses-2_desc-average_padded_debiased_cropped_T2w.nii.gz
    │       ├── sub-BaBa21_ses-2_desc-average_padded_debiased_T1w.nii.gz
    │       ├── sub-BaBa21_ses-2_desc-average_padded_debiased_T2w.nii.gz
    ├── ses-3
    │    └── final
    │       ├── sub-BaBa21_ses-3_desc-average_padded_debiased_cropped_T1w.nii.gz
    │       ├── sub-BaBa21_ses-3_desc-average_padded_debiased_cropped_T2w.nii.gz
    │       ├── sub-BaBa21_ses-3_desc-average_padded_debiased_T1w.nii.gz
    │       ├── sub-BaBa21_ses-3_desc-average_padded_debiased_T2w.nii.gz
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
    <td align="center">T1w padded (after correction) </td> 
    <td align="center">T2w padded (after correction) </td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_padded_debiased_T1w.png" width="400" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_padded_debiased_T2w.png" width="400" />
    </td>
</tr>
<tr> 
    <td align="center">T1w cropped (after correction) </td> 
    <td align="center">T2w cropped (after correction) </td> 
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

## STEP1b: B1 Bias correction (on subjects)

### bias_correction_HCP_T1wT2w.py description

This script performs bias field correction on multiple subject's sessions saving outputs in BIDS
derivatives folder.

| Option                                     | Description                                                                |
| ------------------------------------------ | -------------------------------------------------------------------------- |
| `-h`, `--help`                             | Show this help message and exit.                                           |
| `-i INPUT_CSV`, `--input-csv INPUT_CSV`    | CSV file (e.g. `subjects_sessions.csv`) with columns `subject`, `session`. |
| `-b BIDS_ROOT`, `--bids-root BIDS_ROOT`    | Path to the root of the BIDS dataset.                                      |
| `-o OUTPUT_CSV`, `--output-csv OUTPUT_CSV` | Path to the CSV file listing output T1w and T2w unbiased images.           |
| `--threads THREADS`                        | Number of threads for ITK/ANTs (default: 12).                              |
| `--brain_mask_suffix BRAIN_MASK_SUFFIX`    | Suffix for the binary brain mask filename (e.g., `desc-brain_mask`).       |
| `--s_value S_VALUE`                        | Size of Gaussian kernel in mm when performing mean filtering (default: 2). |
| `--k`                                      | Keep temporary files (adds the `-k` flag).                                 |
| `--dry-run`                                | Print commands without executing them.                                     |

_for ses-0 timepoints_
```bash
python preprocessing/bias_correction_HCP_T1wT2w.py -i list_of_subjects/subjects_ses-0.csv -b BaBa21_openneuro -o list_of_subjects/subjects_ses-0_unbiased.csv --brain_mask_suffix space-orig_desc-brain_mask 
```
Example output structure
```
BaBa21_openneuro/derivatives/unbiased
└── sub-Prune
    ├── ses-0
    │   └── anat
    │       ├── sub-Prune_ses-0_desc-unbiased_T1w.nii.gz
    │       ├── sub-Prune_ses-0_desc-unbiased_T2w.nii.gz
```
<table>
<tr> 
    <td align="center">sub-Prune ses-0 T1w (before correction) </td> 
    <td align="center">sub-Prune ses-0 T2w (before correction) </td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/sub-Prune_T1w.png" width="400" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/sub-Prune_T2w.png" width="400" />
    </td>
</tr>
<tr> 
    <td align="center">sub-Prune ses-0 T1w (after correction) </td> 
    <td align="center">sub-Prune ses-0 T2w (after correction) </td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/sub-Prune_T1w_debiased.png" width="400" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/sub-Prune_T2w_debiased.png" width="400" />
    </td>
</tr>
<tr> 
    <td align="center">sub-Prune ses-0 T1w cropped (after correction) </td> 
    <td align="center">sub-Prune ses-0 T2w cropped (after correction) </td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/sub-Prune_T1w_crop_debiased.png" width="400" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/sub-Prune_T2w_crop_debiased.png" width="400" />
    </td>
</tr>
</table>

_Command to generate the ses-0 average T1w template from all debiased subjects 
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro \
  --subjects_csv list_of_subjects/subjects_ses-0.csv \
  --template_name BaBa21 \
  --template_session ses-0 \
  --reference_suffix desc-sharpen_T1w \
  --patterns warped flipped \
  --template_folder final \
  --input_folder derivatives/unbiased \
  --output_tmp_folder warped_unbiased_HR \
  --modalities desc-unbiased_T1w \
  --map_type contrast \
  --bids_description average
```

Example output structure
```
└── sub-BaBa21
    ├── ses-0
    │   └── final
    │       ├── sub-BaBa21_ses-0_desc-average_desc-unbiased_T1w.nii.gz

```
<table>

  
[return menu](../pipeline4D.md) [--> next STEP](../postprocessing/hist_normalization.md)
