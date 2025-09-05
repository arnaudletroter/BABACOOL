# FINAL RESULTS: **(4D+t)** animation of BaBa21

<table>
<tr> 
    <td align="center">average T1w (CACP re-oriented + contrast normalized + symmetrized + skull-stripped + padded)</td>
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/final_T1w_snap.gif" width="639" height="244" />
    </td>
</tr>
<tr> 
    <td align="center">average T2w (CACP re-oriented + contrast normalized + symmetrized + skull-stripped + padded)</td>
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/final_T2w_snap.gif" width="639" height="244" />
    </td>
</tr>
<tr> 
    <td align="center">WM TPM (CACP re-oriented + symmetrized)</td>
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/final_WM_snap.gif" width="639" height="244" />
    </td>
</tr>
</table>




```bash
./snap.sh ses-1_to_ses-0_desc-MM_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T1w_morph_4D.nii.gz 0 T1w
./snap.sh ses-2_to_ses-1_desc-MM_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T1w_morph_4D.nii.gz 10 T1w
./snap.sh ses-3_to_ses-2_desc-MM_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T1w_morph_4D.nii.gz 20 T1w

./snap.sh ses-1_to_ses-0_desc-MM_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T2w_morph_4D.nii.gz 0 T2w
./snap.sh ses-2_to_ses-1_desc-MM_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T2w_morph_4D.nii.gz 10 T2w
./snap.sh ses-3_to_ses-2_desc-MM_space-CACP_desc-average_padded_debiased_cropped_norm_symmetric_T2w_morph_4D.nii.gz 20 T2w

./snap.sh ses-1_to_ses-0_desc-MM_space-CACP_label-WM_desc-thr0p2_padded_symmetric_probseg_morph_4D.nii.gz 0 WM
./snap.sh ses-2_to_ses-1_desc-MM_space-CACP_label-WM_desc-thr0p2_padded_symmetric_probseg_morph_4D.nii.gz 10 WM
./snap.sh ses-3_to_ses-2_desc-MM_space-CACP_label-WM_desc-thr0p2_padded_symmetric_probseg_morph_4D.nii.gz 20 WM
 
python create_gif.py --folder snap/ --pref T1w --duration 10 --output final_T1w_snap.gif
python create_gif.py --folder snap/ --pref T2w --duration 10 --output final_T2w_snap.gif
python create_gif.py --folder snap/ --pref WM --duration 10 --output final_WM_snap.gif
```

