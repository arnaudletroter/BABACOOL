# PART1: pipeline processing steps for **3D** BaBa21 template construction

This pipeline, written mainly in bash and python, uses [Ants](#2)  and [FSL](#2)  to generate a 3D anatomical template from any BIDS-formatted dataset. 
The [BaBa21](#3) dataset is used here as an example, but the pipeline can be applied to other BIDS datasets as well.
The template can be generated across multiple ages (sessions) and in a multi-modal contrasts (e.g., T1w, T2w).

Processing steps:

1. [## STEP1: Prepare dataset](preprocessing/download_openneuro.md) \
Download a BIDS-formatted dataset from OpenNeuro (example here: BaBa21, Dataset ID: ds005424).

2. [## STEP2: BIDS Session-Age CSV Exporter](preprocessing/bids_exporter.md) \
Generate a CSV file containing session and participant age metadata for the next steps 

3. [## STEP3: Pre-processing stages](preprocessing/denoise_realign.md)
Denoise and rigidly align T1-weighted and T2-weighted volumes to a standard orientation.

4. [## STEP4: Post-processing template construction](postprocessing/template_construction.md)
Use preprocessed images to build a 3D group-average anatomical template, per age

5. [## STEP5: Post-processing TPM generation](postprocessing/generate_TPM.md)
Generate population-based issue probability maps (e.g., gray matter, white matter, CSF) by averaging individual segmentations.

## References
<a id="1">[ANTS]</a> https://github.com/ANTsX/ANTs \
<a id="2">[FSL]</a> https://fsl.fmrib.ox.ac.uk/fsl/docs/#/ \
<a id="3">[BaBa21_2025]</a>
Arnaud Le Troter, David Meunier, Katherine Bryant, Julien Sein, Siham Bouziane, Adrien Meguerditchian,
BaBa21. OpenNeuro. [Dataset] doi: doi:10.18112/openneuro.ds005424.v1.0.0