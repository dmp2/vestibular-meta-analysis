#!/usr/bin/env python3
"""Validate local inputs, scripts, expected outputs, and row eligibility without R."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LEGACY = ROOT / "mycode-11.24"


DK_PATTERNS = [
    "anterior cingulate cortex",
    "cingulate gyrus",
    "cuneus",
    "fusiform gyrus",
    "insula",
    "lateral occipital cortex",
    "lingual gyrus",
    "middle frontal gyrus",
    "middle temporal gyrus",
    "precentral gyrus",
    "postcentral gyrus",
    "precuneus",
    "superior frontal gyrus",
    "superior temporal gyrus",
    "superior orbitofrontal",
    "supramarginal gyrus",
]

SUB_PATTERNS = [
    "hippocampus",
    "parahippocamp",
    "amygdala",
    "caudate",
    "putamen",
    "pallid",
    "accumb",
    "thalam",
    "brainstem",
    "pons",
    "cerebell",
    "vermi",
]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def clean(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"", "na", "nan"}:
        return ""
    return text


def has_float(value: str | None) -> bool:
    try:
        float(clean(value))
        return clean(value) != ""
    except ValueError:
        return False


def matches_any(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in patterns)


def workflow_summary() -> dict[str, object]:
    required_paths = {
        "top_output": ROOT / "output.csv",
        "legacy_output": LEGACY / "output.csv",
        "legacy_output_with_g": LEGACY / "output_with_g.csv",
        "brain_pipeline": ROOT / "run_brain_plot_pipeline.R",
        "brain_master": ROOT / "brain_plots_master.R",
        "funnel_master": ROOT / "funnel_plots_master.R",
        "baujat_master": ROOT / "baujat_plots_master.R",
        "forest_master": ROOT / "forest_plots_master.R",
        "validator": ROOT / "validate_workflow.py",
    }

    files = {name: path.exists() for name, path in required_paths.items()}
    legacy_output_rows = read_csv_rows(required_paths["legacy_output"]) if required_paths["legacy_output"].exists() else []
    output_with_g_rows = read_csv_rows(required_paths["legacy_output_with_g"]) if required_paths["legacy_output_with_g"].exists() else []

    compute_eligible = [
        row for row in legacy_output_rows
        if clean(row.get("Statistic_type")).lower() in {"t", "z", "f"}
        and has_float(row.get("Statistic_value"))
        and has_float(row.get("Sample_Size_Patients"))
        and has_float(row.get("Sample_Size_Controls"))
    ]

    acquired_brain_rows = [
        row for row in output_with_g_rows
        if clean(row.get("Congenital_or_Acquired")).lower() == "acquired"
        and clean(row.get("ROI_Homogenized"))
        and has_float(row.get("Hedges_g_exact"))
    ]

    variance_rows = [
        row for row in output_with_g_rows
        if has_float(row.get("Hedges_g_exact"))
        and has_float(row.get("Hedges_g_variance"))
    ]

    forest_rows = [
        row for row in output_with_g_rows
        if has_float(row.get("Hedges_g_exact"))
        and has_float(row.get("CI_lower"))
        and has_float(row.get("CI_upper"))
    ]

    funnel_baujat = {}
    for etio in ["acquired", "congenital"]:
        for region_type, patterns in [("cortex", DK_PATTERNS), ("subcortex", SUB_PATTERNS)]:
            key = f"{etio}_{region_type}"
            eligible = [
                row for row in variance_rows
                if clean(row.get("Congenital_or_Acquired")).lower() == etio
                and matches_any(clean(row.get("ROI_Homogenized")), patterns)
            ]
            funnel_baujat[key] = len(eligible)

    forest_groups = {}
    for group in ["acquired", "congenital"]:
        forest_groups[group] = sum(
            1 for row in forest_rows
            if clean(row.get("Congenital_or_Acquired")).lower() == group
        )

    expected_outputs = {
        "brain": [
            LEGACY / "brain_acquired_DK2.png",
            LEGACY / "brainpanel_acquired_DK_cortex_only.png",
            LEGACY / "acquired_left_lateral_DK.png",
            LEGACY / "acquired_left_medial_DK.png",
            LEGACY / "acquired_right_lateral_DK.png",
            LEGACY / "acquired_right_medial_DK.png",
            LEGACY / "acquired_subcortex_cerebellum_ASEG.png",
        ],
        "funnel": [
            LEGACY / "funnel_acquired_cortex.png",
            LEGACY / "funnel_acquired_subcortex.png",
            LEGACY / "funnel_congenital_cortex.png",
            LEGACY / "funnel_congenital_subcortex.png",
        ],
        "baujat": [
            LEGACY / "baujat_acquired_cortex.png",
            LEGACY / "baujat_acquired_subcortex.png",
            LEGACY / "baujat_congenital_cortex.png",
            LEGACY / "baujat_congenital_subcortex.png",
        ],
        "forest": [
            LEGACY / "forest" / "forest_acquired.png",
            LEGACY / "forest" / "forest_acquired.svg",
            LEGACY / "forest" / "forest_congenital.png",
            LEGACY / "forest" / "forest_congenital.svg",
        ],
    }

    output_status = {
        group: {
            path.relative_to(ROOT.parent).as_posix(): path.exists()
            for path in paths
        }
        for group, paths in expected_outputs.items()
    }

    return {
        "required_files_present": files,
        "row_counts": {
            "legacy_output": len(legacy_output_rows),
            "output_with_g": len(output_with_g_rows),
            "compute_stage_eligible_rows": len(compute_eligible),
            "brain_stage_acquired_rows": len(acquired_brain_rows),
            "variance_rows_total": len(variance_rows),
            "forest_rows_total": len(forest_rows),
        },
        "funnel_baujat_eligibility": funnel_baujat,
        "forest_eligibility": forest_groups,
        "expected_output_status": output_status,
    }


def main() -> None:
    summary = workflow_summary()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
