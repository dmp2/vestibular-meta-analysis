#!/usr/bin/env python3
"""
Build a study-level crosswalk between the source workbook review frame and the
current scientific grouping audit used by the checked-in workflow.

Outputs:
- workbook_review_frame_crosswalk.csv
- WORKBOOK_REVIEW_FRAME_AUDIT.md
"""

from __future__ import annotations

import csv
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


REPO_DIR = Path(__file__).resolve().parent
WORKBOOK_PATH = Path(
    r"C:\Users\dpado\Documents\jhu\Oto-HNS\meta_analysis\meta_analysis_vestibular_gm_wm.xlsx"
)
CURRENT_DECISIONS_PATH = REPO_DIR / "scientific_grouping_decisions.csv"
OUTPUT_CSV_PATH = REPO_DIR / "workbook_review_frame_crosswalk.csv"
OUTPUT_MD_PATH = REPO_DIR / "WORKBOOK_REVIEW_FRAME_AUDIT.md"

CURRENT_REVIEW_GROUPS = {
    "Bilateral vestibulopathy",
    "Unilateral vestibular loss or deafferentation",
    "Meniere's disease",
    "Vestibular migraine",
    "Post-traumatic or concussive vestibulopathy",
    "White matter disease or small-vessel lesions",
    "Stroke or ischemic vestibular-circuit lesions",
    "Chronic or mild vestibulopathy",
    "Vestibular experts",
    "Healthy non-clinical cohorts",
    "Healthy aging",
    "Spaceflight-related vestibular adaptation",
    "Vestibular schwannoma resection",
    "Other vestibular clinical cohorts",
    "Unclassified or needs review",
}

STATUS_COVERED = "covered_by_current_taxonomy"
STATUS_EXPANSION = "suggests_taxonomy_expansion"
STATUS_AMBIGUOUS = "ambiguous_composite_label"
STATUS_OUT_OF_SCOPE = "out_of_scope_or_non_empirical"


@dataclass
class WorkbookRow:
    sheet: str
    study: str
    condition: str


def repair_mojibake(value: str) -> str:
    text = value or ""
    try:
        repaired = text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        repaired = text
    return repaired


def normalize_text(value: str) -> str:
    text = repair_mojibake(value)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def display_text(value: str) -> str:
    return normalize_text(value)


def slug_text(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", normalize_text(value))
    return slug.strip("_")


def parse_workbook_study(study: str) -> tuple[str, str]:
    text = normalize_text(study)
    match = re.search(r"(19|20)\d{2}", text)
    year = match.group(0) if match else "unknown"
    author_part = text.split(",")[0]
    author_part = author_part.replace("&", " ")
    author_part = re.sub(r"\bet al\.?\b", "", author_part).strip()
    author_part = re.sub(r"\s+", " ", author_part).strip()
    return author_part, year


def parse_xlsx_rows(path: Path) -> list[WorkbookRow]:
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

    def col_letters(cell_ref: str) -> str:
        out = []
        for ch in cell_ref:
            if ch.isalpha():
                out.append(ch)
            else:
                break
        return "".join(out)

    rows: list[WorkbookRow] = []
    with zipfile.ZipFile(path) as zf:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            sst = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in sst.findall("main:si", ns):
                shared_strings.append(
                    "".join(t.text or "" for t in si.iterfind(".//main:t", ns))
                )

        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        relationships = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: "xl/" + rel.attrib["Target"] for rel in relationships}

        for sheet in workbook.find("main:sheets", ns):
            sheet_name = sheet.attrib["name"]
            rel_id = sheet.attrib[
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            ]
            xml_path = rel_map[rel_id]
            sheet_xml = ET.fromstring(zf.read(xml_path))
            sheet_data = sheet_xml.find("main:sheetData", ns)
            if sheet_data is None:
                continue

            for row_index, row in enumerate(sheet_data.findall("main:row", ns), start=1):
                values: dict[str, str] = {}
                for cell in row.findall("main:c", ns):
                    ref = cell.attrib.get("r", "")
                    key = col_letters(ref)
                    cell_type = cell.attrib.get("t")
                    value_node = cell.find("main:v", ns)
                    if value_node is None:
                        inline_node = cell.find("main:is", ns)
                        if inline_node is not None:
                            values[key] = "".join(
                                t.text or "" for t in inline_node.iterfind(".//main:t", ns)
                            )
                        continue

                    raw = value_node.text or ""
                    if cell_type == "s":
                        values[key] = shared_strings[int(raw)] if raw.isdigit() else raw
                    else:
                        values[key] = raw

                if row_index == 1:
                    continue

                study = values.get("A", "").strip()
                condition = values.get("B", "").strip()
                if study and condition:
                    rows.append(
                        WorkbookRow(
                            sheet=sheet_name,
                            study=display_text(study),
                            condition=display_text(condition),
                        )
                    )
    return rows


