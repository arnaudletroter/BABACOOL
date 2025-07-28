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

2. [STEP2 (Optional): Template Symmetrization](preprocessing/template_sym.md)
Symmetrize all volumes by L/R flipping and rigid registration step.
The multi-modal templates were left/right flipped and averaged to generate a temporary symmetrical template, which was used as the final target for a last rigid registration step. 
This step produced an exact symmetrical template by averaging both the co-registered template and its flipped version.

3. [STEP3: Histogram-Based Normalization ](postprocessing/hist_normalization.md) \
T1w and T2w maps were normalized using multiclass histogram-based approach (Sun et al., 2015), using the following equation:


4. [STEP4: Longitudinal registration](postprocessing/template_construction.md)
Use preprocessed images to build a 3D group-average anatomical template, per age

## References
<a id="1">[Glasser, et al. , The minimal preprocessing pipelines for the Human Connectome Project,
NeuroImage 2013]</a> https://doi.org/10.1016/j.neuroimage.2013.04.127 \
