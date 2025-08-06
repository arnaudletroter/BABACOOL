# PART2: pipeline processing steps **(4D+t)** longitudinal template interpolation

This pipeline, written mainly in bash and python, uses [Ants](#2)  and [FSL](#2)  to generate a 5D (4D+t) anatomical template from any BIDS-formatted dataset. 
The [BaBa21](#3) dataset is used here as an example, but the pipeline can be applied to other BIDS datasets as well.
The template can be generated across multiple ages (sessions) and in a multi-modal contrasts (e.g., T1w, T2w).

Processing steps:

[STEP1: B1 Bias correction](postprocessing/bias_correction.md) \
_"T1w and T2w images co-registered in the same space are corrected for B1− and some B1+ bias. 
The bias field is estimated from the square root of the product of the T1w and T2w images, after excluding non-brain tissues. 
This method works because the opposing contrasts in gray and white matter cancel each other out, leaving only the bias field. 
This approach was described by [Glasser](#1) in the context of myelin mapping."_

**We would like to thank Régis Trapeau for suggesting the use of this method in the context of non-human primate data and for providing the  [script](postprocessing/T1xT2BiasFieldCorrection.sh) used to implement it.**

[STEP2: Histogram-Based Normalization ](postprocessing/hist_normalization.md) \
T1w and T2w maps were normalized using multiclass histogram-based approach

[STEP3: Longitudinal registration](postprocessing/longitudinal_registration.md)
- CA-CP Alignment Across Timepoints (OPTIONAL) (rigid + affine)
- multi-modal SyN only registration based on T1w and T2w contrasts (TPM OPTIONAL)

[STEP4: Symmetrize template by L/R flipping and rigid registration (OPTIONAL)](postprocessing/symmetrize_template.md)

[STEP5: Generation of longitudinal intermediate Timepoint](postprocessing/longitudinal_interpolation.md) 

## References
<a id="1">[Glasser, et al.] The minimal preprocessing pipelines for the Human Connectome Project,
NeuroImage 2013 </a> https://doi.org/10.1016/j.neuroimage.2013.04.127 \
