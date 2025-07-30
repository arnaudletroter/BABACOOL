## STEP1: B1 Bias correction

### T1xT2BiasFieldCorrection.sh (using FSL) description
this script generates a bias field corrected template

<table>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-0_beforeBiasCorrection.png" width="400" height="150" />
    </td>
</tr>
<tr> 
    <td align="center">T1w efore Correction</td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-0_afterBiasCorrection.png" width="400" height="150" />
    </td>
</tr>
<tr> 
    <td align="center">T1w After Correction</td> 
</tr>
</table>

### bias_correction.py description

This script performs bias field correction on multiple sessions

| Option                | Description                                                                                    |
| --------------------- |------------------------------------------------------------------------------------------------|
| `--bids_root`         | Path to the root of the BIDS dataset (required).                                               |
| `--sessions`          | List of session identifiers to process (e.g., `ses-0`, `ses-3`).                               |
| `--template_name`     | Template name used in filenames (default: `BaBa21`).                                           |
| `--template_type`     | Template type used in filenames (default: `desc-symmetric-sharpen`).                           |
| `--brain_mask_suffix` | Suffix for the brain mask filename (e.g., `desc-symmetric_desc-brain_mask_probseg`). Optional. |
| `--k`                 | Flag to keep temporary files (adds the `-k` option to the processing command).                 |
| `--s_value`           | size of gauss kernel in mm when performing mean filtering (default is 2)                       |

```bash
python postprocessing/bias_correction.py  --bids_root BaBa21_openneuro --sessions ses-0 ses-3
```
Example output structure
```
└── sub-BaBa21
    ├── ses-0
    │   └── final
    │       ├── sub-BaBa21_ses-0_desc-symmetric_desc-brain_mask_probseg.nii.gz
    │       ├── sub-BaBa21_ses-0_desc-symmetric-sharpen_desc-debiased_T1w.nii.gz
    │       ├── sub-BaBa21_ses-0_desc-symmetric-sharpen_desc-debiased_T2w.nii.gz
    │       ├── sub-BaBa21_ses-0_desc-symmetric-sharpen_T1w.nii.gz
    │       └── sub-BaBa21_ses-0_desc-symmetric-sharpen_T2w.nii.gz
    └── ses-3
        └── final
            ├── sub-BaBa21_ses-3_desc-symmetric_desc-brain_mask_probseg.nii.gz
            ├── sub-BaBa21_ses-3_desc-symmetric-sharpen_desc-debiased_T1w.nii.gz
            ├── sub-BaBa21_ses-3_desc-symmetric-sharpen_desc-debiased_T2w.nii.gz
            ├── sub-BaBa21_ses-3_desc-symmetric-sharpen_T1w.nii.gz
            └── sub-BaBa21_ses-3_desc-symmetric-sharpen_T2w.nii.gz
```

_for all timepoints_
```bash
#!/bin/bash
sessions=("ses-0" "ses-1" "ses-2" "ses-3")
for ses in "${sessions[@]}"; do
    path_template="BaBa21_openneuro/derivatives/template/sub-BaBa21/${ses}/final"
    postprocessing/T1xT2BiasFieldCorrection.sh \
        -t1 ${path_template}/sub-BaBa21_${ses}_desc-symmetric-sharpen_T1w.nii.gz \
        -t2 ${path_template}/sub-BaBa21_${ses}_desc-symmetric-sharpen_T2w.nii.gz \
        -b ${path_template}/sub-BaBa21_${ses}_desc-symmetric_desc-brain_mask_probseg.nii.gz \
        -k -s 2 \
        -os "_desc-debiased"
done
```

or run 

```bash
postprocessing/bias_correction_all_sessions.sh BaBa21_openneuro
```

[return menu](../pipeline4D.md) [--> next STEP](../postprocessing/hist_normalization.md)