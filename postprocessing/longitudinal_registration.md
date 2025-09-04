## STEP3: Longitudinal registration (3 stages)

**Semi-automatic AC-PC Alignment Across Timepoints (OPTIONAL)** 
  - stage 1: manual segmentation of 3-axis binary mask in ses-3 space (called **sub-BaBa21_ses-3_desc-symmetric_label-3axis_mask.nii.gz** )
  - stage 2: Segmentation by rigid + affine registration (ants) for propagation of previous 3-axis mask (ses-3 -> ses-2 -> ses-1 -> ses-0)
  - stage 3: rigid only registration (flirt) 3-axis masks for initial constrained re-alignment of all sessions (ses-0 <-> ses-1 <-> ses-2 <-> ses-3)
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

### register_long_templates.py description

### Command-Line Arguments
| Option                        | Description                                                                             |
|-------------------------------|-----------------------------------------------------------------------------------------|
| `--bids_root`                 | Root BIDS directory (required).                                                         |
| `--template_name`             | Template subject name (required).                                                       |
| `--sessions`                  | List of sessions (ordered) (required). Example: `ses-3 ses-2`.                          |
| `--template_type`             | Template type. Default: `desc-average_padded_debiased_cropped_norm`. (required)                            |
| `--template_modalities`       | List of modalities to use for registration (required). Example: `T1w T2w`.              |
| `--template_path`             | Subfolder for template. Default: `final`.                                               |
| `--brain_mask_suffix`         | Brain mask suffix.                                                                      |
| `--segmentation_mask_suffix`  | Segmentation mask suffix for automatic propagation                                      |
| `--compute-reg`               | Flag to actually compute registration (if not set, registration commands are skipped).  |
| `--contrasts_to_warp`         | Contrasts to warp in CA-CP space. Optional list. Example: `T1w T2w`.                    |
| `--dry-run`                   | Don't actually run commands; perform a dry run. Use this flag to simulate the workflow. |

AC-PC Alignment Across Timepoints template using 3 stages registration ( --compute-reg )

```bash
python postprocessing/register_long_templates.py  \
  --bids_root BaBa21_openneuro \
  --template_name BaBa21 \
  --sessions ses-3 ses-2 ses-1 ses-0 \
  --template_modalities T1w \
  --template_type desc-average_padded_debiased_cropped_norm --template_path final \
  --brain_mask_suffix label-BM_desc-thr0p2_mask \
  --compute-reg \
  --contrasts_to_warp \
      label-WM_desc-thr0p2_probseg \
      label-GM_desc-thr0p2_probseg \
      label-CSF_desc-thr0p2_probseg \
      label-BM_desc-thr0p2_mask \
      desc-average_padded_debiased_cropped_norm_T1w \
      desc-average_padded_debiased_cropped_norm_T2w \
  --segmentation_mask_suffix desc-symmetric_label-3axis_mask
```

