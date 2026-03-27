#!/usr/bin/env python3
"""
combine_all_json_to_csv.py

Usage:
    python combine_all_json_to_csv.py JSON_FOLDER output.csv

What it does:
- Reads EVERY .json file in JSON_FOLDER
- Each JSON can contain:
      * a single dict OR
      * a list of dicts
- Extracts all objects into one DataFrame
- Ensures all MASTER_COLS exist
- Writes a clean output.csv
"""

import os
import sys
import json
import pandas as pd

# ---- MUST MATCH MASTER_DATA HEADERS EXACTLY ----
MASTER_COLS = [
    "Study_ID","Author","Year","Title","Journal","DOI_or_PMID",
    "Etiology","Subtype","Congenital_or_Acquired","Side_deaf_or_lesion",
    "Chronicity_months","Sample_Size_Patients","Sample_Size_Controls",
    "Mean_Age_Patients","Sex_Ratio_Patients","Modality","Acquisition_Type",
    "Scanner_FieldStrength_T","Analysis_Toolbox","Hedges_g_exact",
    "Hedges_g_variance","CI_lower","CI_upper","P_value","Statistic_type",
    "Statistic_value","Direction","ROI_Homogenized","Big_Area","Matter",
    "Side","MNI_X","MNI_Y","MNI_Z","Measure","Network_Assignment",
    "Study_Quality_Score","Extractor","Notes","Source_PDF_or_ZIP",
]

def load_json(path):
    """Returns list of dicts from one JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []


def main(json_folder, output_csv):
    if not os.path.isdir(json_folder):
        raise ValueError(f"Not a folder: {json_folder}")

    combined = []

    for filename in sorted(os.listdir(json_folder)):
        if filename.lower().endswith(".json"):
            full_path = os.path.join(json_folder, filename)
            rows = load_json(full_path)

            study_id = os.path.splitext(filename)[0]
            for r in rows:
                if not r.get("Study_ID"):
                    r["Study_ID"] = study_id
                combined.append(r)

    if not combined:
        print("No JSON objects found. Output not created.")
        return

    df = pd.DataFrame(combined)

    # Ensure master columns exist
    for col in MASTER_COLS:
        if col not in df.columns:
            df[col] = None

    df = df[MASTER_COLS]

    df.to_csv(output_csv, index=False)
    print(f"✅ Created {output_csv} with {len(df)} rows.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("\nUsage: python combine_all_json_to_csv.py JSON_FOLDER output.csv\n")
        sys.exit(1)

    folder = sys.argv[1]
    outfile = sys.argv[2]
    main(folder, outfile)
