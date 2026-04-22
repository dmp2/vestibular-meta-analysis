#!/usr/bin/env python3
"""Validate the reconstructed vestibular-meta-analysis workflow.

This validator is intentionally conservative:

- it does not rewrite any CSVs
- it derives grouping fields at runtime from the reconciled secondary table
- it keeps cohort-design signal via ``Cohort_Contrast`` instead of assuming
  every row is a simple disease-vs-control comparison
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LEGACY_DIR = ROOT / "mycode-11.24"
FOREST_DIR = LEGACY_DIR / "forest"
VALIDATION_JSON = ROOT / "validation_summary.json"

FUNNEL_BAUJAT_GROUP_FIELD = "Review_Group"
FOREST_GROUP_FIELD = "Condition_Normalized"

REQUIRED_COLUMNS = [
    "Study_ID",
    "Author",
    "Year",
    "Title",
    "Etiology",
    "Congenital_or_Acquired",
    "Sample_Size_Patients",
    "Sample_Size_Controls",
    "Hedges_g_exact",
    "Hedges_g_variance",
    "CI_lower",
    "CI_upper",
    "ROI_Homogenized",
    "Big_Area",
    "Matter",
    "Side",
    "Measure",
]

CSV_PATHS = {
    "top_output": ROOT / "output.csv",
    "legacy_output": LEGACY_DIR / "output.csv",
    "historical_output_with_g": LEGACY_DIR / "output_with_g.csv",
    "computed_output_with_g": LEGACY_DIR / "output_with_g_computed.csv",
    "legacy_output_final": LEGACY_DIR / "output_final.csv",
    "root_jsonwithg": ROOT / "jsonwithg.csv",
    "legacy_jsonwithg": LEGACY_DIR / "jsonwithg.csv",
}

SCRIPT_PATHS = {
    "compute": LEGACY_DIR / "compute_hedges_g.R",
    "brain_master": ROOT / "brain_plots_master.R",
    "brain_runner": ROOT / "run_brain_plot_pipeline.R",
    "meta_helpers": ROOT / "meta_plot_helpers.R",
    "funnel_master": ROOT / "funnel_plots_master.R",
    "baujat_master": ROOT / "baujat_plots_master.R",
    "forest_master": ROOT / "forest_plots_master.R",
    "audit_workflow": ROOT / "audit_workflow.py",
}

BRAIN_OUTPUTS = [
    LEGACY_DIR / "brain_acquired_DK2.png",
    LEGACY_DIR / "brainpanel_acquired_DK_cortex_only.png",
    LEGACY_DIR / "acquired_left_lateral_DK.png",
    LEGACY_DIR / "acquired_left_medial_DK.png",
    LEGACY_DIR / "acquired_right_lateral_DK.png",
    LEGACY_DIR / "acquired_right_medial_DK.png",
    LEGACY_DIR / "acquired_subcortex_cerebellum_ASEG.png",
]

DK_PATTERNS = [
    r"anterior cingulate cortex",
    r"cingulate gyrus",
    r"cuneus",
    r"fusiform gyrus",
    r"fusiform",
    r"insula",
    r"intracalcarine cortex",
    r"intracalcarine",
    r"lingual gyrus",
    r"lateral occipital cortex",
    r"lateral occipital",
    r"middle frontal gyrus",
    r"middle temporal gyrus \(mt/v5\)",
    r"middle temporal visual area \(mt/v5\)",
    r"middle temporal gyrus",
    r"^mt/v5$",
    r"postcentral gyrus",
    r"precentral gyrus",
    r"precuneus / superior parietal white matter",
    r"precuneus",
    r"superior frontal gyrus",
    r"superior orbitofrontal cortex",
    r"superior orbitofrontal",
    r"orbital gyrus",
    r"superior temporal gyrus",
    r"primary somatosensory cortex",
    r"supramarginal gyrus",
]

SUB_PATTERNS = [
    r"hippocampus",
    r"parahippocamp",
    r"presubiculum",
    r"amygdala",
    r"caudate",
    r"putamen",
    r"pallid",
    r"accumb",
    r"thalam",
    r"brainstem",
    r"pons",
    r"mesencephalon",
    r"midbrain",
    r"pontomesencephalic",
    r"vestibular nuclei",
    r"gracile nucleus",
    r"cerebell",
    r"vermi",
    r"culmen",
    r"peduncle",
    r"inferior semi-lunar lobule",
    r"crus i",
    r"lobule vi",
]


def has_value(value: object) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return bool(text) and text.lower() not in {"na", "nan"}


def clean_key_part(value: object) -> str:
    return str(value).strip() if has_value(value) else ""


def normalize_space(text: object) -> str:
    return re.sub(r"\s+", " ", str(text).strip())


def normalize_lower(text: object) -> str:
    return normalize_space(text).lower()


def safe_slug(text: object) -> str:
    ascii_text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_text.lower()).strip("_")
    return slug or "unknown"


def composite_key(row: dict[str, str]) -> str:
    return "||".join(
        [
            clean_key_part(row.get("Study_ID")),
            clean_key_part(row.get("ROI_Homogenized")),
            clean_key_part(row.get("Side")),
            clean_key_part(row.get("Measure")),
        ]
    )


def read_csv_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = [{key: (value if value is not None else "") for key, value in row.items()} for row in reader]
        return rows, list(reader.fieldnames or [])


def summarize_csv(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"path": str(path.relative_to(ROOT.parent)), "exists": False}

    rows, fieldnames = read_csv_table(path)
    non_null_counts = {
        column: sum(1 for row in rows if has_value(row.get(column)))
        for column in [
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
    }
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    return {
        "path": str(path.relative_to(ROOT.parent)),
        "exists": True,
        "rows": len(rows),
        "columns": len(fieldnames),
        "missing_required_columns": missing_columns,
        "non_null_counts": non_null_counts,
    }


def prefer_value(primary: str, secondary: str) -> str:
    if has_value(primary):
        return primary
    if has_value(secondary):
        return secondary
    return ""


def source_of_value(primary: str, secondary: str, primary_name: str, secondary_name: str) -> str:
    if has_value(primary):
        return primary_name
    if has_value(secondary):
        return secondary_name
    return "missing"


def normalize_etiology_value(value: str) -> str:
    return normalize_lower(value)


def derive_condition_normalized(etiology_clean: str, etiology_raw: str) -> str:
    if re.search(r"acute unilateral peripheral vestibular neuritis|vestibular neuritis", etiology_clean):
        return "Vestibular neuritis"
    if etiology_clean == "post-concussive vestibular dysfunction":
        return "Post-concussive vestibular dysfunction"
    if etiology_clean == "mild traumatic brain injury with vestibular symptoms":
        return "Mild traumatic brain injury with vestibular symptoms"
    if "sports-related concussion" in etiology_clean:
        return "Sports-related concussion with persistent post-concussive symptoms"
    if etiology_clean == "bilateral vestibular loss":
        return "Bilateral vestibular loss"
    if etiology_clean == "bilateral vestibular failure":
        return "Bilateral vestibular failure"
    if etiology_clean == "bilateral vestibulopathy":
        return "Bilateral vestibulopathy"
    if "neurofibromatosis 2" in etiology_clean:
        return "NF2 bilateral vestibular loss after neurectomy"
    if re.search(r"acoustic neuroma surgery|acoustic neurinoma surgery|vestibular schwannoma removal", etiology_clean):
        return "Unilateral vestibular deafferentation after vestibular schwannoma surgery"
    if etiology_clean == "peripheral vestibular dysfunction":
        return "Peripheral vestibular dysfunction"
    if any(token in etiology_clean for token in ["méni", "meni", "mã©ni"]):
        return "Meniere's disease"
    if etiology_clean == "persistent postural perceptual dizziness":
        return "Persistent postural perceptual dizziness"
    if etiology_clean == "long-term vestibular adaptation in professional ballet dancers":
        return "Professional ballet dancers"
    if "vestibular migraine" in etiology_clean:
        return "Vestibular migraine"
    if any(token in etiology_clean for token in ["small-vessel", "small vessel", "white matter disease"]):
        return "White matter disease or small-vessel lesions"
    if re.search(r"stroke|ischemi", etiology_clean):
        return "Stroke or ischemic vestibular-circuit lesions"
    if any(token in etiology_clean for token in ["spaceflight", "microgravity", "astronaut"]):
        return "Spaceflight-related vestibular adaptation"
    if any(token in etiology_clean for token in ["healthy adults", "healthy older", "healthy younger", "older adults", "younger adults", "aging"]):
        return "Healthy aging"
    return etiology_raw.strip() if has_value(etiology_raw) else "Unclassified or needs review"


def derive_review_group(condition_normalized: str) -> str:
    if condition_normalized == "Vestibular neuritis":
        return "Unilateral vestibular loss or deafferentation"
    if condition_normalized in {
        "Post-concussive vestibular dysfunction",
        "Mild traumatic brain injury with vestibular symptoms",
        "Sports-related concussion with persistent post-concussive symptoms",
    }:
        return "Post-traumatic or concussive vestibulopathy"
    if condition_normalized in {
        "Bilateral vestibular loss",
        "Bilateral vestibular failure",
        "Bilateral vestibulopathy",
    }:
        return "Bilateral vestibulopathy"
    if condition_normalized in {
        "NF2 bilateral vestibular loss after neurectomy",
        "Unilateral vestibular deafferentation after vestibular schwannoma surgery",
    }:
        return "Vestibular schwannoma resection"
    if condition_normalized == "Peripheral vestibular dysfunction":
        return "Chronic or mild vestibulopathy"
    if condition_normalized == "Meniere's disease":
        return "Meniere's disease"
    if condition_normalized == "Vestibular migraine":
        return "Vestibular migraine"
    if condition_normalized == "White matter disease or small-vessel lesions":
        return "White matter disease or small-vessel lesions"
    if condition_normalized == "Stroke or ischemic vestibular-circuit lesions":
        return "Stroke or ischemic vestibular-circuit lesions"
    if condition_normalized == "Professional ballet dancers":
        return "Vestibular experts"
    if condition_normalized == "Healthy aging":
        return "Healthy aging"
    if condition_normalized == "Spaceflight-related vestibular adaptation":
        return "Spaceflight-related vestibular adaptation"
    if condition_normalized == "Persistent postural perceptual dizziness":
        return "Other vestibular clinical cohorts"
    return "Unclassified or needs review"


def derive_condition_family(condition_normalized: str, review_group: str) -> str:
    if condition_normalized in {"Vestibular neuritis", "Peripheral vestibular dysfunction"}:
        return "Unilateral peripheral vestibular syndromes"
    if review_group == "Post-traumatic or concussive vestibulopathy":
        return "Concussion-related vestibulopathy"
    if condition_normalized in {"Bilateral vestibular loss", "Bilateral vestibular failure", "Bilateral vestibulopathy"}:
        return "Bilateral vestibular syndromes"
    if review_group == "Vestibular schwannoma resection":
        return "Vestibular schwannoma resection or deafferentation"
    if condition_normalized == "Meniere's disease":
        return "Meniere's disease"
    if condition_normalized == "Persistent postural perceptual dizziness":
        return "Functional vestibular disorders"
    if review_group in {"Vestibular experts", "Healthy aging", "Spaceflight-related vestibular adaptation"}:
        return "Adaptive or non-clinical cohorts"
    if condition_normalized == "Vestibular migraine":
        return "Vestibular migraine"
    if review_group in {"White matter disease or small-vessel lesions", "Stroke or ischemic vestibular-circuit lesions"}:
        return "Central vascular or white-matter vestibular disorders"
    return review_group


def derive_cohort_contrast(review_group: str, n_patients: str, n_controls: str) -> str:
    both_sample_sizes = has_value(n_patients) and has_value(n_controls)
    if review_group == "Vestibular experts":
        return "expertise_vs_control"
    if review_group == "Healthy aging":
        return "healthy_subgroup_comparison"
    if review_group == "Spaceflight-related vestibular adaptation":
        return "adaptation_or_exposure_comparison"
    if both_sample_sizes:
        return "clinical_vs_control_style"
    return "unclear_or_nonstandard"


def attach_region_membership(row: dict[str, str]) -> None:
    roi_clean = normalize_lower(row.get("ROI_Homogenized", ""))
    row["ROI_clean"] = roi_clean
    row["has_dk_region"] = any(re.search(pattern, roi_clean) for pattern in DK_PATTERNS)
    row["has_sub_label"] = any(re.search(pattern, roi_clean) for pattern in SUB_PATTERNS)


def derive_grouping_fields(row: dict[str, str]) -> None:
    etiology_clean = normalize_etiology_value(row.get("Etiology", ""))
    row["Etiology_clean"] = etiology_clean
    row["Condition_Normalized"] = derive_condition_normalized(etiology_clean, row.get("Etiology", ""))
    row["Review_Group"] = derive_review_group(row["Condition_Normalized"])
    row["Condition_Family"] = derive_condition_family(row["Condition_Normalized"], row["Review_Group"])
    row["Cohort_Contrast"] = derive_cohort_contrast(
        row["Review_Group"],
        row.get("Sample_Size_Patients", ""),
        row.get("Sample_Size_Controls", ""),
    )


def prepare_single_source_meta(rows: list[dict[str, str]], source_name: str) -> list[dict[str, str]]:
    prepared: list[dict[str, str]] = []
    for row in rows:
        clone = dict(row)
        clone[".merge_key"] = composite_key(clone)
        clone["effect_source"] = source_of_value(clone.get("Hedges_g_exact", ""), "", source_name, "missing")
        clone["variance_source"] = source_of_value(clone.get("Hedges_g_variance", ""), "", source_name, "missing")
        clone["ci_source"] = source_name if has_value(clone.get("CI_lower")) and has_value(clone.get("CI_upper")) else "missing"
        derive_grouping_fields(clone)
        attach_region_membership(clone)
        prepared.append(clone)
    return prepared


def reconcile_secondary_tables(
    historical_rows: list[dict[str, str]],
    computed_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, object]]:
    historical_by_key = {composite_key(row): row for row in historical_rows}
    computed_by_key = {composite_key(row): row for row in computed_rows}

    historical_keys = set(historical_by_key)
    computed_keys = set(computed_by_key)
    all_keys = sorted(historical_keys | computed_keys)

    summary = {
        "historical_row_count": len(historical_rows),
        "computed_row_count": len(computed_rows),
        "historical_key_count": len(historical_keys),
        "computed_key_count": len(computed_keys),
        "missing_in_computed_count": len(historical_keys - computed_keys),
        "missing_in_historical_count": len(computed_keys - historical_keys),
        "missing_in_computed_sample": sorted(historical_keys - computed_keys)[:5],
        "missing_in_historical_sample": sorted(computed_keys - historical_keys)[:5],
    }

    reconciled: list[dict[str, str]] = []
    for key in all_keys:
        historical = historical_by_key.get(key, {})
        computed = computed_by_key.get(key, {})
        merged: dict[str, str] = {".merge_key": key}

        for column in REQUIRED_COLUMNS:
            if column in historical or column in computed:
                merged[column] = prefer_value(historical.get(column, ""), computed.get(column, ""))

        all_columns = set(historical) | set(computed)
        for column in all_columns:
            if column == ".merge_key":
                continue
            merged.setdefault(column, prefer_value(historical.get(column, ""), computed.get(column, "")))

        merged["effect_source"] = source_of_value(
            historical.get("Hedges_g_exact", ""),
            computed.get("Hedges_g_exact", ""),
            "historical",
            "computed",
        )
        merged["variance_source"] = source_of_value(
            historical.get("Hedges_g_variance", ""),
            computed.get("Hedges_g_variance", ""),
            "historical",
            "computed",
        )
        merged["ci_source"] = (
            "historical"
            if has_value(historical.get("CI_lower")) and has_value(historical.get("CI_upper"))
            else "computed"
            if has_value(computed.get("CI_lower")) and has_value(computed.get("CI_upper"))
            else "missing"
        )
        derive_grouping_fields(merged)
        attach_region_membership(merged)
        reconciled.append(merged)

    return reconciled, summary


def filter_rows(
    rows: list[dict[str, str]],
    *,
    group_field: str,
    group_value: str,
    region_type: str | None = None,
    require_variance: bool = False,
    require_ci: bool = False,
) -> list[dict[str, str]]:
    filtered = [
        row
        for row in rows
        if row.get(group_field) == group_value and has_value(row.get("Hedges_g_exact"))
    ]
    if region_type == "cortex":
        filtered = [row for row in filtered if row.get("has_dk_region")]
    elif region_type == "subcortex":
        filtered = [row for row in filtered if row.get("has_sub_label")]

    if require_variance:
        filtered = [row for row in filtered if has_value(row.get("Hedges_g_variance"))]
    if require_ci:
        filtered = [
            row for row in filtered if has_value(row.get("CI_lower")) and has_value(row.get("CI_upper"))
        ]
    return filtered


def summarize_secondary_eligibility(rows: list[dict[str, str]], group_field: str) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    group_values = sorted({row.get(group_field, "") for row in rows if has_value(row.get(group_field, ""))})
    for group_value in group_values:
        for region_type in ("cortex", "subcortex"):
            effect_rows = filter_rows(rows, group_field=group_field, group_value=group_value, region_type=region_type)
            variance_rows = filter_rows(
                rows,
                group_field=group_field,
                group_value=group_value,
                region_type=region_type,
                require_variance=True,
            )
            ci_rows = filter_rows(
                rows,
                group_field=group_field,
                group_value=group_value,
                region_type=region_type,
                require_ci=True,
            )
            summaries.append(
                {
                    "group_field": group_field,
                    "group_value": group_value,
                    "region_type": region_type,
                    "rows_effect": len(effect_rows),
                    "rows_variance": len(variance_rows),
                    "rows_ci": len(ci_rows),
                    "review_group": group_value if group_field == "Review_Group" else (effect_rows[0]["Review_Group"] if effect_rows else ""),
                    "condition_family": effect_rows[0]["Condition_Family"] if effect_rows else "",
                    "cohort_contrast": effect_rows[0]["Cohort_Contrast"] if effect_rows else "",
                }
            )
    return summaries


def summarize_forest_eligibility(rows: list[dict[str, str]], group_field: str) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    group_values = sorted({row.get(group_field, "") for row in rows if has_value(row.get(group_field, ""))})
    for group_value in group_values:
        eligible = [
            row
            for row in rows
            if row.get(group_field) == group_value
            and has_value(row.get("Hedges_g_exact"))
            and has_value(row.get("CI_lower"))
            and has_value(row.get("CI_upper"))
        ]
        first = eligible[0] if eligible else next((row for row in rows if row.get(group_field) == group_value), {})
        summaries.append(
            {
                "group_field": group_field,
                "group_value": group_value,
                "rows_ci": len(eligible),
                "review_group": first.get("Review_Group", ""),
                "condition_family": first.get("Condition_Family", ""),
                "cohort_contrast": first.get("Cohort_Contrast", ""),
            }
        )
    return summaries


def output_records_for_secondary(
    secondary_eligibility: list[dict[str, object]],
    forest_eligibility: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    funnel_records: list[dict[str, object]] = []
    baujat_records: list[dict[str, object]] = []
    for item in secondary_eligibility:
        filename = f"{safe_slug(item['group_field'])}_{safe_slug(item['group_value'])}_{item['region_type']}.png"
        funnel_path = LEGACY_DIR / f"funnel_{filename}"
        baujat_path = LEGACY_DIR / f"baujat_{filename}"
        should_exist = item["rows_variance"] >= 2

        funnel_records.append(
            {
                **item,
                "output": str(funnel_path.relative_to(ROOT.parent)),
                "should_exist": should_exist,
                "exists": funnel_path.exists(),
            }
        )
        baujat_records.append(
            {
                **item,
                "output": str(baujat_path.relative_to(ROOT.parent)),
                "should_exist": should_exist,
                "exists": baujat_path.exists(),
            }
        )

    forest_records: list[dict[str, object]] = []
    for item in forest_eligibility:
        base = FOREST_DIR / f"forest_{safe_slug(item['group_field'])}_{safe_slug(item['group_value'])}"
        should_exist = item["rows_ci"] >= 1
        forest_records.append(
            {
                **item,
                "outputs": [
                    str((base.with_suffix(".png")).relative_to(ROOT.parent)),
                    str((base.with_suffix(".svg")).relative_to(ROOT.parent)),
                ],
                "should_exist": should_exist,
                "png_exists": base.with_suffix(".png").exists(),
                "svg_exists": base.with_suffix(".svg").exists(),
            }
        )

    return {"funnel": funnel_records, "baujat": baujat_records, "forest": forest_records}


def count_by(rows: list[dict[str, str]], field: str) -> list[dict[str, object]]:
    counts = Counter(row.get(field, "") for row in rows if has_value(row.get(field, "")))
    return [{"value": key, "count": counts[key]} for key in sorted(counts)]


def summarize_cohort_signal(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        condition = row.get("Condition_Normalized", "")
        if not has_value(condition):
            continue
        grouped[condition][row.get("Cohort_Contrast", "unclear_or_nonstandard")] += 1

    output: list[dict[str, object]] = []
    for condition in sorted(grouped):
        for contrast, count in sorted(grouped[condition].items()):
            output.append(
                {
                    "condition_normalized": condition,
                    "cohort_contrast": contrast,
                    "rows": count,
                }
            )
    return output


def print_csv_summary(csv_summaries: dict[str, dict[str, object]]) -> None:
    print("CSV summaries:")
    for name, summary in csv_summaries.items():
        if not summary["exists"]:
            print(f"  - {name}: missing")
            continue
        print(
            f"  - {name}: rows={summary['rows']}, cols={summary['columns']}, "
            f"effect={summary['non_null_counts']['Hedges_g_exact']}, "
            f"variance={summary['non_null_counts']['Hedges_g_variance']}, "
            f"ci={summary['non_null_counts']['CI_lower']}"
        )


def print_group_summary(
    secondary_eligibility: list[dict[str, object]],
    forest_eligibility: list[dict[str, object]],
) -> None:
    print("")
    print("Secondary-plot eligibility:")
    for item in secondary_eligibility:
        print(
            "  - "
            f"{item['group_value']} / {item['region_type']}: "
            f"effect={item['rows_effect']}, variance={item['rows_variance']}, ci={item['rows_ci']}"
        )

    print("")
    print("Forest eligibility:")
    for item in forest_eligibility:
        print(
            "  - "
            f"{item['group_value']}: rows_ci={item['rows_ci']}, "
            f"review_group={item['review_group']}, "
            f"contrast={item['cohort_contrast']}"
        )


def print_output_summary(outputs: dict[str, list[dict[str, object]]]) -> None:
    print("")
    print("Expected outputs under current grouped workflow:")
    for stage in ("funnel", "baujat"):
        print(f"  {stage}:")
        for item in outputs[stage]:
            if item["should_exist"]:
                status = "present" if item["exists"] else "missing"
                print(f"    - {item['output']} [{status}]")
    print("  forest:")
    for item in outputs["forest"]:
        if item["should_exist"]:
            png_status = "present" if item["png_exists"] else "missing"
            svg_status = "present" if item["svg_exists"] else "missing"
            print(f"    - {item['outputs'][0]} [{png_status}]")
            print(f"    - {item['outputs'][1]} [{svg_status}]")


def main() -> None:
    csv_summaries = {name: summarize_csv(path) for name, path in CSV_PATHS.items()}
    scripts = {
        name: {
            "path": str(path.relative_to(ROOT.parent)),
            "exists": path.exists(),
        }
        for name, path in SCRIPT_PATHS.items()
    }
    brain_outputs = [
        {
            "path": str(path.relative_to(ROOT.parent)),
            "exists": path.exists(),
        }
        for path in BRAIN_OUTPUTS
    ]

    issues: list[str] = []
    historical_path = CSV_PATHS["historical_output_with_g"]
    computed_path = CSV_PATHS["computed_output_with_g"]

    if not historical_path.exists() or not computed_path.exists():
        if not historical_path.exists():
            issues.append(f"Missing historical secondary table: {historical_path}")
        if not computed_path.exists():
            issues.append(f"Missing computed secondary table: {computed_path}")
        payload = {
            "generated_from": str(Path(__file__).relative_to(ROOT.parent)),
            "csv_summaries": csv_summaries,
            "scripts": scripts,
            "brain_outputs": brain_outputs,
            "issues": issues,
        }
        VALIDATION_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print_csv_summary(csv_summaries)
        print("")
        print("Validation halted because required secondary tables are missing.")
        for issue in issues:
            print(f"  - {issue}")
        print("")
        print(f"Wrote {VALIDATION_JSON.relative_to(ROOT.parent)}")
        return

    historical_rows, historical_fields = read_csv_table(historical_path)
    computed_rows, computed_fields = read_csv_table(computed_path)

    missing_hist_cols = [column for column in REQUIRED_COLUMNS if column not in historical_fields]
    missing_comp_cols = [column for column in REQUIRED_COLUMNS if column not in computed_fields]
    if missing_hist_cols:
        issues.append(f"Historical table missing columns: {', '.join(missing_hist_cols)}")
    if missing_comp_cols:
        issues.append(f"Computed table missing columns: {', '.join(missing_comp_cols)}")

    reconciled_rows, reconciliation = reconcile_secondary_tables(historical_rows, computed_rows)
    if reconciliation["missing_in_computed_count"] or reconciliation["missing_in_historical_count"]:
        issues.append("Historical and computed secondary tables do not have identical composite-key coverage.")

    secondary_eligibility = summarize_secondary_eligibility(reconciled_rows, FUNNEL_BAUJAT_GROUP_FIELD)
    forest_eligibility = summarize_forest_eligibility(reconciled_rows, FOREST_GROUP_FIELD)
    outputs = output_records_for_secondary(secondary_eligibility, forest_eligibility)

    payload = {
        "generated_from": str(Path(__file__).relative_to(ROOT.parent)),
        "csv_summaries": csv_summaries,
        "scripts": scripts,
        "brain_outputs": brain_outputs,
        "reconciliation": reconciliation,
        "grouping_fields": {
            "funnel_baujat_group_field": FUNNEL_BAUJAT_GROUP_FIELD,
            "forest_group_field": FOREST_GROUP_FIELD,
            "preserve_cohort_signal_via": "Cohort_Contrast",
        },
        "value_sources": {
            "effect_source_counts": count_by(reconciled_rows, "effect_source"),
            "variance_source_counts": count_by(reconciled_rows, "variance_source"),
            "ci_source_counts": count_by(reconciled_rows, "ci_source"),
        },
        "grouping_inventory": {
            "review_group_counts": count_by(reconciled_rows, "Review_Group"),
            "condition_normalized_counts": count_by(reconciled_rows, "Condition_Normalized"),
            "condition_family_counts": count_by(reconciled_rows, "Condition_Family"),
            "cohort_contrast_counts": count_by(reconciled_rows, "Cohort_Contrast"),
            "cohort_signal_by_condition": summarize_cohort_signal(reconciled_rows),
        },
        "secondary_plot_eligibility": {
            "funnel_and_baujat": secondary_eligibility,
            "forest": forest_eligibility,
        },
        "expected_outputs": outputs,
        "issues": issues,
    }

    VALIDATION_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print_csv_summary(csv_summaries)
    print("")
    print("Derived grouping fields:")
    print(f"  - funnel/Baujat: {FUNNEL_BAUJAT_GROUP_FIELD}")
    print(f"  - forest: {FOREST_GROUP_FIELD}")
    print("  - cohort-design signal retained in: Cohort_Contrast")
    print_group_summary(secondary_eligibility, forest_eligibility)
    print_output_summary(outputs)

    if issues:
        print("")
        print("Issues:")
        for issue in issues:
            print(f"  - {issue}")

    print("")
    print(f"Wrote {VALIDATION_JSON.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
