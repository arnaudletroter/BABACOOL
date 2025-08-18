## STEP5: Post-processing Tissue probability maps generation

### _generate_TPM.py_ description

this script generates Tissue probability maps to template space

| Option                 | Description                                                                                                 |
| ---------------------- |-------------------------------------------------------------------------------------------------------------|
| `-h`, `--help`         | Show this help message and exit                                                                             |
| `--bids_root`          | Root directory of BIDS dataset (required)                                                                   |
| `--subjects_csv`       | CSV file with columns 'subject' and 'session' (required)                                                    |
| `--template_name`      | Template name (e.g. BaBa21) (required)                                                                      |
| `--template_session`   | Template session (e.g. ses-0) (required)                                                                    |
| `--reference_suffix`   | Reference suffix volume for warping input images (e.g. desc-sharpen) (required, default: desc-sharpen\_T1w) |
| `--patterns`           | List of patterns selected for merging (e.g. warped flipped) (required)                                      |
| `--input_folder`       | Folder where input images are located (default: bids\_root)                                                 |
| `--output_tmp_folder`  | Folder under derivatives where warped volumes are saved (default: warped)                                   |
| `--template_folder`    | Folder under template where final template images are located (default: final)                              |
| `--modalities`         | List of modalities/masks to warp (e.g. label-WM label-GM desc-brain if mask or T1w if contrast) (required)  |
| `--map_type`           | Type of map, BIDS-compatible (e.g. mask for TPM or contrast for other maps like T1w)                        |
| `--bids_description`   | Optional list of BIDS descriptions to include in output filenames (e.g. average padded)                     |
| `--dry-run`            | Print commands without executing them                                                                       |
                                                         |

Generate symmetric TPM WM GM CSF 
_for timepoint 3_
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro \
  --subjects_csv list_of_subjects/subjects_ses-3.csv \
  --template_name BaBa21 \
  --template_session ses-3 \
  --reference_suffix desc-sharpen_T1w \
  --patterns warped flipped \
  --template_folder final \
  --input_folder derivatives/segmentation \
  --output_tmp_folder warped_HR \
  --modalities label-WM label-GM label-CSF  \
  --map_type mask \
  --bids_description average probseg
```
Example output structure
```
BaBa21_openneuro/
└── derivatives/
    └── template/
        └── sub-BaBa21/
            └── ses-3/
                ├── final/
                │   ├── sub-BaBa21_ses-3_label-WM_mask_probseg.nii.gz
                │   ├── sub-BaBa21_ses-3_label-GM_desc-average_probseg.nii.gz
                │   ├── sub-BaBa21_ses-3_label-CSF_desc-average_probseg.nii.gz
```
# regenerate symmetric T1w T2w templates (without sharpen) on a padded template largest (for example add 25 pixels on each border to enlarge FOV)
```bash

ImageMath 3 BaBa21_openneuro/derivatives/template/sub-BaBa21/ses-3/final/sub-BaBa21_ses-3_desc-sharpen_padded_T1w.nii.gz \
PadImage BaBa21_openneuro/derivatives/template/sub-BaBa21/ses-3/final/sub-BaBa21_ses-3_desc-sharpen_T1w.nii.gz 25

python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro \
  --subjects_csv list_of_subjects/subjects_ses-3.csv \
  --template_name BaBa21 \
  --template_session ses-3 \
  --reference_suffix desc-sharpen_padded_T1w \
  --patterns warped flipped \
  --template_folder final \
  --output_tmp_folder warped \
  --modalities T1w T2w \
  --map_type contrast \
  --bids_description average padded
 ```

Example output structure
```
BaBa21_openneuro/
└── derivatives/
    └── template/
        └── sub-BaBa21/
            └── ses-3/
                ├── final/
                │   ├── sub-BaBa21_ses-3_desc-average_padded_T1w.nii.gz
                │   └── sub-BaBa21_ses-3_desc-average_padded_T2w.nii.gz
```

# generate asymmetric average padded T2w template (without sharpen)
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro \
  --subjects_csv list_of_subjects/subjects_ses-3.csv \
  --template_name BaBa21 \
  --template_session ses-3 \
  --reference_suffix desc-sharpen_padded_T1w \
  --patterns warped \
  --template_folder final \
  --output_tmp_folder warped \
  --modalities T2w \
  --map_type contrast \
  --bids_description average asym padded
```





[<-- previous STEP](template_construction.md) [return menu](../pipeline3D.md) [--> next STEP](../pipeline4D.md)