## STEP4: Post-processing template construction

### _prepare_MM_subjects_list.py_ description

This script generates an input CSV file compatible for `antsMultivariateTemplateConstruction2.sh` from a BIDS dataset.
It extracts paths to warped T1w, T2w volumes (and optionally others modalities) for each subject and session

The output CSV is headerless and formatted to be used directly with antsMultivariateTemplateConstruction2.sh.

| Option               | Description                                                                   |
|----------------------|-------------------------------------------------------------------------------|
| `-i`, `--input-csv`  | Input CSV with 'subject' and 'session' columns (required).                    |
| `--deriv-subdir`     | Subdirectory under derivatives where volumes are browsed (default: warped)    |
| `--modalities`       | List of modalities to look for (e.g., T1w T2w label-WM_mask)                  |
| `--pattern`          | List of desc patterns to include (e.g., flipped warped)                       |
| `-b`, `--bids-root`  | Path to the root of the BIDS dataset (required for mask search).              |
| `-o`, `--output-csv` | Output CSV file (compatible for `antsMultivariateTemplateConstruction2.sh` )  |

_for timepoint 3_
```bash
python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-3.csv \
 --modalities T1w T2w -b BaBa21_openneuro \
 --pattern warped flipped \
 --deriv-subdir warped_HR -o list_of_subjects/subjects_ses-3_warp_HR_for_MM_template.csv
```
_for timepoint 2_
```bash
python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-2.csv \
 --modalities T1w T2w -b BaBa21_openneuro \
 --pattern warped flipped \
 --deriv-subdir warped_HR -o list_of_subjects/subjects_ses-2_warp_HR_for_MM_template.csv
```
_for timepoint 1_
```bash
python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-1.csv \
 --modalities T1w T2w -b BaBa21_openneuro \
 --pattern warped flipped \
 --deriv-subdir warped_HR -o list_of_subjects/subjects_ses-1_warp_HR_for_MM_template.csv
```
_for timepoint 0_
```bash
python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-0.csv \
 --modalities T1w T2w label-WM_mask  -b BaBa21_openneuro \
 --pattern warped flipped \
 --deriv-subdir warped_HR -o list_of_subjects/subjects_ses-0_warp_HR_for_MM_template.csv
```

### _MM_template_construction.py_ description
This python wrapper runs a 2-stage multivariate template construction pipeline calling _antsMultivariateTemplateConstruction2.sh_, while enforcing as output a BIDS-compatible derivatives structure.

| Option              | Description                                                  |
| ------------------- |--------------------------------------------------------------|
| `-h`, `--help`      | Show this help message and exit                              |
| `-s`, `--subject`   | Subject label (e.g. BaBa21)                                  |
| `-S`, `--session`   | Session label (e.g. ses-0)                                   |
| `--input-list`      | CSV file with list of input NIfTI images for both stages     |
| `-b`, `--bids-root` | BIDS root folder                                             |
| `-j`, `--jobs`      | Number of CPU cores to use (default: 12)                     |
| `--modalities`      | List of modalities to look for (e.g., T1w T2w label-WM_mask) |
| `--ite1`            | Number of iterations for Stage 1 (default: 1)                |
| `--q1`              | Steps for Stage 1 `-q` option (default: 50x30x15)            |
| `--w1`              | Weights for Stage 1 modalities (default: 0.5x0.5x1)          |
| `--ite2`            | Number of iterations for Stage 2 (default: 1)                |
| `--q2`              | Steps for Stage 2 `-q` option (default: 70x50x30)            |
| `--w2`              | Weights for Stage 2 modalities (default: 1x1x1)              |

_for timepoint 3_
```bash
python postprocessing/MM_template_construction.py \
--subject BaBa21 \
--session ses-3 \
--modalities T1w T2w \ 
--input-list list_of_subjects/subjects_ses-3_warp_for_MM_template.csv \
-b BaBa21_openneuro -j 6 --ite1 4 --q1 30x20x10 --w1 1x1 --ite2 4 --q2 50x30x15 --w2 1x1
```

_for timepoint 2_
```bash
python postprocessing/MM_template_construction.py \
--subject BaBa21 \
--session ses-2 \
--modalities T1w T2w \ 
--input-list list_of_subjects/subjects_ses-2_warp_for_MM_template.csv \
-b BaBa21_openneuro -j 6 --ite1 4 --q1 30x20x10 --w1 1x1 --ite2 4 --q2 50x30x15 --w2 1x1
```

_for timepoint 1_
```bash
python postprocessing/MM_template_construction.py \
--subject BaBa21 \
--session ses-1 \
--modalities T1w T2w \ 
--input-list list_of_subjects/subjects_ses-1_warp_for_MM_template.csv \
-b BaBa21_openneuro -j 6 --ite1 4 --q1 30x20x10 --w1 1x1 --ite2 4 --q2 50x30x15 --w2 1x1
```

_for timepoint 0_
```bash
python postprocessing/MM_template_construction.py \
--subject BaBa21 \
--session ses-0 \
--modalities T1w T2w label-WM_mask \ 
--input-list list_of_subjects/subjects_ses-0_warp_for_MM_template.csv \
-b BaBa21_openneuro -j 6 --ite1 4 --q1 30x20x10 --w1 0.5x0.5x1 --ite2 4 --q2 50x30x15 --w2 1x1x1
```

Example output structure for two successive timepoints
```bash
derivatives/
└── template/
    └── sub-BaBa21/
        └── ses-0/
            ├── tmp_LR/
            ├── tmp_HR/
            └── final/
                ├── sub-BaBa21_ses-0_desc-sharpen_T1w.nii.gz
                ├── sub-BaBa21_ses-0_desc-sharpen_T2w.nii.gz
                └── sub-BaBa21_ses-0_desc-sharpen_label-WM_probseg.nii.gz
        └── ses-1/
            ├── tmp_LR/
            ├── tmp_HR/
            └── final/
                ├── sub-BaBa21_ses-1_desc-sharpen_T1w.nii.gz
                └── sub-BaBa21_ses-1_desc-sharpen_T2w.nii.gz
```

[<-- previous STEP](../preprocessing/denoise_realign.md) [return menu](../pipeline3D.md) [--> next STEP](generate_TPM.md)