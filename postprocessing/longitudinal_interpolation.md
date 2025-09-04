## STEP5: Generation of Intermediate Timepoint Templates

### interpolate_long_template.py description

| Option                                                            | Description                                                                                                    |
|-------------------------------------------------------------------| -------------------------------------------------------------------------------------------------------------- |
| `-h, --help`                                                      | Show this help message and exit.                                                                               |
| `--bids_root BIDS_ROOT`                                           | Root BIDS directory.                                                                                           |
| `--template_name TEMPLATE_NAME`                                   | Template subject name.                                                                                         |
| `--sessions [SESSIONS ...]`                                       | List of sessions (ordered).                                                                                    |
| `--registration_modalities [REGISTRATION_MODALITIES ...]`         | Modalities to use for registration, e.g. `T2w T1w`.                                                            |
| `--template_prefix TEMPLATE_PREFIX`                               | Template prefix used for registration (e.g. `space-CACP_desc-average_padded_debiased_cropped_norm_symmetric`). |
| `--registration_metrics [REGISTRATION_METRICS ...]`               | Metrics corresponding to `registration_modalities`, e.g. `MI CC` or `MI[1,32] CC[1,4]`.                        |
| `--template_path TEMPLATE_PATH`                                   | Subfolder for template.                                                                                        |
| `--reg_long_type REG_LONG_TYPE`                                   | Name of registration type.                                                                                     |
| `--output_path OUTPUT_PATH`                                       | Subfolder for template.                                                                                        |
| `--compute-reg`                                                   | Compute registration.                                                                                          |
| `--contrasts_to_interpolate [CONTRASTS_TO_INTERPOLATE ...]`       | Contrasts to interpolate across timepoints.                                                                    |
| `--keep-tmp`                                                      | Keep temporary files.                                                                                          |
| `--dry-run`                                                       | Don't actually run commands.                                                                                   |
| `--morph-enable`                                                  | Enable morphing between two sessions.                                                                          |
| `--morph-numsteps MORPH_NUMSTEPS`                                 | Number of morphing steps (default = 10).                                                                       |
| `--morph-step MORPH_STEP`                                         | Morphing increment (default = 1).                                                                              |
| `--morph-tmpdir MORPH_TMPDIR`                                     | Temporary directory for morphing images.                                                                       |
| `--morph-merge4d`                                                 | Merge all morphs into one 4D file with `fslmerge`.                                                             |

```bash
python postprocessing/interpolate_long_template.py  \
--bids_root BaBa21_openneuro   --template_name BaBa21 \
--template_prefix space-CACP_desc-average_padded_debiased_cropped_norm_symmetric \
--sessions ses-3 ses-2 ses-1 \
--registration_modalities T2w T1w \
--registration_metrics CC CC \
--compute-reg \
--reg_long_type desc-MM \
--template_path final \
--dry-run    
      
      
```
```bash
## temporary copy of the WM TPM used as metric for registration
cd BaBa21_openneuro/derivatives/template/sub-BaBa21/ses-0/final
cp -rf sub-BaBa21_ses-0_space-CACP_label-WM_desc-thr0p2_symmetric_probseg.nii.gz sub-BaBa21_ses-0_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_WM.nii.gz
cd ../../ses-1/final
cp -rf sub-BaBa21_ses-1_space-CACP_label-WM_desc-thr0p2_symmetric_probseg.nii.gz sub-BaBa21_ses-1_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_WM.nii.gz

python postprocessing/interpolate_long_template.py  \
--bids_root BaBa21_openneuro   --template_name BaBa21 \
--template_prefix space-CACP_desc-average_padded_debiased_cropped_norm_symmetric \
--sessions ses-1 ses-0 \
--registration_modalities T2w T1w WM \
--compute-reg \
--registration_metrics MI MI CC[1,4] \
--reg_long_type desc-MM \
--template_path final 
```

```bash
python postprocessing/interpolate_long_template.py  \
--bids_root BaBa21_openneuro   --template_name BaBa21 \
--sessions ses-3 ses-2 ses-1 ses-0 \
--registration_modalities T1w \
--registration_metrics CC \
--reg_long_type desc-MM \
--template_prefix space-CACP_desc-average_padded_debiased_cropped_norm_symmetric \
--template_path final \
--contrasts_to_interpolate \
 space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T1w \
 space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T2w \
 space-CACP_label-WM_desc-thr0p2_padded_symmetric_probseg \
 space-CACP_label-GM_desc-thr0p2_padded_symmetric_probseg \
 space-CACP_label-CSF_desc-thr0p2_padded_symmetric_probseg \
 --morph-enable --morph-numsteps 10 --morph-step 1 --morph-tmpdir tmp --morph-merge4d
```




[<-- previous STEP](longitudinal_registration.md) [return menu](../pipeline4D.md)