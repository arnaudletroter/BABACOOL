# PART2: pipeline processing steps **(4D+t)** longitudinal template interpolation

This pipeline, written mainly in bash and python, uses [Ants](#2)  and [FSL](#2)  to generate a 5D (4D+t) anatomical template from any BIDS-formatted dataset. 
The [BaBa21](#3) dataset is used here as an example, but the pipeline can be applied to other BIDS datasets as well.
The template can be generated across multiple ages (sessions) and in a multi-modal contrasts (e.g., T1w, T2w).

Processing steps:

1. [STEP1: B1 Bias correction](postprocessing/bias_correction.md) \
_"T1w and T2w images co-registered in the same space are corrected for B1− and some B1+ bias. 
The bias field is estimated from the square root of the product of the T1w and T2w images, after excluding non-brain tissues. 
This method works because the opposing contrasts in gray and white matter cancel each other out, leaving only the bias field. 
This approach was described by [Glasser](#1) in the context of myelin mapping."_

**We would like to thank Régis Trapeau for suggesting the use of this method in the context of non-human primate data and for providing the  [script](postprocessing/T1xT2BiasFieldCorrection.sh) used to implement it.**

2. [STEP2: Histogram-Based Normalization ](postprocessing/hist_normalization.md) \
T1w and T2w maps were normalized using multiclass histogram-based approach

3. [STEP3: Longitudinal registration](postprocessing/longitudinal_registration.md)
- CA-CP Alignment Across Timepoints (OPTIONAL)
- Symmetrize all volumes by L/R flipping and rigid registration step (OPTIONAL)
- multi-modal registration based on T1w and T2w contrasts (TPM OPTIONAL), with three stages (rigid, affine, SyN)

4. [STEP4: Generation of Intermediate Timepoint Templates](postprocessing/longitudinal_interpolation.md) 

## References
<a id="1">[Glasser, et al.] The minimal preprocessing pipelines for the Human Connectome Project,
NeuroImage 2013 </a> https://doi.org/10.1016/j.neuroimage.2013.04.127 \
