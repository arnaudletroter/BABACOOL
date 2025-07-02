#!/usr/bin/env python3

import os
import argparse
import pandas as pd

def load_session_ages_for_subject(subject_dir, subject_label):
    """
    Load session ages from sub-*_sessions.tsv for a given subject.
    Returns a dictionary {session_id: age}.
    """
    session_file = os.path.join(subject_dir, f"{subject_label}_sessions.tsv")
    if not os.path.exists(session_file):
        return {}

    try:
        df = pd.read_csv(session_file, sep='\t')
        if 'session_id' in df.columns and 'age' in df.columns:
            return dict(zip(df['session_id'], df['age']))
    except Exception as e:
        print(f"Warning: Failed to read {session_file}: {e}")

    return {}

def parse_bids_dataset(
    bids_root,
    session_filter=None,
    age_min=None,
    age_max=None,
    exclude_subjects=None
):
    """
    Parse the BIDS dataset and return a list of dictionaries
    with 'subject', 'session', 'age', applying filters as needed.
    """
    data = []

    if exclude_subjects is None:
        exclude_subjects = []

    for subject in sorted(os.listdir(bids_root)):
        subject_dir = os.path.join(bids_root, subject)
        if not (subject.startswith("sub-") and os.path.isdir(subject_dir)):
            continue

        if subject in exclude_subjects:
            continue

        session_ages = load_session_ages_for_subject(subject_dir, subject)

        sessions = [
            d for d in os.listdir(subject_dir)
            if d.startswith("ses-") and os.path.isdir(os.path.join(subject_dir, d))
        ]

        if not sessions:
            continue

        for ses in sorted(sessions):
            if session_filter and session_filter not in ses:
                continue

            age = session_ages.get(ses, None)
            if age is not None:
                try:
                    age = float(age)
                except ValueError:
                    age = None

            if age_min is not None and age is not None and age < age_min:
                continue
            if age_max is not None and age is not None and age > age_max:
                continue

            data.append({
                "subject": subject,
                "session": ses,
                "age": age
            })

    return data

def main():
    parser = argparse.ArgumentParser(
        description="Export a CSV listing subjects, sessions, and ages from a BIDS dataset, with optional filters."
    )
    parser.add_argument("-i", "--input", required=True, help="Path to the BIDS root directory.")
    parser.add_argument("-o", "--output", default="subjects_sessions.csv", help="Output CSV filename (default: subjects_sessions.csv).")
    parser.add_argument("-f", "--filter-session", help="Only include sessions that contain this substring (e.g., 'ses-0').")
    parser.add_argument("--age-min", type=float, help="Minimum age (filter).")
    parser.add_argument("--age-max", type=float, help="Maximum age (filter).")
    parser.add_argument("--exclude-subjects", nargs="+", help="List of subject IDs to exclude (e.g., 'sub-01 sub-02').")

    args = parser.parse_args()

    bids_root = args.input
    output_csv = args.output

    if not os.path.isdir(bids_root):
        print(f"Error: the provided path does not exist or is not a directory: {bids_root}")
        exit(1)

    data = parse_bids_dataset(
        bids_root,
        session_filter=args.filter_session,
        age_min=args.age_min,
        age_max=args.age_max,
        exclude_subjects=args.exclude_subjects
    )

    if not data:
        print("No data found matching the given criteria.")
    else:
        df = pd.DataFrame(data)
        df.to_csv(output_csv, index=False)
        print(f"\nCSV file generated: {output_csv}")

        # Statistics
        num_subjects = df['subject'].nunique()
        valid_ages = df['age'].dropna()
        mean_age = valid_ages.mean()
        std_age = valid_ages.std()

        print("\nSummary statistics:")
        print(f"  Number of unique subjects : {num_subjects}")
        print(f"  Mean age                  : {mean_age:.2f}")
        print(f"  Standard deviation (age) : {std_age:.2f}")

if __name__ == "__main__":
    main()
