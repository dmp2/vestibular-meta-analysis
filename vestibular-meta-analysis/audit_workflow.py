#!/usr/bin/env python3
"""Generate a reproducible workflow audit for vestibular-meta-analysis."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
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
    "legacy_output_with_g": ROOT / "mycode-11.24" / "output_with_g.csv",
    "legacy_output_final": ROOT / "mycode-11.24" / "output_final.csv",
    "root_jsonwithg": ROOT / "jsonwithg.csv",
    "legacy_jsonwithg": ROOT / "mycode-11.24" / "jsonwithg.csv",
}


SCRIPT_CATALOG = [
    {
        "path": ROOT / "mycode-11.24" / "compute_hedges_g.R",
        "role": "core_stage",
        "status": "produced by script",
        "notes": "Reads output.csv and writes output_with_g.csv.",
        "expected_outputs": ["output_with_g.csv"],
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
        "role": "figure",
        "status": "produced by script",
        "notes": "Creates acquired cortical DK map from output_with_g.csv.",
        "expected_outputs": ["brain_acquired_DK2.png"],
    },
    {
        "path": ROOT / "mycode-11.24" / "brainonlydk.R",
        "role": "figure",
        "status": "produced by script",
        "notes": "Creates combined cortex-only DK panel.",
        "expected_outputs": ["brainpanel_acquired_DK_cortex_only.png"],
    },
    {
        "path": ROOT / "mycode-11.24" / "braint3.R",
        "role": "figure",
        "status": "produced by script",
        "notes": "Creates four cortical hemisphere views plus one subcortex/cerebellum PNG.",
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
        "role": "figure",
        "status": "possibly produced by script",
        "notes": "Configured to create brainpanel_acquired_DK_ASEG.png, but that output is not currently present.",
        "expected_outputs": ["brainpanel_acquired_DK_ASEG.png"],
    },
    {
        "path": ROOT / "mycode-11.24" / "funnel.r",
        "role": "figure",
        "status": "possibly produced by script",
        "notes": "Generates etiology-based funnel plots from output_with_g.csv, but no matching funnel PNGs are present locally.",
        "expected_outputs": [],
    },
    {
        "path": ROOT / "mycode-11.24" / "funnelt2.R",
        "role": "figure",
        "status": "possibly produced by script",
        "notes": "Generates four region-specific funnel plots, but no matching outputs are present locally.",
        "expected_outputs": [
            "funnel_acquired_cortex.png",
            "funnel_acquired_subcortex.png",
            "funnel_congenital_cortex.png",
            "funnel_congenital_subcortex.png",
        ],
    },
    {
        "path": ROOT / "mycode-11.24" / "forest.py",
        "role": "figure",
        "status": "not attributable from current evidence",
        "notes": "Template script with placeholder paths. No local forest outputs are present.",
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


@dataclass
class CsvSummary:
    path: str
    exists: bool
    rows: int = 0
    columns: int = 0
    non_null_counts: dict[str, int] | None = None


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def summarize_csv(path: Path) -> CsvSummary:
    if not path.exists():
        return CsvSummary(path=relpath(path), exists=False)

    rows = read_csv_rows(path)
    fields = list(rows[0].keys()) if rows else []
    non_null_counts = {}
    for col in CSV_KEY_COLUMNS:
        if col in fields:
            count = sum(1 for row in rows if (row.get(col) or "").strip() not in {"", "NA", "NaN", "nan"})
            non_null_counts[col] = count
    return CsvSummary(
        path=relpath(path),
        exists=True,
        rows=len(rows),
        columns=len(fields),
        non_null_counts=non_null_counts,
    )


def relpath(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def compare_csvs(left: Path, right: Path) -> dict[str, object]:
    left_rows = read_csv_rows(left)
    right_rows = read_csv_rows(right)
    changed_rows = []
    fields_to_compare = [
        "Study_ID",
        "ROI_Homogenized",
        "Hedges_g_exact",
        "Hedges_g_variance",
        "CI_lower",
        "CI_upper",
    ]

    for index, (left_row, right_row) in enumerate(zip(left_rows, right_rows)):
        differences = {}
        for field in fields_to_compare:
            if (left_row.get(field) or "") != (right_row.get(field) or ""):
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


def extract_declared_paths(script_path: Path) -> dict[str, list[str]]:
    text = script_path.read_text(encoding="utf-8", errors="replace")
    inputs = sorted(set(re.findall(r'(?i)(?:input_file|DATA_FILE)\s*[:=<-]+\s*[r"]*"([^"\n]+(?:csv|xlsx|json))"', text)))
    outputs = sorted(set(re.findall(r'(?i)(?:output_file|OUTPUT_PNG|output_png)\s*[:=<-]+\s*[r"]*"([^"\n]+(?:csv|png|svg|pdf))"', text)))
    saves = sorted(set(re.findall(r'(?i)([A-Za-z0-9_\-]+(?:\.png|\.svg|\.pdf|\.csv))', text)))
    return {
        "declared_inputs": inputs,
        "declared_output_vars": outputs,
        "mentioned_output_like_names": saves,
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
        ROOT / "mycode-11.24" / "output_final.csv",
        ROOT / "mycode-11.24" / "jsonwithg.csv",
        ROOT / "mycode-11.24" / "brain_acquired_DK2.png",
        ROOT / "mycode-11.24" / "brainpanel_acquired_DK_cortex_only.png",
        ROOT / "mycode-11.24" / "acquired_left_lateral_DK.png",
        ROOT / "mycode-11.24" / "acquired_left_medial_DK.png",
        ROOT / "mycode-11.24" / "acquired_right_lateral_DK.png",
        ROOT / "mycode-11.24" / "acquired_right_medial_DK.png",
        ROOT / "mycode-11.24" / "acquired_subcortex_cerebellum_ASEG.png",
    ]
    script_outputs = {
        output: relpath(item["path"])
        for item in SCRIPT_CATALOG
        for output in item["expected_outputs"]
    }

    provenance = []
    for path in files:
        name = path.name
        if not path.exists():
            status = "not attributable from current evidence"
            producer = None
        elif name in script_outputs:
            status = "produced by script"
            producer = script_outputs[name]
        else:
            status = "possibly produced by script"
            producer = None
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
    lines = [
        "# Workflow Audit",
        "",
        "This file is generated by `audit_workflow.py` and summarizes the current best reconstruction of the analysis workflow.",
        "",
        "## Workflow Conclusion",
        "",
        "- The strongest historical execution branch is `vestibular-meta-analysis/mycode-11.24`.",
        "- `output.csv` is the precursor table and `output_with_g.csv` is the provisional source-of-truth analysis table.",
        "- `output_final.csv` remains untrusted because the merge step appears to discard some populated effect-size or CI values.",
        "- The top-level Python/R scripts are newer adaptations; only the descriptive top-level PNGs are directly attributable from current files.",
        "",
        "## Likely Historical Pipeline",
        "",
        "1. `output.csv` assembled from manual extraction and/or JSON-derived rows.",
        "2. `mycode-11.24/compute_hedges_g.R` computed or filled `Hedges_g_exact` and `Hedges_g_variance`, producing `output_with_g.csv`.",
        "3. Figure scripts consumed `output_with_g.csv` to produce the current brain-map outputs.",
        "4. `merge_json_into_master.R` later attempted a JSON-based merge into `output_final.csv`, but that step is not considered canonical.",
        "",
        "## CSV Inventory",
        "",
        "| File | Exists | Rows | Cols | Key non-null counts |",
        "|---|---:|---:|---:|---|",
    ]

    for name, csv_summary in summary["csv_summaries"].items():
        non_null = ", ".join(f"{key}={value}" for key, value in (csv_summary["non_null_counts"] or {}).items())
        lines.append(
            f"| `{csv_summary['path']}` | {'yes' if csv_summary['exists'] else 'no'} | "
            f"{csv_summary['rows']} | {csv_summary['columns']} | {non_null} |"
        )

    comparison = summary["output_with_g_vs_output_final"]
    lines.extend(
        [
            "",
            "## `output_with_g.csv` vs `output_final.csv`",
            "",
            f"- Row counts are stable: {comparison['row_count_left']} vs {comparison['row_count_right']}.",
            f"- Rows with at least one changed tracked field: {comparison['changed_row_count']}.",
            "- Sample differences show missing values in `output_final.csv` where `output_with_g.csv` contains populated effect sizes or confidence bounds.",
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
            "| Artifact | Status | Producer |",
            "|---|---|---|",
        ]
    )

    for item in summary["artifact_provenance"]:
        producer = f"`{item['producer']}`" if item["producer"] else ""
        lines.append(f"| `{item['artifact']}` | {item['status']} | {producer} |")

    lines.extend(
        [
            "",
            "## Top-Level Adaptation Branch",
            "",
            "- `combine_all_json_to_csv.py` can regenerate a base CSV from a JSON folder using the shared 40-column schema.",
            "- `meta_analysis_full.py` clearly matches the committed descriptive PNGs, but it expects `all_meta_rows.csv`, which is not present in this directory.",
            "- `make_brain_panels.r` is incomplete in its current location because it sources `brain_plot.R`, which is only present under `.ref/brain plot/brain_plot.R`.",
            "",
            "## References",
            "",
            "- `.ref` contains Excel-based antecedent scripts and examples that appear to be the conceptual source for the newer local rewrites.",
        ]
    )

    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    csv_summaries = {
        name: summarize_csv(path).__dict__
        for name, path in TRACKED_CSVS.items()
    }
    output_compare = compare_csvs(
        TRACKED_CSVS["legacy_output_with_g"],
        TRACKED_CSVS["legacy_output_final"],
    )

    scripts = []
    for item in SCRIPT_CATALOG:
        enriched = dict(item)
        enriched["path"] = relpath(item["path"])
        enriched["declared_paths"] = extract_declared_paths(item["path"])
        scripts.append(enriched)

    summary = {
        "generated_from": relpath(Path(__file__)),
        "csv_summaries": csv_summaries,
        "output_with_g_vs_output_final": output_compare,
        "scripts": scripts,
        "artifact_provenance": build_artifact_provenance(),
        "conclusion": {
            "historical_branch": "vestibular-meta-analysis/mycode-11.24",
            "provisional_source_of_truth": "vestibular-meta-analysis/mycode-11.24/output_with_g.csv",
            "untrusted_intermediates": [
                "jsonwithg.csv",
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
