## STEP4: Generation of Intermediate Timepoint Templates

### interpolate_long_template.py description

| Option                       | Description                                                                                              |
| ---------------------------- | -------------------------------------------------------------------------------------------------------- |
| `--bids_root`                | Root BIDS directory (**required**).                                                                      |
| `--template_name`            | Template subject name (**required**).                                                                    |
| `--sessions`                 | List of sessions in chronological order (**required**).                                                  |
| `--registration_modalities`  | Modalities to use for registration, e.g., `T2w T1w` (**required**).                                      |
| `--suffix_modalities`        | Suffix for each registration modality, in the same order as `--registration_modalities` (**required**).  |
| `--registration_metrics`     | Metrics corresponding to each registration modality, e.g., `MI CC` or `MI[1,32] CC[1,4]` (**required**). |
| `--template_path`            | Subfolder within the template directory containing the files (default: `final`).                         |
| `--output_path`              | Subfolder where outputs/intermediate results are saved (default: `intermediate`).                        |
| `--compute-reg`              | Flag to actually compute registration (if not set, registration commands are skipped).                   |
| `--contrasts_to_interpolate` | List of contrast modalities to interpolate across timepoints.                                            |
| `--keep-tmp`                 | Flag to keep temporary files instead of deleting them.                                                   |
| `--dry-run`                  | If set, commands are printed but not executed.                                                           |

```bash
python postprocessing/interpolate_long_template.py  \
--bids_root BaBa21_openneuro   --template_name BaBa21 \
--sessions ses-3 ses-2 ses-1 \
--registration_modalities T2w T1w \
--registration_metrics CC CC \
--compute-reg \
--reg_long_type desc-MM \
--suffix_modalities \
    space-CACP_desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped \
    space-CACP_desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped \
--template_path final \
--dry-run
```
```bash
python postprocessing/interpolate_long_template.py  \
--bids_root BaBa21_openneuro   --template_name BaBa21 \
--sessions ses-1 ses-0 \
--registration_modalities T2w T1w label-WM_mask_probseg \
--compute-reg \
--reg_long_type desc-MM \
--registration_metrics MI MI CC[1,4] \
--suffix_modalities \
    space-CACP_desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped \
    space-CACP_desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped \
    desc-sym_space-CACP_desc-symmetric  \
--template_path final 
```

```bash
python postprocessing/interpolate_long_template.py  \
--bids_root BaBa21_openneuro   --template_name BaBa21 \
--sessions ses-3 ses-2 ses-1 ses-0\
--registration_modalities T1w \
--registration_metrics CC \
--reg_long_type desc-MM \
--suffix_modalities \
    space-CACP_desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped \
--template_path final \ 
--contrasts_to_interpolate \
  desc-sym_space-CACP_desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped_T1w \
  desc-sym_space-CACP_desc-symmetric-sharpen_desc-debiased_desc-norm_desc-cropped_T2w \
  desc-sym_space-CACP_desc-symmetric_label-WM_mask_probseg
```


[<-- previous STEP](longitudinal_registration.md) [return menu](../pipeline4D.md)