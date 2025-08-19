## STEP5: Post-processing Tissue probability maps generation

### _generate_TPM.py_ description

this script generates Tissue probability maps to template space

| Option                   | Description                                                                             |
|--------------------------|-----------------------------------------------------------------------------------------|
| `-h`, `--help`           | Show this help message and exit                                                         |
| `--bids_root`            | Root directory of BIDS dataset (required)                                               |
| `--subjects_csv`         | CSV file with columns 'subject' and 'session' (required)                                |
| `--template_name`        | Template name (e.g. BaBa21) (required)                                                  |
| `--template_session`     | Template session (e.g. ses-0) (required)                                                |
| `--reference_suffix`     | Reference suffix volume for warping input images (default: desc-sharpen\_T1w)           |
| `--patterns`             | List of patterns selected for merging (e.g. warped flipped) (required)                  |
| `--input_folder`         | Folder where input images are located (default: bids\_root)                             |
| `--output_tmp_folder`    | Folder under derivatives where warped volumes are saved (default: warped)               |
| `--template_folder`      | Folder under template where final template images are located (default: final)          |
| `--modalities`           | List of modalities/masks to warp (e.g. label-WM label-GM if mask or T1w if contrast)    |
| `--map_type`             | Type of map, BIDS-compatible (e.g. mask for TPM or contrast for other maps like T1w)    |
| `--bids_description`     | Optional list of BIDS descriptions to include in output filenames (e.g. average padded) |
| `--dry-run`              | Print commands without executing them                                                   |
                                                         |

**Generate symmetric TPM WM GM CSF** 
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
**Regenerate symmetric T1w T2w templates (without sharpen) on a padded template largest (for example add 25 pixels on each border to enlarge FOV)**
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
  --output_tmp_folder warped_HR \
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

**Generate asymmetric average padded T1w/T2w template (without sharpen)**
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro \
  --subjects_csv list_of_subjects/subjects_ses-3.csv \
  --template_name BaBa21 \
  --template_session ses-3 \
  --reference_suffix desc-sharpen_padded_T1w \
  --patterns warped \
  --template_folder final \
  --output_tmp_folder warped_HR \
  --modalities T1w T2w \
  --map_type contrast \
  --bids_description average asym padded
```
**Generate symmetric TPM WM GM CSF**

_for timepoint 2_
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro \
  --subjects_csv list_of_subjects/subjects_ses-2.csv \
  --template_name BaBa21 \
  --template_session ses-2 \
  --reference_suffix desc-sharpen_T1w \
  --patterns warped flipped \
  --template_folder final \
  --input_folder derivatives/segmentation \
  --output_tmp_folder warped_HR \
  --modalities label-WM label-GM label-CSF  \
  --map_type mask \
  --bids_description average probseg
```
_for timepoint 1_
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro \
  --subjects_csv list_of_subjects/subjects_ses-1.csv \
  --template_name BaBa21 \
  --template_session ses-1 \
  --reference_suffix desc-sharpen_T1w \
  --patterns warped flipped \
  --template_folder final \
  --input_folder derivatives/segmentation \
  --output_tmp_folder warped_HR \
  --modalities label-WM label-GM label-CSF  \
  --map_type mask \
  --bids_description average probseg
```
_for timepoint 0_
```bash
python postprocessing/generate_TPM.py \
  --bids_root BaBa21_openneuro \
  --subjects_csv list_of_subjects/subjects_ses-0.csv \
  --template_name BaBa21 \
  --template_session ses-0 \
  --reference_suffix desc-sharpen_T1w \
  --patterns warped flipped \
  --template_folder final \
  --input_folder derivatives/segmentation \
  --output_tmp_folder warped_HR \
  --modalities label-WM label-GM label-CSF  \
  --map_type mask \
  --bids_description average probseg
```

**Generate _for all timepoints_ the corrected TPM where WM=1-(GM+CSF) with GM,CSF>thr and BM=sum(GM,WM,CSF)>thr)**
```bash
python postprocessing/correct_TPM.py \
  --bids_root BaBa21_openneuro \
  --template_name BaBa21 \
  --session ses-0 ses-1 ses-2 ses-3\
  --TPM_suffix desc-average_probseg \
  --template_folder final \
  --TPM_threshold 0.2
```
Example output structure
```
BaBa21_openneuro/
└── derivatives/
    └── template/
        └── sub-BaBa21/
            └── ses-2/
                ├── final/
                │   ├── sub-BaBa21_ses-2_label-BM_desc-average_probseg.nii.gz
                │   ├── sub-BaBa21_ses-2_label-WM_desc-average_probseg.nii.gz
                │   ├── sub-BaBa21_ses-2_label-GM_desc-average_probseg.nii.gz
                │   ├── sub-BaBa21_ses-2_label-CSF_desc-average_probseg.nii.gz   
                │   ├── sub-BaBa21_ses-2_label-BM_desc-thr0p2_mask.nii.gz
                │   ├── sub-BaBa21_ses-2_label-WM_desc-thr0p2_probseg.nii.gz
                │   ├── sub-BaBa21_ses-2_label-GM_desc-thr0p2_probseg.nii.gz
                │   ├── sub-BaBa21_ses-2_label-CSF_desc-thr0p2_probseg.nii.gz
                │   ├── sub-BaBa21_ses-2_label-WM_desc-thr0p2_probseg.json
                │   ├── sub-BaBa21_ses-2_label-GM_desc-thr0p2_probseg.json
                │   └── sub-BaBa21_ses-2_label-CSF_desc-thr0p2_probseg.json
```


<table>

<tr> 
    <td align="center">TPM WM (average) </td> 
    <td align="center">TPM WM corrected (average thresholded)</td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_WM_average.png" width="400" height="150" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_WM_thr0p2.png" width="400" height="150" />
    </td>
</tr>
<tr> 
    <td align="center">TPM GM (average) </td> 
    <td align="center">TPM GM corrected (average thresholded)</td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_GM_average.png" width="400" height="150" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_GM_thr0p2.png" width="400" height="150" />
    </td>
</tr>
<tr> 
    <td align="center">TPM CSF (average) </td> 
    <td align="center">TPM CSF corrected (average thresholded)</td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_CSF_average.png" width="400" height="150" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_CSF_thr0p2.png" width="400" height="150" />
    </td>
</tr>
<tr> 
    <td align="center">TPM BM (average) </td> 
    <td align="center">TPM BM corrected (average thresholded)</td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_BM_average.png" width="400" height="150" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-2_BM_thr0p2.png" width="400" height="150" />
    </td>
</tr>
</table>

[<-- previous STEP](template_construction.md) [return menu](../pipeline3D.md) [--> next STEP](../pipeline4D.md)