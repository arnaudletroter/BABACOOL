## STEP5: Post-processing Tissue probability maps generation

### _generate_TPM.py_ description

this script generates Tissue probability maps to template space

| Option                      | Description                                                                               |
|-----------------------------|-------------------------------------------------------------------------------------------|
| `-h`, `--help`              | Show this help message and exit                                                           |
| `--bids_root`               | Root directory of BIDS dataset (required)                                                 |
| `--subjects_csv`            | CSV file with columns 'subject' and 'session' (required)                                  |
| `--template_name`           | Template name (e.g. BaBa21) (required)                                                    |
| `--template_session`        | Template session (e.g. ses-0) (required)                                                  |
| `--patterns`                | List of patterns to try for transform filenames (e.g. warped flipped) (required)          |
| `--output_derivatives`      | Output derivatives directory, default: bids_root/derivatives                              |
| `--mask_subfolder`          | Subfolder under derivatives where masks are stored (default: warped)                      |
| `--modalities`              | List of modalities/masks to warp (e.g. label-WM_mask label-GM_mask brain_mask) (required) |
| `--dry-run`                 | Print commands without executing them                                                     |
| `--threads`                 | Number of threads for ITK/ANTs (default: 12)                                              |

_for timepoint 0_
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro  \
  --subjects_csv list_of_subjects/subjects_ses-0.csv \
  --template_name BaBa21 \
  --template_session ses-0 \
  --patterns warped flipped \
  --mask_subfolder segmentation \
  --modalities label-WM_mask label-GM_mask label-CSF_mask desc-brain_mask
```

_for timepoint 1_
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro  \
  --subjects_csv list_of_subjects/subjects_ses-1.csv \
  --template_name BaBa21 \
  --template_session ses-1 \
  --patterns warped flipped \
  --mask_subfolder segmentation \
  --modalities label-WM_mask label-GM_mask label-CSF_mask desc-brain_mask
```

_for timepoint 2_
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro  \
  --subjects_csv list_of_subjects/subjects_ses-2.csv \
  --template_name BaBa21 \
  --template_session ses-2 \
  --patterns warped flipped \
  --mask_subfolder segmentation \
  --modalities label-WM_mask label-GM_mask label-CSF_mask desc-brain_mask
```

_for timepoint 3_
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro  \
  --subjects_csv list_of_subjects/subjects_ses-3.csv \
  --template_name BaBa21 \
  --template_session ses-3 \
  --patterns warped flipped \
  --mask_subfolder segmentation \
  --modalities label-WM_mask label-GM_mask label-CSF_mask desc-brain_mask
```

[<-- previous STEP](template_construction.md) [return menu](../pipeline3D.md) [--> next STEP](../pipeline4D.md)