def load_checked_in_studies(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            row["_author_norm"] = normalize_text(row.get("Author", ""))
            row["_year"] = row.get("Year", "")
            rows.append(row)
    return rows


def match_checked_in_studies(
    workbook_studies: list[str],
    checked_in_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    seen = set()
    for workbook_study in workbook_studies:
        workbook_author_norm, workbook_year = parse_workbook_study(workbook_study)
        workbook_author_tokens = [token for token in workbook_author_norm.split() if token]
        workbook_author_head = workbook_author_tokens[0] if workbook_author_tokens else workbook_author_norm
        for row in checked_in_rows:
            if row["_year"] != workbook_year:
                continue
            author_norm = row["_author_norm"]
            if (
                workbook_author_norm.startswith(author_norm)
                or author_norm.startswith(workbook_author_norm)
                or workbook_author_head == author_norm
            ):
                canonical_key = row.get("Canonical_Study_Key", "")
                if canonical_key not in seen:
                    matches.append(row)
                    seen.add(canonical_key)
    return matches


def classify_workbook_condition(condition_label: str) -> dict[str, str]:
    norm = normalize_text(condition_label)

    if "review or combined study" in norm or "op2" in norm:
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Needs manual scope decision",
            "mapping_status": STATUS_OUT_OF_SCOPE,
            "notes": "This label describes a review or composite framing rather than a single empirical vestibular cohort and should not drive runtime grouping.",
        }

    if "healthy + lesion" in norm:
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Needs manual scope decision",
            "mapping_status": STATUS_AMBIGUOUS,
            "notes": "This workbook label mixes lesion and normative states and should be resolved manually before any runtime use.",
        }

    if "vestibular neuritis + cerebral small vessel disease" in norm:
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Needs split across vestibular and vascular axes",
            "mapping_status": STATUS_AMBIGUOUS,
            "notes": "This label spans two different scientific axes and should not be imported as a single runtime group value.",
        }

    if "bilateral vestibulopathy" in norm and "vestibular experts" in norm:
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Needs manual scope decision",
            "mapping_status": STATUS_AMBIGUOUS,
            "notes": "This label appears to combine a patient cohort and a non-clinical expert cohort in one workbook entry.",
        }

    if norm == "md" or any(
        token in norm for token in ["meniere", "late-stage md", "late stage md", "(md)", " md"]
    ):
        return {
            "proposed_condition_label": "Meniere's disease",
            "proposed_review_group": "Meniere's disease",
            "mapping_status": STATUS_COVERED,
            "notes": "Workbook spelling and abbreviation variants can be normalized directly to the current Meniere review bin.",
        }

    if "vestibular migraine" in norm or " vm" in norm:
        return {
            "proposed_condition_label": "Vestibular migraine",
            "proposed_review_group": "Vestibular migraine",
            "mapping_status": STATUS_COVERED,
            "notes": "Vestibular migraine is already a reserved top-layer review group in the scientific audit.",
        }

    if any(
        token in norm
        for token in [
            "post-concuss",
            "postconcuss",
            "post traumatic",
            "post-traumatic",
            "concussion",
            "mild tbi",
            "traumatic brain injury",
            "vestibular agnosia",
        ]
    ):
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Post-traumatic or concussive vestibulopathy",
            "mapping_status": STATUS_COVERED,
            "notes": "The workbook's concussion and TBI variants fit the current traumatic vestibular review bin while remaining distinct at the condition layer.",
        }

    if any(token in norm for token in ["white matter disease", "small vessel"]):
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "White matter disease or small-vessel lesions",
            "mapping_status": STATUS_COVERED,
            "notes": "The workbook explicitly supports the reserved vascular white-matter review bin.",
        }

    if any(
        token in norm
        for token in [
            "stroke",
            "infarct",
            "infarction",
            "wallenberg",
            "vascular vertigo",
            "brainstem / cerebellar",
            "subcortical vestibular circuitry",
            "pivc region",
            "cerebellar lesion",
            "peduncle",
            "thalamic or brainstem infarction",
        ]
    ):
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Stroke or ischemic vestibular-circuit lesions",
            "mapping_status": STATUS_COVERED,
            "notes": "The workbook contains multiple lesion and infarction cohorts that support retaining the stroke or ischemic review bin.",
        }

    if "spaceflight" in norm or "astronaut" in norm:
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Spaceflight-related vestibular adaptation",
            "mapping_status": STATUS_COVERED,
            "notes": "These workbook cohorts directly support the reserved spaceflight adaptation review bin.",
        }

    if any(token in norm for token in ["dancer", "vestibular experts", "slackliners", "experts"]):
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Vestibular experts",
            "mapping_status": STATUS_COVERED,
            "notes": "The workbook strongly supports a non-clinical expert or adaptation review bin distinct from disease entities.",
        }

    if any(
        token in norm
        for token in [
            "healthy older",
            "healthy younger vs. older",
            "healthy young vs healthy older",
            "healthy younger & older",
            "healthy younger vs. older adults",
            "age-related saccular",
            "age-related saccular loss",
        ]
    ):
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Healthy aging",
            "mapping_status": STATUS_COVERED,
            "notes": "These workbook cohorts align with the current aging-focused normative review bin.",
        }

    if any(token in norm for token in ["healthy adults", "healthy young adults", "balance training"]):
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Healthy non-clinical cohorts",
            "mapping_status": STATUS_COVERED,
            "notes": "These workbook cohorts now map to the dedicated `Healthy non-clinical cohorts` review bin instead of being forced into `Healthy aging`.",
        }

    if any(token in norm for token in ["pppd", "persistent postural perceptual dizziness"]):
        return {
            "proposed_condition_label": "Persistent postural perceptual dizziness",
            "proposed_review_group": "Other vestibular clinical cohorts",
            "mapping_status": STATUS_COVERED,
            "notes": "PPPD remains a distinct condition entity within the residual clinical review bucket.",
        }

    if "phobic postural vertigo" in norm or "idiopathic dizziness" in norm:
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Other vestibular clinical cohorts",
            "mapping_status": STATUS_COVERED,
            "notes": "These cohorts fit the residual clinical review bucket but should remain distinct from PPPD unless the source literature is re-opened.",
        }

    if any(
        token in norm
        for token in [
            "chronic, mild vestibulopathy",
            "horizontal semicircular canal loss",
            "peripheral vestibular dysfunction",
        ]
    ):
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Chronic or mild vestibulopathy",
            "mapping_status": STATUS_COVERED,
            "notes": "These workbook cohorts are reasonable fits for the current chronic or mild vestibular review bin.",
        }

    if any(token in norm for token in ["acoustic neuroma", "schwannoma"]):
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Vestibular schwannoma resection",
            "mapping_status": STATUS_COVERED,
            "notes": "Surgical unilateral deafferentation cohorts fit the current schwannoma-resection review framing.",
        }

    if "uvd" in norm and "vn" not in norm:
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Vestibular schwannoma resection",
            "mapping_status": STATUS_COVERED,
            "notes": "Surgical unilateral deafferentation cohorts fit the current schwannoma-resection review framing.",
        }

    if any(
        token in norm
        for token in [
            "vestibular neuritis",
            "acute vn",
            "vn recovery",
            "unilateral vn recovery",
            "acute vestibular neuritis recovery",
            "acute uvd from vn",
        ]
    ):
        return {
            "proposed_condition_label": "Vestibular neuritis",
            "proposed_review_group": "Unilateral vestibular loss or deafferentation",
            "mapping_status": STATUS_COVERED,
            "notes": "Acute VN and VN recovery labels support the unilateral peripheral loss review bin and should normalize to vestibular neuritis where appropriate.",
        }

    if any(token in norm for token in ["bilateral vestib", "bvp", "bvl", "incomplete bvp"]):
        if "neurofibromatosis type ii" in norm or "neurofibromatosis" in norm:
            return {
                "proposed_condition_label": condition_label,
                "proposed_review_group": "Vestibular schwannoma resection",
                "mapping_status": STATUS_COVERED,
                "notes": "The workbook's bilateral NF2 cohort is best treated as a surgical-causal schwannoma study at the top layer, consistent with the current audit.",
            }
        return {
            "proposed_condition_label": condition_label,
            "proposed_review_group": "Bilateral vestibulopathy",
            "mapping_status": STATUS_COVERED,
            "notes": "BVL, BVP, and incomplete BVP support retaining a bilateral vestibular review bin.",
        }

    return {
        "proposed_condition_label": condition_label,
        "proposed_review_group": "Unclassified or needs review",
        "mapping_status": STATUS_AMBIGUOUS,
        "notes": "No safe automatic mapping rule was available; this workbook label should be reviewed manually before any taxonomy change.",
    }


