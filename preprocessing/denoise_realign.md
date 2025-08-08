## STEP3: Pre-processing anatomical volumes (T1w, T2w)

### Denoise (T1w, T2w) 
### _denoise_anat.py_ description
This Python script reads a CSV file listing subject/session pairs, navigates a BIDS dataset structure, and runs ANTs DenoiseImage on T1w and T2w images.
This script writes the denoised images into a derivatives folder within the BIDS dataset, following the BIDS standard for derivatives data.
For each input image found in the original dataset under:
```<dataset_root>/sub-XX/ses-YY/anat/```
the script saves the denoised image in:
```<dataset_root>/derivatives/denoised/sub-XX/ses-YY/anat/```

| Option               | Description                                        |
|----------------------|----------------------------------------------------|
| `-i`, `--input-csv`  | CSV file with `subject,session` columns (required) |
| `-b`, `--bids-root`  | Path to the BIDS dataset root (required)           |
| `-o`, `--output-csv` | CSV file to save paths of denoised outputs         |
| `--threads`          | Number of ITK/ANTs threads (default: 12)           |
| `--dry-run`          | Print commands without executing them              |

```bash
python preprocessing/denoise_anat.py \
  -i list_of_subjects/subjects_ses-0.csv \
  -b BaBa21_openneuro \
  --threads 8 \
  -o list_of_subjects/subjects_ses-0_den.csv
```
### re-orient (T1w, T2w) on Haiko89 T1w template

