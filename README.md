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

# PART1: The pipeline steps for **3D** BaBa21 template construction 

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
ses-2	    764\

### Command-Line Arguments
```bash
Argument	Description
-i, --input	(required) Path to the BIDS root directory.
-o, --output	Output CSV filename (default: subjects_sessions.csv).
-f, --filter-session	Include only sessions whose names contain this substring.
--age-min	Minimum age filter.
--age-max	Maximum age filter.
--exclude-subjects	List of subject IDs to exclude (e.g., sub-01 sub-02).
```
### BaBA21 Usage

_for timepoint 0_ 
```bash
python parse_dataset.py -i BaBa21_openneuro -o subjects_ses-0.csv \
--age-min 0 --age-max 100  -f ses-0 \
--exclude-subjects sub-BaBa21 sub-Noe sub-Oz sub-Ozy
```
_for timepoint 1_
```bash
python parse_dataset.py -i BaBa21_openneuro -o subjects_ses-1.csv \
--age-min 0 --age-max 100  -f ses-1 \
--exclude-subjects sub-BaBa21 sub-Noe sub-Oz sub-Ozy
```
_for timepoint 2_
```bash
python parse_dataset.py -i BaBa21_openneuro -o subjects_ses-2.csv \
--age-min 0 --age-max 100  -f ses-2 \
--exclude-subjects sub-BaBa21 sub-Noe sub-Oz sub-Ozy
```
_for timepoint 3_
```bash
python parse_dataset.py -i BaBa21_openneuro -o subjects_ses-3.csv \
--age-min 0 --age-max 100  -f ses-3 \
--exclude-subjects sub-BaBa21 sub-Noe sub-Oz sub-Ozy
```


# PART2: The pipeline steps for **(4D+t)** longitudinal BaBa21 template interpolation


