## STEP3: Longitudinal registration

- CA-CP Alignment Across Timepoints (OPTIONAL)
- Symmetrize all volumes by L/R flipping and rigid registration step (OPTIONAL)
- multi-modal registration based on T1w and T2w contrasts (TPM OPTIONAL), with three stages (rigid, affine, SyN)

### register_long_templates.py description

python postprocessing/register_long_templates.py  \
  --bids_root ../BaBa21_openneuro \
  --template_name BaBa21 \
  --sessions ses-3 ses-2 ses-1 ses-0 \
  --template_type desc-symmetric-sharpen \
  --template_modalities T1w T2w \
  --brain_mask_suffix desc-symmetric_desc-brain_mask_probseg \
  --TPM_modalities desc-symmetric_label-WM_mask_probseg --TPM_path paper \
  --template_path paper --brainmask_path paper --segmentation_mask_suffix desc-symmetric_desc-3axis-mask


[<-- previous STEP](hist_normalization.md) [return menu](../pipeline4D.md) [--> next STEP](longitudinal_interpolation.md)