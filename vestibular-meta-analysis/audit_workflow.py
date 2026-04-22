#!/usr/bin/env python3
"""Generate a reproducible workflow audit for vestibular-meta-analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
AUDIT_MD = ROOT / "WORKFLOW_AUDIT.md"
AUDIT_JSON = ROOT / "audit_summary.json"


CSV_KEY_COLUMNS = [
    "Study_ID",
    "ROI_Homogenized",
    "Hedges_g_exact",
    "Hedges_g_variance",
    "CI_lower",
    "CI_upper",
    "Congenital_or_Acquired",
    "Measure",
    "Matter",
    "Big_Area",
]


TRACKED_CSVS = {
    "top_output": ROOT / "output.csv",
    "legacy_output": ROOT / "mycode-11.24" / "output.csv",
    "historical_output_with_g": ROOT / "mycode-11.24" / "output_with_g.csv",
    "computed_output_with_g": ROOT / "mycode-11.24" / "output_with_g_computed.csv",
    "legacy_output_final": ROOT / "mycode-11.24" / "output_final.csv",
    "root_jsonwithg": ROOT / "jsonwithg.csv",
    "legacy_jsonwithg": ROOT / "mycode-11.24" / "jsonwithg.csv",
}


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


SCRIPT_CATALOG = [
    {
        "path": ROOT / "mycode-11.24" / "compute_hedges_g.R",
        "role": "core_stage",
        "status": "produced by script",
        "notes": "Stable repo-relative compute stage. Reads output.csv and writes output_with_g_computed.csv.",
        "expected_outputs": ["output_with_g_computed.csv"],
    },
    {
        "path": ROOT / "run_brain_plot_pipeline.R",
        "role": "verified_pipeline",
        "status": "produced by script",
        "notes": "Verified one-command brain runner: output.csv -> compute_hedges_g.R -> output_with_g_computed.csv -> brain_plots_master.R.",
        "expected_outputs": [],
    },
    {
        "path": ROOT / "brain_plots_master.R",
        "role": "verified_pipeline",
        "status": "produced by script",
        "notes": "Repo-relative replacement for the acquired brain-plot branch. Matches the committed acquired brain outputs.",
        "expected_outputs": [
            "brain_acquired_DK2.png",
            "brainpanel_acquired_DK_cortex_only.png",
            "acquired_left_lateral_DK.png",
            "acquired_left_medial_DK.png",
            "acquired_right_lateral_DK.png",
            "acquired_right_medial_DK.png",
            "acquired_subcortex_cerebellum_ASEG.png",
        ],
    },
    {
        "path": ROOT / "meta_plot_helpers.R",
        "role": "helper",
        "status": "produced by script",
        "notes": "Hybrid secondary-plot reconciliation layer. Preserves historical variance/CI values and falls back to recomputed effect sizes by composite key.",
        "expected_outputs": [],
    },
    {
        "path": ROOT / "funnel_plots_master.R",
        "role": "verified_pipeline",
        "status": "produced by script",
        "notes": "Repo-relative funnel master using the hybrid secondary-plot table and REML. Saves only variance-eligible groups.",
        "expected_outputs": [
            "funnel_acquired_cortex.png",
            "funnel_acquired_subcortex.png",
            "funnel_congenital_cortex.png",
            "funnel_congenital_subcortex.png",
        ],
    },
    {
        "path": ROOT / "baujat_plots_master.R",
        "role": "verified_pipeline",
        "status": "produced by script",
        "notes": "Repo-relative Baujat master using the hybrid secondary-plot table and REML. Saves only variance-eligible groups.",
        "expected_outputs": [
            "baujat_acquired_cortex.png",
            "baujat_acquired_subcortex.png",
            "baujat_congenital_cortex.png",
            "baujat_congenital_subcortex.png",
        ],
    },
    {
        "path": ROOT / "forest_plots_master.R",
        "role": "verified_pipeline",
        "status": "produced by script",
        "notes": "Repo-relative forest master using the hybrid secondary-plot table. Saves etiologies that have Hedges g plus confidence bounds.",
        "expected_outputs": [
            "forest/forest_acquired.png",
            "forest/forest_acquired.svg",
            "forest/forest_congenital.png",
            "forest/forest_congenital.svg",
        ],
    },
    {
        "path": ROOT / "mycode-11.24" / "merge_json_into_master.R",
        "role": "merge_stage",
        "status": "possibly produced by script",
        "notes": "Suspicious merge step. Join uses Study_ID + ROI_Homogenized, but jsonwithg.csv is sparse in ROI_Homogenized.",
        "expected_outputs": ["output_final.csv"],
    },
    {
        "path": ROOT / "mycode-11.24" / "Brainsurfacemaps.r",
        "role": "historical_figure",
        "status": "produced by script",
        "notes": "Historical acquired cortical DK map script using output_with_g.csv.",
        "expected_outputs": ["brain_acquired_DK2.png"],
    },
    {
        "path": ROOT / "mycode-11.24" / "brainonlydk.R",
        "role": "historical_figure",
        "status": "produced by script",
        "notes": "Historical combined cortex-only DK panel script.",
        "expected_outputs": ["brainpanel_acquired_DK_cortex_only.png"],
    },
    {
        "path": ROOT / "mycode-11.24" / "braint3.R",
        "role": "historical_figure",
        "status": "produced by script",
        "notes": "Historical acquired cortical hemisphere views plus subcortex/cerebellum figure script.",
        "expected_outputs": [
            "acquired_left_lateral_DK.png",
            "acquired_left_medial_DK.png",
            "acquired_right_lateral_DK.png",
            "acquired_right_medial_DK.png",
            "acquired_subcortex_cerebellum_ASEG.png",
        ],
    },
    {
        "path": ROOT / "mycode-11.24" / "braint2.R",
        "role": "historical_figure",
        "status": "possibly produced by script",
        "notes": "Configured to create brainpanel_acquired_DK_ASEG.png, but that output is not currently present.",
        "expected_outputs": ["brainpanel_acquired_DK_ASEG.png"],
    },
    {
        "path": ROOT / "mycode-11.24" / "funnel.r",
        "role": "reference_baseline",
        "status": "possibly produced by script",
        "notes": "Older etiology-based funnel script retained as reference only.",
        "expected_outputs": [],
    },
    {
        "path": ROOT / "mycode-11.24" / "funnelt2.R",
        "role": "reference_baseline",
        "status": "possibly produced by script",
        "notes": "Older four-panel funnel script that informed the current funnel master.",
        "expected_outputs": [
            "funnel_acquired_cortex.png",
            "funnel_acquired_subcortex.png",
            "funnel_congenital_cortex.png",
            "funnel_congenital_subcortex.png",
        ],
    },
    {
        "path": ROOT / "mycode-11.24" / "forest.py",
        "role": "reference_baseline",
        "status": "not attributable from current evidence",
        "notes": "Template Python forest script with non-local paths. Conceptual reference only.",
        "expected_outputs": [],
    },
    {
        "path": ROOT / "meta_analysis_full.py",
        "role": "newer_adaptation",
        "status": "produced by script",
        "notes": "Top-level descriptive plots match committed PNGs. Script expects all_meta_rows.csv, which is not present.",
        "expected_outputs": [
            "plot_big_area_counts.png",
            "plot_matter_counts.png",
            "plot_side_counts.png",
            "plot_roi_counts_top20.png",
        ],
    },
    {
        "path": ROOT / "combine_all_json_to_csv.py",
        "role": "newer_adaptation",
        "status": "possibly produced by script",
        "notes": "Can regenerate a base table from JSON, but the specific JSON source folder is not encoded here.",
        "expected_outputs": ["output.csv"],
    },
    {
        "path": ROOT / "make_brain_panels.r",
        "role": "newer_adaptation",
        "status": "not attributable from current evidence",
        "notes": "Incomplete as written because it sources brain_plot.R from the local folder, but that file is absent here.",
        "expected_outputs": [
            "GM_brain_map.png",
            "GM_funnel.png",
            "GM_baujat.png",
            "GM_roi_per_area.png",
            "WM_brain_map.png",
            "WM_funnel.png",
            "WM_baujat.png",
            "WM_roi_per_area.png",
        ],
    },
]


def relpath(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


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


def summarize_csv(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "path": relpath(path),
            "exists": False,
            "rows": 0,
            "columns": 0,
            "non_null_counts": {},
        }

    rows = read_csv_rows(path)
    fields = list(rows[0].keys()) if rows else []
    non_null_counts = {}
    for col in CSV_KEY_COLUMNS:
        if col in fields:
            non_null_counts[col] = sum(1 for row in rows if has_value(row.get(col)))

    return {
        "path": relpath(path),
        "exists": True,
        "rows": len(rows),
        "columns": len(fields),
        "non_null_counts": non_null_counts,
    }


def compare_csvs(left: Path, right: Path) -> dict[str, object]:
    left_rows = read_csv_rows(left)
    right_rows = read_csv_rows(right)
    changed_rows = []
    tracked_fields = [
        "Study_ID",
        "ROI_Homogenized",
        "Hedges_g_exact",
        "Hedges_g_variance",
        "CI_lower",
        "CI_upper",
    ]

    for index, (left_row, right_row) in enumerate(zip(left_rows, right_rows)):
        differences = {}
        for field in tracked_fields:
            if clean(left_row.get(field)) != clean(right_row.get(field)):
                differences[field] = {
                    "left": left_row.get(field),
                    "right": right_row.get(field),
                }
        if differences:
            changed_rows.append(
                {
                    "row_index": index,
                    "Study_ID": left_row.get("Study_ID") or right_row.get("Study_ID"),
                    "ROI_Homogenized": left_row.get("ROI_Homogenized") or right_row.get("ROI_Homogenized"),
                    "differences": differences,
                }
            )

    return {
        "left": relpath(left),
        "right": relpath(right),
        "row_count_left": len(left_rows),
        "row_count_right": len(right_rows),
        "changed_row_count": len(changed_rows),
        "sample_changed_rows": changed_rows[:12],
    }


def assert_unique_keys(rows: list[dict[str, str]], source_name: str) -> dict[str, dict[str, str]]:
    keyed: dict[str, dict[str, str]] = {}
    for row in rows:
        key = merge_key(row)
        if key in keyed:
            raise ValueError(
                f"{source_name} has non-unique composite keys on "
                "Study_ID + ROI_Homogenized + Side + Measure"
            )
        keyed[key] = row
    return keyed


def prefer(primary: str | None, secondary: str | None) -> str:
    if has_value(primary):
        return clean(primary)
    if has_value(secondary):
        return clean(secondary)
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

    if set(historical) != set(computed):
        raise ValueError(
            "Historical and computed secondary-plot tables do not cover the same composite keys."
        )

    columns = list(historical_rows[0].keys()) if historical_rows else []
    reconciled: list[dict[str, str]] = []

    for row in historical_rows:
        key = merge_key(row)
        historical_row = historical[key]
        computed_row = computed[key]

        merged = {
            column: prefer(historical_row.get(column), computed_row.get(column))
            for column in columns
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
        if has_value(historical_row.get("CI_lower")) and has_value(historical_row.get("CI_upper")):
            merged["ci_source"] = "historical"
        elif has_value(computed_row.get("CI_lower")) and has_value(computed_row.get("CI_upper")):
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
        subset = [row for row in subset if has_float(row.get("Hedges_g_variance"))]

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


def current_secondary_plot_status() -> dict[str, object]:
    historical_path = TRACKED_CSVS["historical_output_with_g"]
    computed_path = TRACKED_CSVS["computed_output_with_g"]
    if not historical_path.exists() or not computed_path.exists():
        return {
            "hybrid_rows": 0,
            "value_sources": {},
            "funnel_baujat": [],
            "forest": [],
        }

    historical_rows = read_csv_rows(historical_path)
    computed_rows = read_csv_rows(computed_path)
    hybrid_rows = reconcile_secondary_tables(historical_rows, computed_rows)

    source_counts = {
        "effect_source": {
            source: sum(1 for row in hybrid_rows if row["effect_source"] == source)
            for source in ("historical", "computed", "missing")
        },
        "variance_source": {
            source: sum(1 for row in hybrid_rows if row["variance_source"] == source)
            for source in ("historical", "computed", "missing")
        },
        "ci_source": {
            source: sum(1 for row in hybrid_rows if row["ci_source"] == source)
            for source in ("historical", "computed", "missing")
        },
    }

    funnel_baujat = []
    for etio in ("acquired", "congenital"):
        for region_type in ("cortex", "subcortex"):
            rows_effect = subset_secondary_rows(hybrid_rows, etio, region_type)
            rows_variance = subset_secondary_rows(
                hybrid_rows,
                etio,
                region_type,
                require_variance=True,
            )
            rows_ci = subset_secondary_rows(
                hybrid_rows,
                etio,
                region_type,
                require_ci=True,
            )
            funnel_baujat.append(
                {
                    "etio": etio,
                    "region_type": region_type,
                    "rows_effect": len(rows_effect),
                    "rows_variance": len(rows_variance),
                    "rows_ci": len(rows_ci),
                    "eligible_for_model": len(rows_variance) >= 2,
                    "funnel_output_exists": (
                        ROOT / "mycode-11.24" / f"funnel_{etio}_{region_type}.png"
                    ).exists(),
                    "baujat_output_exists": (
                        ROOT / "mycode-11.24" / f"baujat_{etio}_{region_type}.png"
                    ).exists(),
                }
            )

    forest = []
    for etio in ("acquired", "congenital"):
        rows_ci = forest_rows_for_group(hybrid_rows, etio)
        forest.append(
            {
                "etio": etio,
                "rows_ci": len(rows_ci),
                "eligible_for_plot": len(rows_ci) >= 1,
                "png_output_exists": (
                    ROOT / "mycode-11.24" / "forest" / f"forest_{etio}.png"
                ).exists(),
                "svg_output_exists": (
                    ROOT / "mycode-11.24" / "forest" / f"forest_{etio}.svg"
                ).exists(),
            }
        )

    return {
        "hybrid_rows": len(hybrid_rows),
        "value_sources": source_counts,
        "funnel_baujat": funnel_baujat,
        "forest": forest,
    }


def build_artifact_provenance() -> list[dict[str, object]]:
    files = [
        ROOT / "output.csv",
        ROOT / "plot_big_area_counts.png",
        ROOT / "plot_matter_counts.png",
        ROOT / "plot_side_counts.png",
        ROOT / "plot_roi_counts_top20.png",
        ROOT / "mycode-11.24" / "output.csv",
        ROOT / "mycode-11.24" / "output_with_g.csv",
        ROOT / "mycode-11.24" / "output_with_g_computed.csv",
        ROOT / "mycode-11.24" / "output_final.csv",
        ROOT / "mycode-11.24" / "jsonwithg.csv",
        ROOT / "mycode-11.24" / "brain_acquired_DK2.png",
        ROOT / "mycode-11.24" / "brainpanel_acquired_DK_cortex_only.png",
        ROOT / "mycode-11.24" / "acquired_left_lateral_DK.png",
        ROOT / "mycode-11.24" / "acquired_left_medial_DK.png",
        ROOT / "mycode-11.24" / "acquired_right_lateral_DK.png",
        ROOT / "mycode-11.24" / "acquired_right_medial_DK.png",
        ROOT / "mycode-11.24" / "acquired_subcortex_cerebellum_ASEG.png",
        ROOT / "mycode-11.24" / "funnel_acquired_cortex.png",
        ROOT / "mycode-11.24" / "funnel_acquired_subcortex.png",
        ROOT / "mycode-11.24" / "funnel_congenital_cortex.png",
        ROOT / "mycode-11.24" / "funnel_congenital_subcortex.png",
        ROOT / "mycode-11.24" / "baujat_acquired_cortex.png",
        ROOT / "mycode-11.24" / "baujat_acquired_subcortex.png",
        ROOT / "mycode-11.24" / "baujat_congenital_cortex.png",
        ROOT / "mycode-11.24" / "baujat_congenital_subcortex.png",
        ROOT / "mycode-11.24" / "forest" / "forest_acquired.png",
        ROOT / "mycode-11.24" / "forest" / "forest_acquired.svg",
        ROOT / "mycode-11.24" / "forest" / "forest_congenital.png",
        ROOT / "mycode-11.24" / "forest" / "forest_congenital.svg",
    ]

    script_outputs = {}
    for item in SCRIPT_CATALOG:
        base_dir = item["path"].parent
        for output in item["expected_outputs"]:
            script_outputs[(base_dir / output).name] = relpath(item["path"])

    provenance = []
    for path in files:
        producer = script_outputs.get(path.name)
        if path.exists() and producer:
            status = "produced by script"
        elif path.exists():
            status = "possibly produced by script"
        else:
            status = "not attributable from current evidence"
        provenance.append(
            {
                "artifact": relpath(path),
                "exists": path.exists(),
                "status": status,
                "producer": producer,
            }
        )
    return provenance


def write_markdown(summary: dict[str, object]) -> None:
    secondary = summary["secondary_plot_status"]

    lines = [
        "# Workflow Audit",
        "",
        "This file is generated by `audit_workflow.py` and summarizes the current best reconstruction of the analysis workflow.",
        "",
        "## Workflow Conclusion",
        "",
        "- The strongest historical execution branch remains `vestibular-meta-analysis/mycode-11.24`.",
        "- The verified runnable brain branch is now `output.csv -> compute_hedges_g.R -> output_with_g_computed.csv -> brain_plots_master.R`.",
        "- The preserved historical analysis table is `mycode-11.24/output_with_g.csv`.",
        "- The verified rerun table is `mycode-11.24/output_with_g_computed.csv`.",
        "- Secondary plots now use a hybrid reconciliation layer that preserves historical variance/CI values and falls back to recomputed effect sizes where needed.",
        "- `output_final.csv` remains untrusted because the merge step appears to discard populated effect-size or CI values.",
        "",
        "## Verified Runnable Branches",
        "",
        "1. Brain plots: `output.csv -> compute_hedges_g.R -> output_with_g_computed.csv -> brain_plots_master.R`.",
        "2. Secondary plots: `output_with_g.csv + output_with_g_computed.csv -> meta_plot_helpers.R -> funnel/Baujat/forest masters`.",
        "",
        "## Current Secondary-Plot Reality",
        "",
        "| Group | Effect rows | Variance rows | CI rows | Eligible for funnel/Baujat | Funnel present | Baujat present |",
        "|---|---:|---:|---:|---|---|---|",
    ]

    for item in secondary["funnel_baujat"]:
        lines.append(
            f"| `{item['etio']}/{item['region_type']}` | {item['rows_effect']} | "
            f"{item['rows_variance']} | {item['rows_ci']} | "
            f"{'yes' if item['eligible_for_model'] else 'no'} | "
            f"{'yes' if item['funnel_output_exists'] else 'no'} | "
            f"{'yes' if item['baujat_output_exists'] else 'no'} |"
        )

    lines.extend(
        [
            "",
            "| Etiology | CI rows | Eligible for forest | PNG present | SVG present |",
            "|---|---:|---|---|---|",
        ]
    )

    for item in secondary["forest"]:
        lines.append(
            f"| `{item['etio']}` | {item['rows_ci']} | "
            f"{'yes' if item['eligible_for_plot'] else 'no'} | "
            f"{'yes' if item['png_output_exists'] else 'no'} | "
            f"{'yes' if item['svg_output_exists'] else 'no'} |"
        )

    lines.extend(
        [
            "",
            "## CSV Inventory",
            "",
            "| File | Exists | Rows | Cols | Key non-null counts |",
            "|---|---:|---:|---:|---|",
        ]
    )

    for csv_summary in summary["csv_summaries"].values():
        non_null = ", ".join(
            f"{key}={value}" for key, value in csv_summary["non_null_counts"].items()
        )
        lines.append(
            f"| `{csv_summary['path']}` | {'yes' if csv_summary['exists'] else 'no'} | "
            f"{csv_summary['rows']} | {csv_summary['columns']} | {non_null} |"
        )

    historical_vs_final = summary["historical_vs_output_final"]
    historical_vs_computed = summary["historical_vs_computed"]
    lines.extend(
        [
            "",
            "## Table Comparisons",
            "",
            f"- `output_with_g.csv` vs `output_final.csv`: {historical_vs_final['changed_row_count']} rows change in tracked effect-size or CI fields.",
            f"- `output_with_g.csv` vs `output_with_g_computed.csv`: {historical_vs_computed['changed_row_count']} rows change in tracked effect-size or CI fields.",
            "- The first comparison is the main reason `output_final.csv` remains non-canonical.",
            "- The second comparison is expected because the verified rerun table is a recomputation branch, not a byte-for-byte historical replica.",
            "",
            "## Script Provenance",
            "",
            "| Script | Role | Status | Notes |",
            "|---|---|---|---|",
        ]
    )

    for item in summary["scripts"]:
        lines.append(
            f"| `{item['path']}` | {item['role']} | {item['status']} | {item['notes']} |"
        )

    lines.extend(
        [
            "",
            "## Artifact Provenance",
            "",
            "| Artifact | Exists | Status | Producer |",
            "|---|---|---|---|",
        ]
    )

    for item in summary["artifact_provenance"]:
        producer = f"`{item['producer']}`" if item["producer"] else ""
        lines.append(
            f"| `{item['artifact']}` | {'yes' if item['exists'] else 'no'} | "
            f"{item['status']} | {producer} |"
        )

    lines.extend(
        [
            "",
            "## Top-Level Adaptation Branch",
            "",
            "- `combine_all_json_to_csv.py` can regenerate a base CSV from JSON using the shared 40-column schema.",
            "- `meta_analysis_full.py` matches the committed descriptive top-level PNGs, but it expects `all_meta_rows.csv`, which is not present here.",
            "- `make_brain_panels.r` remains incomplete in its current location because it expects a local `brain_plot.R` that is not present in the top-level folder.",
            "",
            "## References",
            "",
            "- `.ref` contains the original Excel-based or desktop-path scripts that informed the newer local rewrites.",
        ]
    )

    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    csv_summaries = {
        name: summarize_csv(path)
        for name, path in TRACKED_CSVS.items()
    }

    scripts = []
    for item in SCRIPT_CATALOG:
        enriched = dict(item)
        enriched["path"] = relpath(item["path"])
        scripts.append(enriched)

    summary = {
        "generated_from": relpath(Path(__file__)),
        "csv_summaries": csv_summaries,
        "historical_vs_output_final": compare_csvs(
            TRACKED_CSVS["historical_output_with_g"],
            TRACKED_CSVS["legacy_output_final"],
        ),
        "historical_vs_computed": compare_csvs(
            TRACKED_CSVS["historical_output_with_g"],
            TRACKED_CSVS["computed_output_with_g"],
        ),
        "secondary_plot_status": current_secondary_plot_status(),
        "scripts": scripts,
        "artifact_provenance": build_artifact_provenance(),
        "conclusion": {
            "historical_branch": "vestibular-meta-analysis/mycode-11.24",
            "historical_table": "vestibular-meta-analysis/mycode-11.24/output_with_g.csv",
            "verified_rerun_table": "vestibular-meta-analysis/mycode-11.24/output_with_g_computed.csv",
            "untrusted_intermediates": [
                "vestibular-meta-analysis/jsonwithg.csv",
                "vestibular-meta-analysis/mycode-11.24/jsonwithg.csv",
                "vestibular-meta-analysis/mycode-11.24/output_final.csv",
            ],
        },
    }

    AUDIT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(summary)
    print(f"Wrote {AUDIT_MD}")
    print(f"Wrote {AUDIT_JSON}")


if __name__ == "__main__":
    main()
