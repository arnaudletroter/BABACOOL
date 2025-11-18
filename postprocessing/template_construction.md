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
 
 python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-3.csv \
 --modalities T1w T2w -b BaBa21_openneuro \
 --pattern warped flipped \
 --deriv-subdir warped -o list_of_subjects/subjects_ses-3_warp_for_MM_template.csv
```
_for timepoint 2_
```bash
python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-2.csv \
 --modalities T1w T2w -b BaBa21_openneuro \
 --pattern warped flipped \
 --deriv-subdir warped_HR -o list_of_subjects/subjects_ses-2_warp_HR_for_MM_template.csv
 
 python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-2.csv \
 --modalities T1w T2w -b BaBa21_openneuro \
 --pattern warped flipped \
 --deriv-subdir warped -o list_of_subjects/subjects_ses-2_warp_for_MM_template.csv
```
_for timepoint 1_
```bash
python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-1.csv \
 --modalities T1w T2w -b BaBa21_openneuro \
 --pattern warped flipped \
 --deriv-subdir warped_HR -o list_of_subjects/subjects_ses-1_warp_HR_for_MM_template.csv
 
 python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-1.csv \
 --modalities T1w T2w -b BaBa21_openneuro \
 --pattern warped flipped \
 --deriv-subdir warped -o list_of_subjects/subjects_ses-1_warp_for_MM_template.csv
```
_for timepoint 0_
```bash
python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-0.csv \
 --modalities T1w T2w label-WM_mask  -b BaBa21_openneuro \
 --pattern warped flipped \
 --deriv-subdir warped_HR -o list_of_subjects/subjects_ses-0_warp_HR_for_MM_template.csv
 
 python preprocessing/prepare_MM_subjects_list.py \
 -i list_of_subjects/subjects_ses-0.csv \
 --modalities T1w T2w label-WM_mask  -b BaBa21_openneuro \
 --pattern warped flipped \
 --deriv-subdir warped -o list_of_subjects/subjects_ses-0_warp_for_MM_template.csv
```

### _MM_template_construction.py_ description

This python wrapper runs a 2-stage multivariate template construction pipeline (LowRes + HighRes) calling _antsMultivariateTemplateConstruction2.sh_, while enforcing as output a BIDS-compatible derivatives structure. 

The template construction was performed in two main stages using the ANTs antsMultivariateTemplateConstruction2.sh script, pooling both T1w and T2w contrasts as inputs (see also Fig. 1):

Stage 1 (Low spatial Resolution)
- T1w and T2w images were downsampled to an isotropic voxel size of (0.6 mm)³
- Cropped to a matrix size of 180³ voxels in Haiko89 space.
four iterations with parameters: shrink factor 4x2x1, smoothing factor 2x1x0, and cross-correlation for pairwise registration.
- Maximum iterations were set to 30x20x10.
- Laplacian sharpening (Xin Wang, 2007) was applied to the T1w and T2w templates at each iteration.
- The output of the last iteration was interpolated to 0.4 mm isotropic resolution, serving as target for Stage 2.
Stage 2  (High spatial Resolution)
- The preprocessed T1w and T2w images were resampled to an isotropic voxel size of (0.4 mm)³ 
- Cropped to a matrix size of 270³ voxels in Haiko89 space.
- two iterations shrink factor 4x2x1, smoothing factor 2x1x0, and cross-correlation for pairwise registration
- Maximum iterations were set to 70x50x30.
- Laplacian sharpening was applied at each iteration.


| Option              | Description                                                                |
|---------------------|----------------------------------------------------------------------------|
| **General**         |                                                                            |
| `-s`, `--subject`   | Subject label (e.g. `BaBa21`) (required).                                  |
| `-S`, `--session`   | Session label (e.g. `ses-0`) (required).                                   |
| `-b`, `--bids-root` | BIDS root folder (required).                                               |
| `-j`, `--jobs`      | Number of CPU cores to use (default: `12`).                                |
| `--modalities`      | List of modalities to look for (e.g., `T1w T2w label-WM_mask`) (required). |
| `--dry-run`         | Print commands without executing them.                                     |
|                     |                                                                            |
| **Stage 1 (LR)**    |                                                                            |
| `--input-list1`     | CSV file with list of input NIfTI images for first stage (required).       |
| `--LR-reg-metrics`  | Type of similarity metric used for pairwise registration (default: `MI`).  |
| `--ite1`            | Number of iterations for Stage 1 (default: `4`).                           |
| `--q1`              | Steps for Stage 1 `-q` option (default: `50x30x15`).                       |
| `--w1`              | Weights for Stage 1 modalities (default: `0.5x0.5x1`).                     |
|                     |                                                                            |
| **Stage 2 (HR)**    |                                                                            |
| `--input-list2`     | CSV file with list of input NIfTI images for second stage (required).      |
| `--HR-reg-metrics`  | Type of similarity metric used for pairwise registration (default: `CC`).  |
| `--ite2`            | Number of iterations for Stage 2 (default: `2`).                           |
| `--q2`              | Steps for Stage 2 `-q` option (default: `70x50x30`).                       |
| `--w2`              | Weights for Stage 2 modalities (default: `1x1x1`).                         |
| `--res-HR`          | Pixel resolution in mm (default: `0.4`).                                   |

_for timepoint 3_
```bash
python postprocessing/MM_template_construction.py \
-b BaBa21_openneuro -j 6 \
--subject BaBa21 \
--session ses-3 \
--modalities T1w T2w \
--input-list-LR list_of_subjects/subjects_ses-3_warp_for_MM_template.csv \
 --ite1 4 --q1 30x20x10 --w1 1x1 \
