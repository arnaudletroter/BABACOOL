## STEP5: Post-processing Tissue probability maps generation

### _generate_TPM.py_ description

this script generates Tissue probability maps to template space

| Option                   | Description                                                                                   |
|--------------------------|-----------------------------------------------------------------------------------------------|
| `-h`, `--help`           | Show this help message and exit                                                               |
| `--bids_root`            | Root directory of BIDS dataset (required)                                                     |
| `--subjects_csv`         | CSV file with columns 'subject' and 'session' (required)                                      |
| `--template_name`        | Template name (e.g. BaBa21) (required)                                                        |
| `--template_session`     | Template session (e.g. ses-0) (required)                                                      |
| `--reference_suffix`     | reference suffix volume For warping input images (e.g. desc-symmetric-sharpen_T1w) (required) |
| `--patterns`             | List of patterns to try for transform filenames (e.g. warped flipped) (required)              |
| `--output_derivatives`   | Output derivatives directory, default: bids_root/derivatives                                  |
| `--input_folder`         | folder where input are founded (default: bids_root)"                                          |
| `--output_folder`        | folder under derivatives where masks are saved (default: warped)"                             |
| `--modalities`           | List of modalities/masks to warp (e.g. label-WM_mask label-GM_mask brain_mask) (required)     |
| `--map_type`             | type of map, bids compatible (e.g. probseg for TPM or mean for contrasts)"                    |
| `--dry-run`              | Print commands without executing them                                                         |
| `--threads`              | Number of threads for ITK/ANTs (default: 12)                                                  |

_for timepoint 3_

 # generate symmetric TPM WM GM CSF BM 

```bash
  python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro  \
  --subjects_csv list_of_subjects/subjects_ses-3.csv \
  --template_name BaBa21 \
  --template_session ses-3 \
  --reference_suffix desc-symmetric-sharpen_T1w \
  --patterns warped flipped\
  --input_folder derivatives/segmentation \
  --output_folder warped \
  --modalities label-WM_mask label-GM_mask label-CSF_mask desc-brain_mask \
  --map_type probseg
```

Example output structure
```
BaBa21_openneuro/
└── derivatives/
    └── template/
        └── sub-BaBa21/
            └── ses-3/
                ├── final/
                │   ├── sub-BaBa21_ses-3_desc-symmetric_label-WM_mask_probseg.nii.gz
                │   ├── sub-BaBa21_ses-3_desc-symmetric_label-GM_mask_probseg.nii.gz
                │   ├── sub-BaBa21_ses-3_desc-symmetric_label-CSF_mask_probseg.nii.gz
                │   └── sub-BaBa21_ses-3_desc-symmetric_desc-brain_mask_probseg.nii.gz
```
# regenerate symmetric T1w T2w templates (without sharpen) on a padded template (add 25 pixels on each border for example to enlarge FOV)
```bash

ImageMath 3 BaBa21_openneuro/derivatives/template/sub-BaBa21/ses-3/final/sub-BaBa21_ses-3_desc-symmetric-sharpen_desc-padded_T1w.nii.gz \
PadImage BaBa21_openneuro/derivatives/template/sub-BaBa21/ses-3/final/sub-BaBa21_ses-3_desc-symmetric-sharpen_T1w.nii.gz 25

python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro  \
  --subjects_csv list_of_subjects/subjects_ses-3.csv \
  --template_name BaBa21 \
  --template_session ses-3 \
  --reference_suffix desc-symmetric-sharpen_desc-padded_T1w \
  --patterns warped flipped \
  --output_folder warped \
  --modalities T1w T2w  \
  --map_type desc-padded_mean
 ```

Example output structure
```
BaBa21_openneuro/
└── derivatives/
    └── template/
        └── sub-BaBa21/
            └── ses-3/
                ├── final/
                │   ├── sub-BaBa21_ses-3_desc-symmetric_T1w_desc-padded_mean.nii.gz
                │   └── sub-BaBa21_ses-3_desc-symmetric_T2w_desc-padded_mean.nii.gz
```


# generate asymmetric average T2w template (without sharpen)
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro  \
  --subjects_csv list_of_subjects/subjects_ses-3.csv \
  --template_name BaBa21 \
  --template_session ses-3 \
  --reference_suffix desc-symmetric-sharpen_T1w \
  --patterns warped \
  --output_folder warped \
  --modalities T2w \
  --map_type desc-asym_mean
```





[<-- previous STEP](template_construction.md) [return menu](../pipeline3D.md) [--> next STEP](../pipeline4D.md)