def build_crosswalk_rows(
    workbook_rows: list[WorkbookRow],
    checked_in_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    grouped: dict[str, list[WorkbookRow]] = defaultdict(list)
    for row in workbook_rows:
        grouped[row.condition].append(row)

    output_rows: list[dict[str, str]] = []
    for condition_label in sorted(grouped):
        entries = grouped[condition_label]
        studies = sorted({entry.study for entry in entries})
        sheets = sorted({entry.sheet for entry in entries})
        matched_checked_in = match_checked_in_studies(studies, checked_in_rows)

        proposal = classify_workbook_condition(condition_label)
        proposed_review_group = proposal["proposed_review_group"]
        runtime_group_ready = (
            "yes"
            if proposal["mapping_status"] == STATUS_COVERED
            and proposed_review_group in CURRENT_REVIEW_GROUPS
            else "no"
        )

        output_rows.append(
            {
                "Workbook_Condition_Label": condition_label,
                "N_Workbook_Studies": str(len(studies)),
                "Workbook_Study_Examples": "; ".join(studies[:4]),
                "Workbook_Sheets": "; ".join(sheets),
                "Proposed_Condition_Label": proposal["proposed_condition_label"],
                "Proposed_Review_Group": proposed_review_group,
                "Mapping_Status": proposal["mapping_status"],
                "Current_Runtime_Group_Ready": runtime_group_ready,
                "CheckedIn_Study_Match_Count": str(len(matched_checked_in)),
                "CheckedIn_Study_Matches": "; ".join(
                    match.get("Canonical_Study_Key", "") for match in matched_checked_in[:6]
                ),
                "Notes": proposal["notes"],
            }
        )
    return output_rows


def write_crosswalk_csv(rows: list[dict[str, str]], path: Path) -> None:
    fieldnames = [
        "Workbook_Condition_Label",
        "N_Workbook_Studies",
        "Workbook_Study_Examples",
        "Workbook_Sheets",
        "Proposed_Condition_Label",
        "Proposed_Review_Group",
        "Mapping_Status",
        "Current_Runtime_Group_Ready",
        "CheckedIn_Study_Match_Count",
        "CheckedIn_Study_Matches",
        "Notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown_summary(
    rows: list[dict[str, str]],
    workbook_rows: list[WorkbookRow],
    path: Path,
) -> None:
    unique_studies = sorted({row.study for row in workbook_rows})
    unique_conditions = sorted({row.condition for row in workbook_rows})

    status_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        status_groups[row["Mapping_Status"]].append(row)

    current_group_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        current_group_counts[row["Proposed_Review_Group"]] += 1

    covered_absent = [
        row
        for row in rows
        if row["Mapping_Status"] == STATUS_COVERED and row["CheckedIn_Study_Match_Count"] == "0"
    ]
    expansion_rows = status_groups[STATUS_EXPANSION]
    ambiguous_rows = status_groups[STATUS_AMBIGUOUS]
    out_of_scope_rows = status_groups[STATUS_OUT_OF_SCOPE]

    lines: list[str] = []
    lines.append("# Workbook Review-Frame Audit")
    lines.append("")
    lines.append(
        "This document crosswalks the original workbook review frame against the current scientific grouping audit and runtime taxonomy."
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- Source workbook: `{WORKBOOK_PATH}`")
    lines.append(f"- Checked-in scientific mapping source: `{CURRENT_DECISIONS_PATH.name}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Workbook study-condition pairs: {len(workbook_rows)}")
    lines.append(f"- Unique workbook studies: {len(unique_studies)}")
    lines.append(f"- Unique workbook condition labels: {len(unique_conditions)}")
    lines.append(
        f"- Condition labels covered directly by the current runtime taxonomy: {len(status_groups[STATUS_COVERED])}"
    )
    lines.append(
        f"- Condition labels suggesting taxonomy expansion: {len(expansion_rows)}"
    )
    lines.append(
        f"- Condition labels requiring manual review because they are composite or ambiguous: {len(ambiguous_rows)}"
    )
    lines.append(
        f"- Condition labels that should not drive runtime grouping as written: {len(out_of_scope_rows)}"
    )
    lines.append("")
    lines.append("## Main Findings")
    lines.append("")
    lines.append(
        "- The workbook strongly supports retaining the current clinical review bins for bilateral vestibular disorders, unilateral peripheral loss, schwannoma-related deafferentation, traumatic vestibulopathy, Meniere's disease, vestibular migraine, vascular or ischemic cohorts, white-matter disease, vestibular experts, and spaceflight adaptation."
    )
    lines.append(
        "- The workbook supports separating age-comparison cohorts from other healthy or training-based non-clinical cohorts. `Healthy aging` should stay narrow, while generic healthy adults and training cohorts can be incorporated through a broader `Healthy non-clinical cohorts` review bin."
    )
    lines.append(
        '- The workbook contains mixed or composite labels such as `vestibular neuritis + cerebral small vessel disease` and `bilateral vestibulopathy (bvp), "vestibular experts"`. Those labels are scientifically useful context, but they should not be used directly as runtime grouping values.'
    )
    lines.append(
        "- Several review-protocol categories are supported by the workbook even though they are absent or sparse in the checked-in CSV subset. That means the top-layer taxonomy should continue to reflect the review protocol, not only the currently instantiated extraction rows."
    )
    lines.append("")
    lines.append("## Proposed Review-Group Coverage")
    lines.append("")
    for group in sorted(current_group_counts):
        lines.append(f"- {group}: {current_group_counts[group]} workbook condition labels")
    lines.append("")
    lines.append("## Covered But Not Yet Represented In The Checked-In CSV")
    lines.append("")
    if covered_absent:
        for row in covered_absent[:20]:
            lines.append(f"- `{row['Workbook_Condition_Label']}` -> `{row['Proposed_Review_Group']}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Taxonomy Expansion Candidates")
    lines.append("")
    if expansion_rows:
        for row in expansion_rows:
            lines.append(
                f"- `{row['Workbook_Condition_Label']}` suggests an additional healthy or non-clinical review layer beyond the current `Healthy aging` bin."
            )
    else:
        lines.append("- None. The current runtime taxonomy now has a `Healthy non-clinical cohorts` review layer for these workbook labels.")
    lines.append("")
    lines.append("## Manual-Review Labels")
    lines.append("")
    for row in ambiguous_rows + out_of_scope_rows:
        lines.append(f"- `{row['Workbook_Condition_Label']}`: {row['Notes']}")
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append("- Keep the current runtime grouping logic unchanged for the checked-in subset.")
    lines.append(
        "- Use the workbook as the scientific reference frame for whether top-layer review bins are missing or misnamed."
    )
    lines.append(
        "- Keep `Healthy aging` for age-comparison cohorts and route generic healthy or training-based cohorts through `Healthy non-clinical cohorts` when those studies are added to the extraction table."
    )
    lines.append("")
    lines.append("## Machine-Readable Crosswalk")
    lines.append("")
    lines.append(f"- See `{OUTPUT_CSV_PATH.name}` for the full workbook-condition crosswalk.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not WORKBOOK_PATH.exists():
        raise SystemExit(f"Missing workbook: {WORKBOOK_PATH}")
    if not CURRENT_DECISIONS_PATH.exists():
        raise SystemExit(f"Missing checked-in decisions table: {CURRENT_DECISIONS_PATH}")

    workbook_rows = parse_xlsx_rows(WORKBOOK_PATH)
    checked_in_rows = load_checked_in_studies(CURRENT_DECISIONS_PATH)
    crosswalk_rows = build_crosswalk_rows(workbook_rows, checked_in_rows)
    write_crosswalk_csv(crosswalk_rows, OUTPUT_CSV_PATH)
    write_markdown_summary(crosswalk_rows, workbook_rows, OUTPUT_MD_PATH)

    print(f"Wrote {OUTPUT_CSV_PATH}")
    print(f"Wrote {OUTPUT_MD_PATH}")


if __name__ == "__main__":
    main()
