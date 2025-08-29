## STEP4: Symmetrize all volumes by L/R flipping with rigid registration step (OPTIONAL)

The script performs iterative symmetrization of anatomical images and other contrasts in a BIDS dataset, ensuring consistent left-right symmetry across sessions. It combines rigid registration, flipping, and averaging of images.

### algorithm for symmetrization

**1. Input Validation**
- Check required anatomical templates and optional contrast maps.  
- Stop execution if any required files are missing.

**2. Initial Preparation**  
- For each session:  
  - Load anatomical template (T1w by default).  
  - Create left-right flipped version.  
  - Compute temporary symmetric image (`sym-tmp_mean`).
  
**3. Iterative Registration (Symmetrization Loop)**  
- Repeat until stopping criteria:  
  - Register original image → temporary symmetric image (`FSL flirt` + `--flirt-opts`).  
    - Save matrix → `anat2sym.mat`.  
  - Register flipped image → same symmetric image.  
    - Save matrix → `flip2sym.mat`.  
  - Decompose matrices → Euler angles (`rx, ry, rz`) + translation.  
  - Compute symmetry score → absolute sum of rotation angles.  
  - Stop if:  
    - All sum Euler angles < `--max-angle`.  
    - Iterations reach `--max-iter`.  
  - Otherwise, repeat using previous `sym-tmp_mean`.
  
**4. Final Symmetric Image**  
- Apply transformations to original and flipped images.  
- Average results → final symmetric anatomical image.  
- Preserve BIDS-compliant naming (`symmetric` before modality).

**5. Propagation to Other Contrasts**  
- For each contrast in `--contrasts_to_sym`:  
  - Apply `anat2sym.mat` and `flip2sym.mat`.  
  - Average → symmetric contrast map.  
  - Optionally remove temporary files.
  
**6. Outputs**  
- Symmetrized anatomical images per session.  
- Symmetrized contrast maps (if provided).  
- Optional logging of symmetry scores.  
- Temporary files can be kept or deleted (`--keep-tmp`).

### sym_template.py description

| Option                | Description                                                                                    |
| --------------------- |------------------------------------------------------------------------------------------------|
| `--bids_root`         | Root BIDS directory (**required**).                                                            |
| `--template_name`     | Template subject name (**required**).                                                          |
| `--sessions`          | List of sessions (ordered) (**required**).                                                     |
| `--template_type`     | Template type (default: `desc-average_padded_debiased_cropped_norm`).                          |
| `--template_modality` | Single modality for rigid registration (default: `T1w`).                                       |
| `--template_path`     | Subfolder for template (default: `final`).                                                     |
| `--contrasts_to_sym`  | List of contrasts/maps to symmetrize.                                                          |
| `--keep-tmp`          | Keep temporary files (flipped/warped).                                                         |
| `--compute-reg`       | Compute registration (default: False).                                                         |
| `--dry-run`           | Don’t actually run commands.                                                                   |
| `--flirt-opts`        | Options to pass to FSL flirt (default: `-dof 6 -searchrx -5 5 -searchry -5 5 -searchrz -5 5`). |
| `--max-angle`         | Maximum sum of Euler rotation angle (degrees) to stop iteration (default: 1).                  |
| `--max-iter`          | Maximum number of iterations for symmetrization (default: 10).                                 |

First running to Symmetrize anatomical template using rigid registration ( --compute-reg )

```bash
python postprocessing/sym_template.py --bids_root ../BaBa21_openneuro  --template_name BaBa21  \
  --sessions ses-2 ses-3 --template_modality T1w --template_type space-CACP_desc-average_padded_debiased_cropped_norm \
  --template_path final --max-angle 1 --max-iter 4 \
  --compute-reg
```

Second running to just apply the previous transformation to other contrasts/maps

```bash
python postprocessing/sym_template.py --bids_root ../BaBa21_openneuro  --template_name BaBa21  \
  --sessions ses-2 ses-3 \
  --template_modality T1w --template_type space-CACP_desc-average_padded_debiased_cropped_norm \
  --template_path final \
  --contrasts_to_sym \
      space-CACP_label-WM_desc-thr0p2_probseg \
      space-CACP_label-GM_desc-thr0p2_probseg \
      space-CACP_label-CSF_desc-thr0p2_probseg \
      space-CACP_label-BM_desc-thr0p2_mask \
      space-CACP_desc-average_padded_debiased_cropped_norm_T1w \
      space-CACP_desc-average_padded_debiased_cropped_norm_T2w \
      space-CACP_desc-sharpen_T1w \
      space-CACP_desc-sharpen_T2w
```

Example output structure on 2 successive sessions
```
BaBa21_openneuro/
└── derivatives/
    └── template/
        └── sub-BaBa21/
            └── ses-2/
                └── final/
                    ├── sub-BaBa21_ses-2_space-CACP_label-WM_desc-thr0p2_symmetric_probseg.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_label-GM_desc-thr0p2_symmetric_probseg.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_label-CSF_desc-thr0p2_symmetric_probseg.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_label-BM_desc-thr0p2_symmetric_mask.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T1w.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T2w.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_desc-sharpen_symmetric_T1w.nii.gz
                    ├── sub-BaBa21_ses-2_space-CACP_desc-sharpen_symmetric_T2w.nii.gz   
            └── ses-3/
                └── final/
                    ├── sub-BaBa21_ses-3_space-CACP_label-WM_desc-thr0p2_symmetric_probseg.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_label-GM_desc-thr0p2_symmetric_probseg.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_label-CSF_desc-thr0p2_symmetric_probseg.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_label-BM_desc-thr0p2_symmetric_mask.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T1w.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T2w.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_desc-sharpen_symmetric_T1w.nii.gz
                    ├── sub-BaBa21_ses-3_space-CACP_desc-sharpen_symmetric_T2w.nii.gz
```

[<-- previous STEP](longitudinal_registration.md) [return menu](../pipeline4D.md) [--> next STEP](longitudinal_interpolation.md)