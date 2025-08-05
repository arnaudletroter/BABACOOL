## STEP3: Longitudinal registration (3 stages)

stage1: Semi-automatic AC-PC Alignment Across Timepoints (OPTIONAL) with two stages 
  - manual segmentation of 3-axis binary mask in ses-3 space (called **sub-BaBa21_ses-3_desc-symmetric_label-3axis_mask.nii.gz** )
  - first stage: rigid + affine registration (ants) and descending 3-axis mask propagation ses-3 -> ses-2 -> ses-1 -> ses-0
  - second stage: rigid only registration (flirt) and ascending propagation ses-0 -> ses-1 -> ses-2 -> ses-3

<table>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/images/ses-3_CACP_3axis.png" width="600" />
    </td>
</tr>
<tr> 
    <td align="center">sub-BaBa21_ses-3_desc-symmetric_label-3axis_mask.nii.gz</td> 
</tr>
</table>

stage2: Multi-modal registration based on T1w and T2w contrasts (TPM OPTIONAL), with three stages (rigid, affine)

stage3: Symmetrize all volumes by L/R flipping and rigid registration step (OPTIONAL)

### register_long_templates.py description

### Command-Line Arguments
| Option                          | Description                                                                             |
|---------------------------------|-----------------------------------------------------------------------------------------|
| `--bids_root`                   | Root BIDS directory (required).                                                         |
| `--template_name`              | Template subject name (required).                                                       |
| `--sessions`                   | List of sessions (ordered) (required). Example: `ses-3 ses-2`.                          |
| `--template_type`              | Template type. Default: `desc-symmetric-sharpen`. (required)                            |
| `--template_modalities`        | Modalities to use for registration (required). Example: `T1w T2w`.                      |
| `--template_path`              | Subfolder for template. Default: `final`.                                               |
| `--brain_mask_suffix`          | Brain mask suffix.                                                                      |
| `--segmentation_mask_suffix`   | Segmentation mask suffix for automatic propagation                                      |
| `--contrasts_to_warp`          | Contrasts to warp in CA-CP space. Optional list. Example: `T1w T2w`.                    |
| `--dry-run`                    | Don't actually run commands; perform a dry run. Use this flag to simulate the workflow. |


```bash
python postprocessing/register_long_templates.py  \
  --bids_root BaBa21_openneuro \
  --template_name BaBa21 \
  --sessions ses-3 ses-2 ses-1 ses-0\
  --template_modalities T1w \
  --template_type desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped --template_path final \
  --brain_mask_suffix desc-symmetric_brain_mask_probseg \
  --contrasts_to_warp \
      desc-symmetric_label-WM_mask_probseg \
      desc-symmetric_label-GM_mask_probseg \
      desc-symmetric_label-CSF_mask_probseg \
      desc-symmetric_brain_mask_probseg \
      desc-symmetric-sharpen_T1w \
      desc-symmetric-sharpen_T2w \
      desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped_T1w \
      desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped_T2w \
  --segmentation_mask_suffix desc-symmetric_label-3axis_mask
```

[<-- previous STEP](hist_normalization.md) [return menu](../pipeline4D.md) [--> next STEP](longitudinal_interpolation.md)