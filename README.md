# the BABACOOL project

We present the BABACOOL (BAby Brain Atlas COnstruction for Optimized Labeled segmentation) approach for creating multi-modal developmental atlases, which we used to produce BaBa21, a population-based longitudinal developmental baboon template. BaBa21 consists of structural (T1- and T2-weighted) images and tissue probability maps from a population of 21 baboons (Papio anubis) scanned at 4 timepoints beginning from 2 weeks after birth and continuing to sexual maturity (5 years).
This resource is made available to provide a normalization target for baboon data across the lifespan, and further, facilitate neuroimaging research in baboons, comparative research with humans and nonhuman primate species for which developmental templates are available (e.g., macaques). 

<table>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/T1w_snap.gif" width="400" height="150" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/T2w_snap.gif" width="400" height="150" />
    </td>
</tr>
<tr> 
    <td align="center">T1w</td> 
    <td align="center">T2w</td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/WM_snap.gif" width="400" height="150" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/WM_gii_snap_top.gif" width="150" height="150" />
    </td>
</tr>
<tr> 
    <td align="center">WM priors maps</td> 
    <td align="center">Cortical Surface</td> 
</tr>
  
</table>

# PART1: preprocessing stages -> The pipeline steps for **3D** BaBa21 template construction 

## Requirements

