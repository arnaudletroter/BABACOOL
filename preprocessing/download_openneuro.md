## STEP1: Download BaBa21 BIDS dataset from openneuro (ID=ds005424)

This dataset contains 21 subjects (4 sessions), and the resulting template sub-BaBa21, and probabilistic atlas (TPM WM,GM,CSF) . 
The T1w and T2w anatomical volumes and manual segmentations (WM,GM,CSF) of a single subject (sub-Prune) are published without embargo. 
Other twenty subjects can be retrieved on request from the authors and will be published in a next version.

### You can use git
```bash
git clone https://openneuro.org/git/3/ds005424
or
git clone https://github.com/OpenNeuroDatasets/ds005424.git
```

Note: The above command only clones the metadata skeleton of the dataset.
To retrieve the full dataset files, including all images and segmentation masks, we recommend using DataLad.
Detailed instructions are available here: [DataLad + OpenNeuro guide](https://handbook.datalad.org/en/latest/usecases/openneuro.html)

### or datalad (recommended)
```bash
configure git before
git config --global user.email "your-email@"
git config --global user.name "your-github-account"

cd /babacool
datalad clone https://github.com/OpenNeuroDatasets/ds005424.git

ouptput:
[INFO   ] Remote origin not usable by git-annex; setting annex-ignore                                                                                                                              
[INFO   ] https://github.com/OpenNeuroDatasets/ds005424.git/config download failed: Not Found                                                                                                      
install(ok): /babacool/ds005424 (dataset)

to get a subject
cd /babacool/ds005424
datalad get sub-Prune

output:
get(ok): sub-Prune/ses-0/anat/sub-Prune_ses-0_T1w.nii.gz (file)                                                                                                                                    
get(ok): sub-Prune/ses-0/anat/sub-Prune_ses-0_T2w.nii.gz (file)                                                                                                                                    
get(ok): sub-Prune/ses-1/anat/sub-Prune_ses-1_T1w.nii.gz (file)
get(ok): sub-Prune/ses-1/anat/sub-Prune_ses-1_T2w.nii.gz (file)
get(ok): sub-Prune/ses-2/anat/sub-Prune_ses-2_T1w.nii.gz (file)
get(ok): sub-Prune/ses-2/anat/sub-Prune_ses-2_T2w.nii.gz (file)
get(ok): sub-Prune/ses-3/anat/sub-Prune_ses-3_T1w.nii.gz (file)
get(ok): sub-Prune/ses-3/anat/sub-Prune_ses-3_T2w.nii.gz (file)
get(ok): sub-Prune (directory)
action summary:
get (ok: 9)

download all:
datalad get .
Total:   1%|▍                | 18.0M/3.43G [00:09<30:05, 1.89M Bytes/s]
Get derivatives/atlas/sub-Haiko89/ses-Adult/ana ..:  28%|████▌           | 1.03M/3.61M [00:00<00:01, 1.96M Bytes/s]
Get derivatives/atlas/sub-Haiko89/ses-Adult/ana ..:  35%|████████▋                | 1.25M/3.61M [00:00<00:01, 2.05M Bytes/s]
Get derivatives/atlas/sub-Haiko89/ses-Adult/ana ..:  41%|█████████████▎                  | 1.50M/3.61M [00:00<00:00, 2.16M Bytes/s]
Get derivatives/atlas/sub-Haiko89/ses-Adult/ana ..:  49%|████████████████▉                  | 1.75M/3.61M [00:00<00:00, 2.28M Bytes/s]
....
waiting 10 minutes
action summary:
  get (ok: 513)
Total 3,4GB

```
[return menu](../pipeline3D.md) [--> next STEP](bids_exporter.md)