For next step: duplicate (for renaming) ses-3 files to ses-3_space-CACP
```
cd BaBa21_openneuro/derivatives/template/sub-BaBa21/ses-3/final
cp -rf sub-BaBa21_ses-3_label-WM_desc-thr0p2_probseg.nii.gz sub-BaBa21_ses-3_space-CACP_label-WM_desc-thr0p2_probseg.nii.gz
cp -rf sub-BaBa21_ses-3_label-GM_desc-thr0p2_probseg.nii.gz sub-BaBa21_ses-3_space-CACP_label-GM_desc-thr0p2_probseg.nii.gz
cp -rf sub-BaBa21_ses-3_label-CSF_desc-thr0p2_probseg.nii.gz sub-BaBa21_ses-3_space-CACP_label-CSF_desc-thr0p2_probseg.nii.gz
cp -rf sub-BaBa21_ses-3_label-BM_desc-thr0p2_mask.nii.gz sub-BaBa21_ses-3_space-CACP_label-BM_desc-thr0p2_mask.nii.gz
cp -rf sub-BaBa21_ses-3_desc-average_padded_debiased_cropped_norm_T1w.nii.gz sub-BaBa21_ses-3_space-CACP_desc-average_padded_debiased_cropped_norm_T1w.nii.gz
cp -rf sub-BaBa21_ses-3_desc-average_padded_debiased_cropped_norm_T2w.nii.gz sub-BaBa21_ses-3_space-CACP_desc-average_padded_debiased_cropped_norm_T2w.nii.gz
cp -rf sub-BaBa21_ses-3_desc-sharpen_T1w.nii.gz sub-BaBa21_ses-3_space-CACP_desc-sharpen_T1w.nii.gz
cp -rf sub-BaBa21_ses-3_desc-sharpen_T2w.nii.gz sub-BaBa21_ses-3_space-CACP_desc-sharpen_T2w.nii.gz
```
output structure of longitudinal transformations 
```
../BaBa21_openneuro/derivatives/transforms/sub-BaBa21
└── long
    ├── ses-1_to_ses-0_0GenericAffine.mat
    ├── ses-1_to_ses-0_flirt_ants_rig.mat
    ├── ses-1_to_ses-0_flirt.mat
    ├── ses-2_to_ses-1_0GenericAffine.mat
    ├── ses-2_to_ses-1_flirt_ants_rig.mat
    ├── ses-2_to_ses-1_flirt.mat
    ├── ses-3_to_ses-2_0GenericAffine.mat
    ├── ses-3_to_ses-2_flirt_ants_rig.mat
    └── ses-3_to_ses-2_flirt.mat
```

Just apply the previous transformation to other contrasts (here average sharpen T1w T2w templates), skip registration step

```bash
python postprocessing/register_long_templates.py  \
  --bids_root BaBa21_openneuro \
  --template_name BaBa21 \
  --sessions ses-3 ses-2 ses-1 ses-0 \
  --template_modalities T1w \
  --template_type desc-average_padded_debiased_cropped_norm --template_path final \
  --brain_mask_suffix label-BM_desc-thr0p2_mask \
  --contrasts_to_warp \
      desc-sharpen_T1w \
      desc-sharpen_T2w \
      label-WM_desc-thr0p2_padded_probseg \
      label-GM_desc-thr0p2_padded_probseg \
      label-CSF_desc-thr0p2_padded_probseg
```

Example output structure on 2 successive sessions
```
BaBa21_openneuro/
└── derivatives/
    └── template/
        └── sub-BaBa21/
            └── ses-2/
                └── final/
                    ├── sub-BaBa21_ses-2_space-CACP_label-WM_desc-thr0p2_probseg.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_label-GM_desc-thr0p2_probseg.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_label-CSF_desc-thr0p2_probseg.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_label-BM_desc-thr0p2_mask.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_label-WM_desc-thr0p2_padded_probseg.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_label-GM_desc-thr0p2_padded_probseg.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_label-CSF_desc-thr0p2_padded_probseg.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_desc-average_padded_debiased_cropped_norm_T1w.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_desc-average_padded_debiased_cropped_norm_T2w.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_desc-sharpen_T1w.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_desc-sharpen_T2w.nii.gz   
            └── ses-3/
                └── final/
                    ├── sub-BaBa21_ses-3_space-CACP_label-WM_desc-thr0p2_probseg.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_label-GM_desc-thr0p2_probseg.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_label-CSF_desc-thr0p2_probseg.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_label-BM_desc-thr0p2_mask.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_label-WM_desc-thr0p2_padded_probseg.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_label-GM_desc-thr0p2_padded_probseg.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_label-CSF_desc-thr0p2_padded_probseg.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_desc-average_padded_debiased_cropped_norm_T1w.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_desc-average_padded_debiased_cropped_norm_T2w.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_desc-sharpen_T1w.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_desc-sharpen_T2w.nii.gz
```

[<-- previous STEP](hist_normalization.md) [return menu](../pipeline4D.md) [--> next STEP](symmetrize_template.md)