This pipeline is mainly written in `bash` and `python` scripts, and requires [ANTs](https://github.com/ANTsX/ANTs), [FSL](https://fsl.fmrib.ox.ac.uk/fsl/docs/#/)

and python scripts which require
**[NumPy](https://numpy.org/), [SciPy](https://scipy.org/)**

## STEP1: Download the partial subject BIDS dataset from openneuro (ID=ds005424)

This dataset contains 21 subjects (4 sessions), and the resulting template sub-BaBa21, and probabilistic atlas (TPM WM,GM,CSF) . 
The T1w and T2w anatomical volumes and manual segmentations (WM,GM,CSF) of a single subject (sub-Prune) are published without embargo. Other twenty subjects can be retrieved on request from the authors and will be published in a next version.

### You can use git
```bash
$ git clone https://openneuro.org/git/3/ds005424
```
### or datalad
```bash
$ datalad install https://openneuro.org/git/3/ds005424
```

## STEP2: BIDS Session-Age CSV Exporter

This command-line Python script extracts, filters, and exports subject-session-age data from a BIDS dataset.
It helps you generate a CSV listing each subject’s sessions and their recorded ages, with flexible filtering options for easy analysis.

### Features 
- Reads BIDS-compliant dataset structure
  - Extracts session-age info from sub-*_sessions.tsv files
  - Filters by Session name, Age range, Excluded subjects 
  - Exports to CSV
  - Prints summary statistics (number of subjects, mean and standard deviation of age)

### output Dataset org
```bash
├── /path/to/bids/
│   ├── sub-01/
│   │   ├── sub-01_sessions.tsv
│   │   ├── ses-0/
│   │   └── ses-1/
│   ├── sub-02/
│   │   ├── sub-01_sessions.tsv
│   │   ├── ses-0/
│   │   └── ses-1/
│   │...
```
Each sub-*_sessions.tsv file contains, 
for example:\
session_id	age\
ses-0	    35\
ses-1	    274\
ses-2	    764

### _parse_dataset.py_ description
```
| Option                   | Description                                              |
| ------------------------ | -------------------------------------------------------- |
| `-i`, `--input`          | Path to the BIDS root directory (required)               |
| `-o`, `--output`         | Output CSV filename (default: subjects_sessions.csv)     |
| `-f`, `--filter-session` | Include only sessions whose names contain this substring |
| `--age-min`              | Minimum age filter (in day)                              |
| `--age-max`              | Maximum age filter (in day)                              |
| --exclude-subjects`      | List of subject IDs to exclude (e.g., sub-01 sub-02)     |
```
### BaBA21 Usage

_for timepoint 0_ (N=17 subjects)
```bash
python preprocessing/parse_dataset.py -i BaBa21_openneuro -o list_of_subjects/subjects_ses-0.csv \
--age-min 0 --age-max 100  -f ses-0 \
--exclude-subjects sub-Oz 
```
_for timepoint 1_ (N=18 subjects)
```bash
python preprocessing/parse_dataset.py -i BaBa21_openneuro -o list_of_subjects/subjects_ses-1.csv \
--age-min 200 --age-max 400  -f ses-1 \
--exclude-subjects sub-Ozy
```
_for timepoint 2_ (N=21 subjects)
```bash
python preprocessing/parse_dataset.py -i BaBa21_openneuro -o list_of_subjects/subjects_ses-2.csv \
--age-min 600 --age-max 900  -f ses-2 \
```
_for timepoint 3_ (N=21 subjects)
```bash
python preprocessing/parse_dataset.py -i BaBa21_openneuro -o list_of_subjects/subjects_ses-3.csv \
--age-min 1500 --age-max 1800  -f ses-3 \
```

## STEP3: Pre-processing anatomical volumes (T1w, T2w)

### Denoise (T1w, T2w) 
### _denoise_anat.py_ description
This Python script reads a CSV file listing subject/session pairs, navigates a BIDS dataset structure, and runs ANTs DenoiseImage on T1w and T2w images.
This script writes the denoised images into a derivatives folder within the BIDS dataset, following the BIDS standard for derivatives data.
For each input image found in the original dataset under:
```<dataset_root>/sub-XX/ses-YY/anat/```
the script saves the denoised image in:
```<dataset_root>/derivatives/denoised/sub-XX/ses-YY/anat/```
```
| Option               | Description                                        |
| -------------------- | -------------------------------------------------- |
| `-i`, `--input-csv`  | CSV file with `subject,session` columns (required) |
| `-b`, `--bids-root`  | Path to the BIDS dataset root (required)           |
| `-o`, `--output-log` | Optional file to save paths of denoised outputs    |
| `--threads`          | Number of ITK/ANTs threads (default: 12)           |
| `--dry-run`          | Print commands without executing them              |
```

```bash
python preprocessing/denoise_anat.py \
  -i list_of_subjects/subjects_ses-3.csv \
  -b BaBa21_openneuro \
  --threads 8 \
  -o log/denoise_files_ses-3.txt
```
## re-orient (T1w, T2w) on Haiko89 T1w template

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

```
| Option               | Description                                               |
| -------------------- | --------------------------------------------------------- |
| `-i`, `--input`      | Path to the original Haiko89 folder (required)            |
| `-o`, `--output`     | Path to the derivatives/atlas folder (inside derivatives) |
```

```bash
python preprocessing/convert_haiko_to_bids_derivative.py -i Haiko89 -o BaBa21_openneuro/derivatives/atlas
```
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
```
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

```
| Option                | Description                                                                                     |
| --------------------  | ----------------------------------------------------------------------------------------------- |
| `--bids_root`         | Path to the root of the BIDS dataset (required).                                                |
| `--subjects_csv`      | CSV file containing columns `sub` and `ses` listing subjects and sessions to process (required).|
| `--output_derivatives`| Optional path to derivatives directory. Defaults to `{bids_root}/derivatives`.                  |
| `--sym`               | Use symmetric Haiko89 template (default: asymmetric)`.                                          |
| `--padding`           | Flag to generate a padded version of the Haiko89 template image                                 |
| `--pad_size`          | Padding size in pixel (default: 50)                                                             |
| `--generate_brainmask`| Flag to generate a brainmask TPM by thresholding the sum of CSF, GM, and WM tissue maps.        |
| `--flipping_LR`       | Flip warped T1w/T2w images Left-Right (default: False)                                          |
| `--session_filter`    | Optional list of sessions (e.g. `ses-1 ses-2`) to limit processing to these sessions only.      |
| `--dry-run`           | Print commands without executing them.                                                          |
| `--threads`           | Number of threads for ITK/ANTs (default: 12)                                                    |
```
_for timepoint 3_ (Generate a Haiko89 brainmask and padded template only once)
```bash
python preprocessing/realign_subjects_2_Haiko89.py \
  --subjects_csv list_of_subjects/subjects_ses-3.csv \
  --bids_root BaBa21_openneuro \
  --sym \
  --threads 8 \
  --padding \
  --pad_size 50 \
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

# PART2: The pipeline steps for **(4D+t)** longitudinal BaBa21 template interpolation


