# STEP4: Symmetrize all volumes by L/R flipping with rigid registration step (OPTIONAL)

### sym_template.py description

### Command-Line Arguments

| Option                | Description                                                         |
| --------------------- | ------------------------------------------------------------------- |
| `--bids_root`         | Root BIDS directory (**required**).                                 |
| `--template_name`     | Template subject name (**required**).                               |
| `--sessions`          | List of sessions (ordered) (**required**).                          |
| `--template_type`     | Template type. Defaults to `desc-symmetric-sharpen` (**required**). |
| `--template_modality` | Single modality to use for rigid FLIRT registration (**required**). |
| `--template_path`     | Subfolder where templates are located. Defaults to `final`.         |
| `--contrasts_to_sym`  | List of contrasts to symmetrize (e.g., `T2w`, `PD`).                |
| `--keep-tmp`          | Keep temporary files (e.g., flipped/warped images).                 |
| `--compute-reg`       | Compute registration and symmetrization steps. Defaults to `False`. |
| `--dry-run`           | Only print commands without executing them. Useful for testing.     |

# Symmetrize template using rigid registration ( --compute-reg )

```bash
python postprocessing/sym_template.py --bids_root ../BaBa21_openneuro  --template_name BaBa21 \
  --sessions ses-3 ses-2 ses-1 ses-0 \
  --template_modality T1w \
  --template_type space-CACP_desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped --template_path final \
  --compute-reg
```

# Just apply the previous transformation to other contrasts

```bash
python postprocessing/sym_template.py --bids_root ../BaBa21_openneuro  --template_name BaBa21 \
  --sessions ses-3 ses-2 ses-1 ses-0 \
  --template_modality T1w \
  --template_type space-CACP_desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped --template_path final \
  --contrasts_to_sym \
  space-CACP_desc-symmetric_label-WM_mask_probseg \
  space-CACP_desc-symmetric_label-GM_mask_probseg \
  space-CACP_desc-symmetric_label-CSF_mask_probseg \
  space-CACP_desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped_T1w \
  space-CACP_desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped_T2w \
  space-CACP_desc-symmetric-sharpen_T1w \
  space-CACP_desc-symmetric-sharpen_T2w
```

[<-- previous STEP](longitudinal_registration.md) [return menu](../pipeline4D.md) [--> next STEP](longitudinal_interpolation.md)