# the BABACOOL project

We present the BABACOOL (BAby Brain Atlas COnstruction for Optimized Labeled segmentation) approach for creating multi-modal developmental atlases, which we used to produce BaBa21, a population-based longitudinal developmental baboon template. BaBa21 consists of structural (T1- and T2-weighted) images and tissue probability maps from a population of 21 baboons (Papio anubis, Female=9 Male=12) scanned at 4 timepoints beginning from 2 weeks after birth and continuing to sexual maturity (5 years).
This resource is made available to provide a normalization target for baboon data across the lifespan, and further, facilitate neuroimaging research in baboons, comparative research with humans and nonhuman primate species for which developmental templates are available (e.g., macaques). 

## (Optional but recommended) Create a python environment:
```bash
conda create --name BABACOOL
conda activate BABACOOL
pip install -r requirements.txt
```
### list of external dependencies to install
- FSL v6.0.7.6 (fslmaths, fslstats, fslswapdim, flirt, fsleyes)
- ANTs v2.4 (antsRegistration, antsApplyTransforms, MultiplyImages, ImageMath, CopyImageHeaderInformation, AverageImages, DenoiseImage, antsMultivariateTemplateConstruction2.sh, T1xT2BiasFieldCorrection.sh)
- Convert3D v1.4 (c3d_affine_tool, c3d)
- Freesurfer 8.1.0 (mri_convert)

## Alternative with minimalist Docker image, including all babacool scripts, git/datalad, other software dependencies
```bash
#This approach ensures full reproducibility of the computational environment, including all pinned software dependencies used for BaBa21 construction.

#install
docker pull arnaudletroter/babacool:1.0
#run
docker run -it --rm  arnaudletroter/babacool:1.0 /bin/bash

#convert docker image to singularity image
singularity build babacool_v1.sif docker://arnaudletroter/babacool:1.0

# Build (for documentation purposes only)
# The Docker image was originally built on macOS 26.3.1 (Apple Silicon M2 Pro)
# using Docker Desktop version 4.25.0.
# However, the environment is fully portable and can be rebuilt from the provided Dockerfile on any system supporting Docker.
# docker build -t babacool:1.0 .
```

## How to use ?

This repository provides a complete pipeline for longitudinal brain template construction and analysis. The workflow can be used in two contexts:
1. **Reproduction of the BaBa21 template (as presented in this study)**  
2. **Application to other longitudinal datasets**
---
### BaBa21 template construction (this study)

[# PART1: pipeline processing steps for **3D** template construction](pipeline3D.md) 

[# PART2: pipeline processing steps for **(4D+t)** longitudinal template interpolation](pipeline4D.md)

[# FINAL RESULTS: **(4D+t)** animation of BaBa21 4D and growth trajectories of brain tissues](BaBa21_4D.md)

This sequence reproduces exactly the processing used for BaBa21 generation, including the dataset-specific initialization described in the manuscript.

---
### Usage on other datasets
When applying this pipeline to a new dataset, users should follow the same processing workflow described above.

**Important: manual initialization step**
A single manual step is required before running the automated pipeline:
- [Manual delineation of a 3-axis AC-PC](postprocessing/longitudinal_registration.md) binary mask in the chosen reference timepoint (equivalent to the BaBa21 ses-3 initialization)
This step is dataset-specific and must be performed for each new dataset. All subsequent steps of the pipeline are fully automated.

## Preview of results
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

## If you use it, please cite the paper:
Katherine L. Bryant, Arnaud Le Troter, David Meunier, Yannick Becker, Scott A. Love, Siham Bouziane, Kep Kee Loh, Julien Sein, Luc Renaud, Olivier Coulon, Adrien Meguerditchian, 
under revision in Imaging Neuroscience. Longitudinal MRI template of the baboon brain from birth to adolescence

Arnaud Le Troter, David Meunier, Katherine Bryant, Julien Sein, Siham Bouziane, and Adrien Meguerditchian (2025). BaBa21. OpenNeuro. [Dataset] doi: doi:10.18112/openneuro.ds005424.v1.0.1

## Work in Progress 

integration of dMRI templates and atlas of Tract 
<td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/FAcolor_snap.gif" width="400" height="150" />
</td>

## Acknowledgements
We are very grateful to the Station de Primatologie CNRS, particularly animal care staff, vets and technicians as well as administrative staff of the ILCB, the CRPN and the LPC: Nadia Melili, Nadera Bureau, Frederic Lombardo and Colette Pourpe respectively.