--input-list-HR list_of_subjects/subjects_ses-3_warp_HR_for_MM_template.csv \
--ite2 2 --q2 70x50x30 --w2 1x1 --res-HR 0.4 --dry-run
```

_for timepoint 2_
```bash
python postprocessing/MM_template_construction.py \
-b BaBa21_openneuro -j 6 \
--subject BaBa21 \
--session ses-2 \
--modalities T1w T2w \
--input-list-LR list_of_subjects/subjects_ses-2_warp_for_MM_template.csv \
 --ite1 4 --q1 30x20x10 --w1 1x1 \
--input-list-HR list_of_subjects/subjects_ses-2_warp_HR_for_MM_template.csv \
--ite2 2 --q2 70x50x30 --w2 1x1 --res-HR 0.4 --dry-run
```

_for timepoint 1_
```bash
python postprocessing/MM_template_construction.py \
-b BaBa21_openneuro -j 6 \
--subject BaBa21 \
--session ses-1 \
--modalities T1w T2w \
--input-list-LR list_of_subjects/subjects_ses-1_warp_for_MM_template.csv \
 --ite1 4 --q1 30x20x10 --w1 1x1 \
--input-list-HR list_of_subjects/subjects_ses-1_warp_HR_for_MM_template.csv \
--ite2 2 --q2 70x50x30 --w2 1x1 --res-HR 0.4 --dry-run
```

_for timepoint 0_
```bash
python postprocessing/MM_template_construction.py \
-b BaBa21_openneuro -j 6 \
--subject BaBa21 \
--session ses-0 \
--modalities T1w T2w label-WM_mask \
--input-list-LR list_of_subjects/subjects_ses-0_warp_for_MM_template.csv \
 --ite1 4 --q1 30x20x10 --w1 0.5x0.5x1 \
--input-list-HR list_of_subjects/subjects_ses-0_warp_HR_for_MM_template.csv \
--ite2 2 --q2 70x50x30 --w2 1x1x1 --res-HR 0.4 --dry-run
```

Example output structure for two successive timepoints
```bash
derivatives/
└── template/
    └── sub-BaBa21/
        └── ses-0/
            └── tmp_LR/
                ├── SyN_iteration3_MYtemplate0.nii.gz # T1w
                ├── SyN_iteration3_MYtemplate1.nii.gz # T2w
                └── SyN_iteration3_MYtemplate2.nii.gz # label-WM_mask
            └── tmp_HR/
                ├── SyN_iteration1_MYtemplate0.nii.gz # T1w
                ├── SyN_iteration1_MYtemplate1.nii.gz # T2w
                └── SyN_iteration1_MYtemplate2.nii.gz # label-WM_mask
            └── final/
                ├── sub-BaBa21_ses-0_desc-sharpen_T1w.nii.gz
                ├── sub-BaBa21_ses-0_desc-sharpen_T2w.nii.gz
                └── sub-BaBa21_ses-0_desc-sharpen_label-WM_mask.nii.gz
        ...
        └── ses-3/
            └── tmp_LR/
                ├── SyN_iteration3_MYtemplate0.nii.gz # T1w
                └── SyN_iteration3_MYtemplate1.nii.gz # T2w
            └── tmp_HR/
                ├── SyN_iteration1_MYtemplate0.nii.gz # T1w
                └── SyN_iteration1_MYtemplate1.nii.gz # T2w
            └── final/
                ├── sub-BaBa21_ses-1_desc-sharpen_T1w.nii.gz
                └── sub-BaBa21_ses-1_desc-sharpen_T2w.nii.gz
```

[<-- previous STEP](../preprocessing/denoise_realign.md) [return menu](../pipeline3D.md) [--> next STEP](generate_TPM.md)
