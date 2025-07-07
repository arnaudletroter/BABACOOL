#!/usr/bin/env python3

import os
import shutil
import argparse
import pandas as pd

def update_participants_tsv(participants_tsv_path):
    """
    Read or create participants.tsv inside the derivatives directory,
    and add or update the entry for sub-Haiko89 with 'type=Template'.
    """
    if os.path.isfile(participants_tsv_path):
        participants_df = pd.read_csv(participants_tsv_path, sep='\t')
    else:
        participants_df = pd.DataFrame(columns=['participant_id', 'type'])

    new_participant = {
        'participant_id': 'sub-Haiko89',
        'type': 'Template'
    }

    if 'participant_id' in participants_df.columns and new_participant['participant_id'] in participants_df['participant_id'].values:
        participants_df.loc[participants_df['participant_id'] == new_participant['participant_id'], 'type'] = new_participant['type']
    else:
        participants_df = pd.concat([participants_df, pd.DataFrame([new_participant])], ignore_index=True)

    participants_df.to_csv(participants_tsv_path, sep='\t', index=False)
    print(f"Updated participants.tsv at {participants_tsv_path}")

def create_sessions_tsv(sub_dir):
    """
    Create sub-Haiko89_sessions.tsv in derivatives/atlas/sub-Haiko89/
    with session_id and age (in days).
    """
    sessions_tsv_path = os.path.join(sub_dir, "sub-Haiko89_sessions.tsv")
    sessions_df = pd.DataFrame({
        'session_id': ['ses-Adult'],
        'age': [4000]
    })
    sessions_df.to_csv(sessions_tsv_path, sep='\t', index=False)
    print(f"Created sessions file at {sessions_tsv_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Convert Haiko89 template folder into BIDS derivatives subject with BIDS-compliant filenames."
    )
    parser.add_argument("-i", "--input", required=True, help="Path to the original Haiko89 folder")
    parser.add_argument("-o", "--output", required=True, help="Path to the derivatives/atlas folder (inside derivatives)")

    args = parser.parse_args()

    input_dir = args.input
    output_root = args.output

    if not os.path.isdir(input_dir):
        print(f"Error: Input folder does not exist: {input_dir}")
        exit(1)

    # Target anat folder in BIDS derivatives
    sub_dir = os.path.join(output_root, "sub-Haiko89")
    anat_dir = os.path.join(sub_dir, "ses-Adult", "anat")
    os.makedirs(anat_dir, exist_ok=True)
    print(f"Created target folder: {anat_dir}")

    # Mapping of input → BIDS-compliant output filenames
    mapping = {
        "Haiko89_Asymmetric.Template_n89.nii.gz": "sub-Haiko89_ses-Adult_desc-asymmetric_T1w.nii.gz",
        "Haiko89sym_Symmetric.Template_n89.nii.gz": "sub-Haiko89_ses-Adult_desc-symmetric_T1w.nii.gz",
        "TPM_Asymmetric.CSF_Haiko89.nii.gz": "sub-Haiko89_ses-Adult_desc-asymmetric_label-CSF_probseg.nii.gz",
        "TPM_Asymmetric.GreyMatter_Haiko89.nii.gz": "sub-Haiko89_ses-Adult_desc-asymmetric_label-GM_probseg.nii.gz",
        "TPM_Asymmetric.WhiteMatter_Haiko89.nii.gz": "sub-Haiko89_ses-Adult_desc-asymmetric_label-WM_probseg.nii.gz",
        "TPM_Symmetric.CSF_Haiko89sym.nii.gz": "sub-Haiko89_ses-Adult_desc-symmetric_label-CSF_probseg.nii.gz",
        "TPM_Symmetric.GreyMatter_Haiko89sym.nii.gz": "sub-Haiko89_ses-Adult_desc-symmetric_label-GM_probseg.nii.gz",
        "TPM_Symmetric.WhiteMatter_Haiko89sym.nii.gz": "sub-Haiko89_ses-Adult_desc-symmetric_label-WM_probseg.nii.gz",
    }

    for orig, new in mapping.items():
        src = os.path.join(input_dir, orig)
        dst = os.path.join(anat_dir, new)

        if not os.path.isfile(src):
            print(f"Warning: {orig} not found in input folder. Skipping.")
            continue

        shutil.copy2(src, dst)
        print(f"Copied {src} -> {dst}")

    # participants.tsv is at the root of the BIDS dataset (two levels up from derivatives/atlas)
    bids_root = os.path.abspath(os.path.join(output_root, "..", ".."))
    participants_tsv_path = os.path.join(bids_root, "participants.tsv")
    update_participants_tsv(participants_tsv_path)

    # Create sessions file in sub-Haiko89 directory
    create_sessions_tsv(sub_dir)

    print("Conversion completed successfully.")

if __name__ == "__main__":
    main()
