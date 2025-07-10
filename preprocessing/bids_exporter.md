## STEP2: BIDS Session-Age CSV Exporter](preprocessing/bids_exporter.md)

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

| Option                   | Description                                               |
| ------------------------ |-----------------------------------------------------------|
| `-i`, `--input`          | Path to the BIDS root directory (required)                |
| `-o`, `--output`         | Output CSV filename (default: subjects_sessions.csv)      |
| `-f`, `--filter-session` | Include only sessions whose names contain this substring  |
| `--age-min`              | Minimum age filter (in day)                               |
| `--age-max`              | Maximum age filter (in day)                               |
| --exclude-subjects`      | List of subject IDs to exclude (e.g., sub-01 sub-02)      |

### BaBA21 Usage

_for timepoint 0_ (N=17 subjects)
```bash
python preprocessing/parse_dataset.py -i BaBa21_openneuro -o list_of_subjects/subjects_ses-0.csv \
--age-min 0 --age-max 100  -f ses-0 \
--exclude-subjects sub-Oz sub-Omelette 
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
[<-- previous STEP](download_openneuro.md) [return menu](../pipeline3D.md) [--> next STEP](denoise_realign.md)