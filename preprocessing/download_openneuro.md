## STEP1: Download BaBa21 BIDS dataset from openneuro (ID=ds005424)

This dataset contains 21 subjects (4 sessions), and the resulting template sub-BaBa21, and probabilistic atlas (TPM WM,GM,CSF) . 
The T1w and T2w anatomical volumes and manual segmentations (WM,GM,CSF) of a single subject (sub-Prune) are published without embargo. 
Other twenty subjects can be retrieved on request from the authors and will be published in a next version.

### You can use git
```bash
$ git clone https://openneuro.org/git/3/ds005424
or
$ git clone https://github.com/OpenNeuroDatasets/ds005424.git
```

Note: The above command only clones the metadata skeleton of the dataset.
To retrieve the full dataset files, including all images and segmentation masks, we recommend using DataLad.
Detailed instructions are available here: [DataLad + OpenNeuro guide](https://handbook.datalad.org/en/latest/usecases/openneuro.html)

### or datalad
```bash
$ datalad install https://openneuro.org/git/3/ds005424
```
[return menu](../pipeline3D.md) [--> next STEP](bids_exporter.md)
