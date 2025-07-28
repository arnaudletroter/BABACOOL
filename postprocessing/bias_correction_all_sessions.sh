#!/bin/bash
sessions=("ses-0" "ses-1" "ses-2" "ses-3")
for ses in "${sessions[@]}"; do
    path_template="$1/derivatives/template/sub-BaBa21/${ses}/final"
    postprocessing/T1xT2BiasFieldCorrection.sh \
        -t1 ${path_template}/sub-BaBa21_${ses}_desc-symmetric-sharpen_T1w.nii.gz \
        -t2 ${path_template}/sub-BaBa21_${ses}_desc-symmetric-sharpen_T2w.nii.gz \
        -b ${path_template}/sub-BaBa21_${ses}_desc-HR-symmetric_desc-brain_mask_probseg.nii.gz \
        -k -s 2 \
        -os "_desc-debiased"
done