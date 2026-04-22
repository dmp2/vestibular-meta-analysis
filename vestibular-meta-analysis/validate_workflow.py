#!/usr/bin/env python3
"""Validate local inputs, scripts, expected outputs, and plot eligibility without R."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LEGACY = ROOT / "mycode-11.24"


DK_PATTERNS = [
    "anterior cingulate cortex",
    "cingulate gyrus",
    "cuneus",
    "fusiform gyrus",
    "fusiform",
    "insula",
    "intracalcarine cortex",
    "intracalcarine",
    "lingual gyrus",
    "lateral occipital cortex",
    "lateral occipital",
    "middle frontal gyrus",
    "middle temporal gyrus (mt/v5)",
    "middle temporal visual area (mt/v5)",
    "middle temporal gyrus",
    "mt/v5",
    "postcentral gyrus",
    "precentral gyrus",
    "precuneus / superior parietal white matter",
    "precuneus",
    "superior frontal gyrus",
    "superior orbitofrontal cortex",
    "superior orbitofrontal",
    "orbital gyrus",
    "superior temporal gyrus",
    "primary somatosensory cortex",
    "supramarginal gyrus",
]

SUB_PATTERNS = [
    "hippocampus",
    "parahippocamp",
    "presubiculum",
    "amygdala",
    "caudate",
    "putamen",
    "pallid",
    "accumb",
    "thalam",
    "brainstem",
    "pons",
    "mesencephalon",
    "midbrain",
    "pontomesencephalic",
    "vestibular nuclei",
    "gracile nucleus",
    "cerebell",
    "vermi",
    "culmen",
    "peduncle",
    "inferior semi-lunar lobule",
    "crus i",
    "lobule vi",
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


def has_value(value: str | None) -> bool:
    return clean(value) != ""


def has_float(value: str | None) -> bool:
    text = clean(value)
    if not text:
        return False
    try:
        float(text)
        return True
    except ValueError:
        return False


def merge_key(row: dict[str, str]) -> str:
    return "||".join(
        clean(row.get(column))
        for column in ("Study_ID", "ROI_Homogenized", "Side", "Measure")
    )


def assert_unique_keys(rows: list[dict[str, str]], source_name: str) -> dict[str, dict[str, str]]:
    keyed: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []

    for row in rows:
        key = merge_key(row)
        if key in keyed:
            duplicates.append(key)
        keyed[key] = row

    if duplicates:
        sample = ", ".join(duplicates[:5])
        raise ValueError(
            f"{source_name} has non-unique composite keys on "
            f"Study_ID + ROI_Homogenized + Side + Measure. Sample keys: {sample}"
        )

    return keyed


def prefer(primary: str | None, secondary: str | None) -> str:
    if has_value(primary):
        return str(primary).strip()
    if has_value(secondary):
        return str(secondary).strip()
    return ""


def source_of_value(
    primary: str | None,
    secondary: str | None,
    primary_name: str,
    secondary_name: str,
) -> str:
    if has_value(primary):
        return primary_name
    if has_value(secondary):
        return secondary_name
    return "missing"


def reconcile_secondary_tables(
    historical_rows: list[dict[str, str]],
    computed_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    historical = assert_unique_keys(historical_rows, "historical")
    computed = assert_unique_keys(computed_rows, "computed")

    historical_keys = set(historical)
    computed_keys = set(computed)

    missing_in_computed = sorted(historical_keys - computed_keys)
    missing_in_historical = sorted(computed_keys - historical_keys)

    if missing_in_computed or missing_in_historical:
        details = []
        if missing_in_computed:
            details.append(
                "missing in computed: " + ", ".join(missing_in_computed[:5])
            )
        if missing_in_historical:
            details.append(
                "missing in historical: " + ", ".join(missing_in_historical[:5])
            )
        raise ValueError(
            "Historical and computed secondary-plot tables do not cover the same "
            "composite keys: " + " | ".join(details)
        )

    column_names = list(historical_rows[0].keys()) if historical_rows else []
    reconciled: list[dict[str, str]] = []

    for row in historical_rows:
        key = merge_key(row)
        historical_row = historical[key]
        computed_row = computed[key]

        merged = {
            column: prefer(historical_row.get(column), computed_row.get(column))
            for column in column_names
        }
        merged["effect_source"] = source_of_value(
            historical_row.get("Hedges_g_exact"),
            computed_row.get("Hedges_g_exact"),
            "historical",
            "computed",
        )
        merged["variance_source"] = source_of_value(
            historical_row.get("Hedges_g_variance"),
            computed_row.get("Hedges_g_variance"),
            "historical",
            "computed",
        )
        if has_value(historical_row.get("CI_lower")) and has_value(
            historical_row.get("CI_upper")
        ):
            merged["ci_source"] = "historical"
        elif has_value(computed_row.get("CI_lower")) and has_value(
            computed_row.get("CI_upper")
        ):
            merged["ci_source"] = "computed"
        else:
            merged["ci_source"] = "missing"

        reconciled.append(merged)

    return reconciled


def matches_any(text: str, patterns: list[str]) -> bool:
    lowered = clean(text).lower()
    return any(pattern in lowered for pattern in patterns)


def subset_secondary_rows(
    rows: list[dict[str, str]],
    etio: str,
    region_type: str,
    require_variance: bool = False,
    require_ci: bool = False,
) -> list[dict[str, str]]:
    patterns = DK_PATTERNS if region_type == "cortex" else SUB_PATTERNS

    subset = [
        row
        for row in rows
        if clean(row.get("Congenital_or_Acquired")).lower() == etio
        and has_float(row.get("Hedges_g_exact"))
        and matches_any(clean(row.get("ROI_Homogenized")), patterns)
    ]

    if require_variance:
        subset = [
            row for row in subset if has_float(row.get("Hedges_g_variance"))
        ]

    if require_ci:
        subset = [
            row
            for row in subset
            if has_float(row.get("CI_lower")) and has_float(row.get("CI_upper"))
        ]

    return subset


def forest_rows_for_group(rows: list[dict[str, str]], etio: str) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if clean(row.get("Congenital_or_Acquired")).lower() == etio
        and has_float(row.get("Hedges_g_exact"))
        and has_float(row.get("CI_lower"))
        and has_float(row.get("CI_upper"))
    ]


def workflow_summary() -> dict[str, object]:
    required_paths = {
        "top_output": ROOT / "output.csv",
        "legacy_output": LEGACY / "output.csv",
        "historical_output_with_g": LEGACY / "output_with_g.csv",
        "computed_output_with_g": LEGACY / "output_with_g_computed.csv",
        "brain_pipeline": ROOT / "run_brain_plot_pipeline.R",
        "brain_master": ROOT / "brain_plots_master.R",
        "funnel_master": ROOT / "funnel_plots_master.R",
        "baujat_master": ROOT / "baujat_plots_master.R",
        "forest_master": ROOT / "forest_plots_master.R",
        "meta_helpers": ROOT / "meta_plot_helpers.R",
        "validator": ROOT / "validate_workflow.py",
    }

    files = {name: path.exists() for name, path in required_paths.items()}

    legacy_output_rows = (
        read_csv_rows(required_paths["legacy_output"])
        if required_paths["legacy_output"].exists()
        else []
    )
    historical_rows = (
        read_csv_rows(required_paths["historical_output_with_g"])
        if required_paths["historical_output_with_g"].exists()
        else []
    )
    computed_rows = (
        read_csv_rows(required_paths["computed_output_with_g"])
        if required_paths["computed_output_with_g"].exists()
        else []
    )

    hybrid_rows = (
        reconcile_secondary_tables(historical_rows, computed_rows)
        if historical_rows and computed_rows
        else []
    )

    compute_eligible = [
        row
        for row in legacy_output_rows
        if clean(row.get("Statistic_type")).lower() in {"t", "z", "f"}
        and has_float(row.get("Statistic_value"))
        and has_float(row.get("Sample_Size_Patients"))
        and has_float(row.get("Sample_Size_Controls"))
    ]

    brain_stage_rows = [
        row
        for row in computed_rows
        if clean(row.get("Congenital_or_Acquired")).lower() == "acquired"
        and clean(row.get("ROI_Homogenized"))
        and has_float(row.get("Hedges_g_exact"))
    ]

    secondary_sources = {
        "effect_source": dict(Counter(row["effect_source"] for row in hybrid_rows)),
        "variance_source": dict(
            Counter(row["variance_source"] for row in hybrid_rows)
        ),
        "ci_source": dict(Counter(row["ci_source"] for row in hybrid_rows)),
    }

    funnel_baujat_eligibility = []
    funnel_baujat_expected = {}
    for etio in ("acquired", "congenital"):
        for region_type in ("cortex", "subcortex"):
            effect_rows = subset_secondary_rows(hybrid_rows, etio, region_type)
            variance_rows = subset_secondary_rows(
                hybrid_rows,
                etio,
                region_type,
                require_variance=True,
            )
            ci_rows = subset_secondary_rows(
                hybrid_rows,
                etio,
                region_type,
                require_ci=True,
            )
            eligible_for_model = len(variance_rows) >= 2

            funnel_baujat_eligibility.append(
                {
                    "etio": etio,
                    "region_type": region_type,
                    "rows_effect": len(effect_rows),
                    "rows_variance": len(variance_rows),
                    "rows_ci": len(ci_rows),
                    "eligible_for_model": eligible_for_model,
                }
            )
            funnel_baujat_expected[f"{etio}_{region_type}"] = eligible_for_model

    forest_eligibility = []
    forest_expected = {}
    for etio in ("acquired", "congenital"):
        ci_rows = forest_rows_for_group(hybrid_rows, etio)
        eligible_for_plot = len(ci_rows) >= 1
        forest_eligibility.append(
            {
                "etio": etio,
                "rows_ci": len(ci_rows),
                "eligible_for_plot": eligible_for_plot,
            }
        )
        forest_expected[etio] = eligible_for_plot

    expected_outputs = {
        "brain": [
            {
                "path": LEGACY / "brain_acquired_DK2.png",
                "should_exist": True,
            },
            {
                "path": LEGACY / "brainpanel_acquired_DK_cortex_only.png",
                "should_exist": True,
            },
            {
                "path": LEGACY / "acquired_left_lateral_DK.png",
                "should_exist": True,
            },
            {
                "path": LEGACY / "acquired_left_medial_DK.png",
                "should_exist": True,
            },
            {
                "path": LEGACY / "acquired_right_lateral_DK.png",
                "should_exist": True,
            },
            {
                "path": LEGACY / "acquired_right_medial_DK.png",
                "should_exist": True,
            },
            {
                "path": LEGACY / "acquired_subcortex_cerebellum_ASEG.png",
                "should_exist": True,
            },
        ],
        "funnel": [
            {
                "path": LEGACY / "funnel_acquired_cortex.png",
                "should_exist": funnel_baujat_expected["acquired_cortex"],
            },
            {
                "path": LEGACY / "funnel_acquired_subcortex.png",
                "should_exist": funnel_baujat_expected["acquired_subcortex"],
            },
            {
                "path": LEGACY / "funnel_congenital_cortex.png",
                "should_exist": funnel_baujat_expected["congenital_cortex"],
            },
            {
                "path": LEGACY / "funnel_congenital_subcortex.png",
                "should_exist": funnel_baujat_expected["congenital_subcortex"],
            },
        ],
        "baujat": [
            {
                "path": LEGACY / "baujat_acquired_cortex.png",
                "should_exist": funnel_baujat_expected["acquired_cortex"],
            },
            {
                "path": LEGACY / "baujat_acquired_subcortex.png",
                "should_exist": funnel_baujat_expected["acquired_subcortex"],
            },
            {
                "path": LEGACY / "baujat_congenital_cortex.png",
                "should_exist": funnel_baujat_expected["congenital_cortex"],
            },
            {
                "path": LEGACY / "baujat_congenital_subcortex.png",
                "should_exist": funnel_baujat_expected["congenital_subcortex"],
            },
        ],
        "forest": [
            {
                "path": LEGACY / "forest" / "forest_acquired.png",
                "should_exist": forest_expected["acquired"],
            },
            {
                "path": LEGACY / "forest" / "forest_acquired.svg",
                "should_exist": forest_expected["acquired"],
            },
            {
                "path": LEGACY / "forest" / "forest_congenital.png",
                "should_exist": forest_expected["congenital"],
            },
            {
                "path": LEGACY / "forest" / "forest_congenital.svg",
                "should_exist": forest_expected["congenital"],
            },
        ],
    }

    output_status = {
        group: {
            item["path"].relative_to(ROOT.parent).as_posix(): {
                "exists": item["path"].exists(),
                "should_exist": item["should_exist"],
            }
            for item in items
        }
        for group, items in expected_outputs.items()
    }

    return {
        "required_files_present": files,
        "row_counts": {
            "legacy_output": len(legacy_output_rows),
            "historical_output_with_g": len(historical_rows),
            "computed_output_with_g": len(computed_rows),
            "hybrid_secondary_rows": len(hybrid_rows),
            "compute_stage_eligible_rows": len(compute_eligible),
            "brain_stage_acquired_rows_computed": len(brain_stage_rows),
        },
        "secondary_value_sources": secondary_sources,
        "secondary_plot_eligibility": {
            "funnel_baujat": funnel_baujat_eligibility,
            "forest": forest_eligibility,
        },
        "expected_output_status": output_status,
    }


def main() -> None:
    summary = workflow_summary()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
