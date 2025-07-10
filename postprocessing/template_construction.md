## STEP4: Post-processing template construction

### prepare_MM_subjects_list.py.py description

This script generates an input CSV file compatible for `antsMultivariateTemplateConstruction2.sh` from a BIDS dataset.
It extracts paths to warped T1w, T2w volumes (and optionally others modalities) for each subject and session

The output CSV is headerless and formatted to be used directly with antsMultivariateTemplateConstruction2.sh.

| Option                | Description                                                                              |
|-----------------------|------------------------------------------------------------------------------------------|
| `-i`, `--input-csv`   | Input CSV with 'subject' and 'session' columns (required).                               |
| `--deriv-subdir`      | Subdirectory under derivatives to look for files (default: segmentation)                 |
| `--modalities`        | List of modalities to look for (e.g., T1w T2w label-WM_mask)                             |
| `-b`, `--bids-root`   | Path to the root of the BIDS dataset (required for mask search).                         |
| `-o`, `--output-csv`  | Output CSV file (no header - compatible for `antsMultivariateTemplateConstruction2.sh` ) |


```bash
python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-0.csv \
 --modalities T1w T2w label-WM_mask  -b BaBa21_openneuro/ \
 --deriv-subdir warped -o list_of_subjects/subjects_ses-0_warp_for_MM_template.csv
```

```bash
python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-1.csv \
 --modalities T1w T2w -b BaBa21_openneuro/ \
 --deriv-subdir warped -o list_of_subjects/subjects_ses-1_warp_for_MM_template.csv
```

```bash
python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-2.csv \
 --modalities T1w T2w -b BaBa21_openneuro/ \
 --deriv-subdir warped -o list_of_subjects/subjects_ses-2_warp_for_MM_template.csv
```

```bash
python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-3.csv \
 --modalities T1w T2w -b BaBa21_openneuro/ \
 --deriv-subdir warped -o list_of_subjects/subjects_ses-3_warp_for_MM_template.csv
```

### _MM_template_construction.py_ description
This python wrapper runs a 2-stage multivariate template construction pipeline calling _antsMultivariateTemplateConstruction2.sh_, while enforcing as output a BIDS-compatible derivatives structure.

```bash
python postprocessing/MM_template_construction.py \
--subject BaBa21 \
--session ses-0 \
--input-list list_of_subjects/subjects_ses-0_warp_for_MM_template.csv \
-b BaBa21_openneuro -j 12
```

```bash
python postprocessing/MM_template_construction.py \
--subject BaBa21 \
--session ses-1 \
--input-list list_of_subjects/subjects_ses-1_warp_for_MM_template.csv \
-b BaBa21_openneuro -j 12
```

```bash
python postprocessing/MM_template_construction.py \
--subject BaBa21 \
--session ses-2 \
--input-list list_of_subjects/subjects_ses-2_warp_for_MM_template.csv \
-b BaBa21_openneuro -j 12
```

```bash
python postprocessing/MM_template_construction.py \
--subject BaBa21 \
--session ses-3 \
--input-list list_of_subjects/subjects_ses-3_warp_for_MM_template.csv \
-b BaBa21_openneuro -j 12
```

Example output structure
```bash
derivatives/
└── template/
    └── sub-BaBa21/
        └── ses-0/
            ├── tmp_LR/
            ├── tmp_HR/
            ├── final/
            ├── sub-BaBa21_ses-0_desc-symmetric-sharpen_T1w.nii.gz
            ├── sub-BaBa21_ses-0_desc-symmetric-sharpen_T2w.nii.gz
            └── sub-BaBa21_ses-0_desc-symmetric-sharpen_label-WM_probseg.nii.gz
```

[<-- previous STEP](../preprocessing/denoise_realign.md) [return menu](../pipeline3D.md) [--> next STEP](generate_TPM.md)