### Steps for Downloading and Organizing the Haiko89 Dataset
These steps rely on an external MRI template for in vivo baboon brain (the **Haiko89** template collection) in the BaBa21 bids dataset.
- Available at: [https://www.nitrc.org/projects/haiko89/](https://www.nitrc.org/projects/haiko89/)
> Love, S.A., Marie, D., Roth, M., Lacoste, R., Nazarian, B., Bertello, A., Coulon, O., Anton, J.-L., Meguerditchian, A., 2016. The average baboon brain: MRI templates and tissue probability maps from 89 individuals. NeuroImage. doi:10.1016/j.neuroimage.2016.03.018

**Folder structure requirement**  
All files from the Haiko89 package must be kept together in a single directory. For example:
```
Haiko89
├── Haiko89_Asymmetric.Template_n89.nii.gz
├── Haiko89sym_Symmetric.Template_n89.nii.gz
├── TPM_Asymmetric.CSF_Haiko89.nii.gz
├── TPM_Asymmetric.GreyMatter_Haiko89.nii.gz
├── TPM_Asymmetric.WhiteMatter_Haiko89.nii.gz
├── TPM_Symmetric.CSF_Haiko89sym.nii.gz
├── TPM_Symmetric.GreyMatter_Haiko89sym.nii.gz
└── TPM_Symmetric.WhiteMatter_Haiko89sym.nii.gz
```

### Convert Haiko89 Folder to a BIDS Subject
### _convert_haiko_to_bids_derivative.py_ description

This Python script converts the original Haiko89 template files into a BIDS-compliant derivatives structure for a synthetic subject sub-Haiko and session ses-Adult.
The script update the participants.tsv at the BIDS root.

| Option               | Description                                               |
| -------------------- | --------------------------------------------------------- |
| `-i`, `--input`      | Path to the original Haiko89 folder (required)            |
| `-o`, `--output`     | Path to the derivatives/atlas folder (inside derivatives) |

```bash
python preprocessing/convert_haiko_to_bids_derivative.py -i Haiko89 -o BaBa21_openneuro/derivatives/atlas
```

| Original File                               | BIDS-Compliant Filename                                      |
| --------------------------------------------|------------------------------------------------------------- |
| Haiko89_Asymmetric.Template_n89.nii.gz      | sub-Haiko_ses-Adult_desc-asymmetric_T1w.nii.gz               |
| Haiko89sym_Symmetric.Template_n89.nii.gz    | sub-Haiko_ses-Adult_desc-symmetric_T1w.nii.gz                |
| TPM_Asymmetric.CSF_Haiko89.nii.gz           | sub-Haiko_ses-Adult_desc-asymmetric_label-CSF_probseg.nii.gz |
| TPM_Asymmetric.GreyMatter_Haiko89.nii.gz    | sub-Haiko_ses-Adult_desc-asymmetric_label-GM_probseg.nii.gz  |
| TPM_Asymmetric.WhiteMatter_Haiko89.nii.gz   | sub-Haiko_ses-Adult_desc-asymmetric_label-WM_probseg.nii.gz  |
| TPM_Symmetric.CSF_Haiko89sym.nii.gz         | sub-Haiko_ses-Adult_desc-symmetric_label-CSF_probseg.nii.gz  |
| TPM_Symmetric.GreyMatter_Haiko89sym.nii.gz  | sub-Haiko_ses-Adult_desc-symmetric_label-GM_probseg.nii.gz   |
| TPM_Symmetric.WhiteMatter_Haiko89sym.nii.gz | sub-Haiko_ses-Adult_desc-symmetric_label-WM_probseg.nii.gz   |

### Re-align anatomical volumes (T1w, T2w) on Haiko89

This Python script integrates the Haiko89 baboon brain MRI template into a BIDS dataset. It supports:

Rigid registration of subject T1w/T2w images to the Haiko89 space
- Optional padding of the template
- Brainmask generation from TPMs
- Left–right flipping of outputs
- Symmetric/asymmetric template selection
- BIDS-compliant paths and naming

### realign_subjects_2_Haiko89.py description

This script performs rigid registration of individual BIDS dataset subjects’ denoised T1w and T2w anatomical images to the Haiko89 brain template converted to BIDS format.

| Option                | Description                                                                                      |
| --------------------  |--------------------------------------------------------------------------------------------------|
| `--bids_root`         | Path to the root of the BIDS dataset (required).                                                 |
| `--subjects_csv`      | CSV file containing columns `sub` and `ses` listing subjects and sessions to process (required). |
| `--output_derivatives`| Optional path to derivatives directory. Defaults to `{bids_root}/derivatives`.                   |
| `--sym`               | Use symmetric Haiko89 template (default: asymmetric)`.                                           |
| `--padding`           | Flag to generate a padded version of the Haiko89 template image                                  |
| `--resolution`        | pixel resolution in mm (default: 0.6)                                                            |
| `--pad_size`          | Padding size in pixel (default: 50)                                                              |
| `--generate_brainmask`| Flag to generate a brainmask TPM by thresholding the sum of CSF, GM, and WM tissue maps.         |
| `--flipping_LR`       | Flip warped T1w/T2w images Left-Right (default: False)                                           |
| `--session_filter`    | Optional list of sessions (e.g. `ses-1 ses-2`) to limit processing to these sessions only.       |
| `--dry-run`           | Print commands without executing them.                                                           |
| `--threads`           | Number of threads for ITK/ANTs (default: 12)                                                     |

_for timepoint 3_ (Generate a Haiko89 brainmask and padded template only once)
```bash
python preprocessing/realign_subjects_2_Haiko89.py \
  --subjects_csv list_of_subjects/subjects_ses-3.csv \
  --bids_root BaBa21_openneuro \
  --sym \
  --threads 8 \
  --padding \
  --pad_size 5 \
  --generate_brainmask \
  --flipping_LR
```
_for timepoint 2_
```bash
python preprocessing/realign_subjects_2_Haiko89.py \
  --subjects_csv list_of_subjects/subjects_ses-2.csv \
  --bids_root BaBa21_openneuro \
  --sym \
  --threads 8 \
  --flipping_LR
```
_for timepoint 1_
```bash
python preprocessing/realign_subjects_2_Haiko89.py \
  --subjects_csv list_of_subjects/subjects_ses-1.csv \
  --bids_root BaBa21_openneuro \
  --sym \
  --threads 8 \
  --flipping_LR
```
_for timepoint 0_
```bash
python preprocessing/realign_subjects_2_Haiko89.py \
  --subjects_csv list_of_subjects/subjects_ses-0.csv \
  --bids_root BaBa21_openneuro \
  --sym \
  --threads 8 \
  --flipping_LR
```

[<-- previous STEP](bids_exporter.md) [return menu](../pipeline3D.md) [--> next STEP](../postprocessing/template_construction.md)