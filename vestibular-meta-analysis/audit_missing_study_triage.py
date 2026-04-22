#!/usr/bin/env python3
"""
Prioritize workbook-listed studies that are absent from the checked-in student
output and are most likely to contain extractable ROI-level effect information.

Outputs:
- missing_study_triage.csv
- MISSING_STUDY_TRIAGE.md
"""

from __future__ import annotations

import csv
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


REPO_DIR = Path(__file__).resolve().parent
WORKBOOK_PATH = Path(
    r"C:\Users\dpado\Documents\jhu\Oto-HNS\meta_analysis\meta_analysis_vestibular_gm_wm.xlsx"
)
CURRENT_DECISIONS_PATH = REPO_DIR / "scientific_grouping_decisions.csv"
WORKBOOK_CROSSWALK_PATH = REPO_DIR / "workbook_review_frame_crosswalk.csv"
OUTPUT_CSV_PATH = REPO_DIR / "missing_study_triage.csv"
OUTPUT_MD_PATH = REPO_DIR / "MISSING_STUDY_TRIAGE.md"


@dataclass
class WorkbookEntry:
    sheet: str
    study: str
    condition: str
    data: str
    outcome: str
    association: str
    region: str


@dataclass
class StudyAggregate:
    study: str
    clean_study: str = ""
    author_year_key: str = ""
    sheets: set[str] = field(default_factory=set)
    conditions: set[str] = field(default_factory=set)
    data_snippets: list[str] = field(default_factory=list)
    outcome_snippets: list[str] = field(default_factory=list)
    association_snippets: list[str] = field(default_factory=list)
    region_snippets: list[str] = field(default_factory=list)


def repair_mojibake(value: str) -> str:
    text = value or ""
    try:
        repaired = text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        repaired = text
    return repaired


def clean_display_text(value: str) -> str:
    text = repair_mojibake(value)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    return text


def normalize_text(value: str) -> str:
    text = clean_display_text(value)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def clean_workbook_study_name(study: str) -> str:
    text = clean_display_text(study)
    text = re.sub(r"((?:19|20)\d{2})\d+\b", r"\1", text)
    text = re.sub(r"\bet al\.\s+((?:19|20)\d{2})\b", r"et al., \1", text)
    text = re.sub(r"\.\s+((?:19|20)\d{2})\b", r"., \1", text)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_workbook_study(study: str) -> tuple[str, str]:
    text = normalize_text(clean_workbook_study_name(study))
    match = re.search(r"(19|20)\d{2}", text)
    year = match.group(0) if match else "unknown"
    author_part = text.split(",")[0]
    author_part = author_part.replace("&", " ")
    author_part = re.sub(r"\bet al\.?\b", "", author_part).strip()
    author_part = re.sub(r"[^\w\s-]", " ", author_part)
    author_part = re.sub(r"\s+", " ", author_part).strip()
    return author_part, year


def build_author_year_key(study: str) -> str:
    author_part, year = parse_workbook_study(study)
    return f"{author_part}|{year}"


def parse_workbook() -> list[WorkbookEntry]:
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

    def col_letters(cell_ref: str) -> str:
        out = []
        for ch in cell_ref:
            if ch.isalpha():
                out.append(ch)
            else:
                break
        return "".join(out)

    entries: list[WorkbookEntry] = []
    with zipfile.ZipFile(WORKBOOK_PATH) as zf:
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

            header_map: dict[str, str] = {}
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
                    header_map = {col: clean_display_text(name) for col, name in values.items()}
                    continue

                study = clean_display_text(values.get("A", ""))
                condition = clean_display_text(values.get("B", ""))
                if not study or not condition:
                    continue

                def value_for_header(name: str) -> str:
                    for col, header in header_map.items():
                        if header == name:
                            return clean_display_text(values.get(col, ""))
                    return ""

                entries.append(
                    WorkbookEntry(
                        sheet=sheet_name,
                        study=study,
                        condition=condition,
                        data=value_for_header("Data"),
                        outcome=value_for_header("Outcome Measure"),
                        association=value_for_header("Association"),
                        region=value_for_header("Region"),
                    )
                )
    return entries


def load_checked_in_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with CURRENT_DECISIONS_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            row["_author_norm"] = normalize_text(row.get("Author", ""))
            row["_year"] = row.get("Year", "")
            rows.append(row)
    return rows


def match_checked_in_studies(
    workbook_study: str,
    checked_in_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    workbook_author_norm, workbook_year = parse_workbook_study(workbook_study)
    workbook_author_tokens = [token for token in workbook_author_norm.split() if token]
    workbook_author_head = workbook_author_tokens[0] if workbook_author_tokens else workbook_author_norm

    matches: list[dict[str, str]] = []
    seen = set()
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


def load_crosswalk() -> dict[str, dict[str, str]]:
    with WORKBOOK_CROSSWALK_PATH.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {row["Workbook_Condition_Label"]: row for row in rows}


def aggregate_missing_studies(
    entries: list[WorkbookEntry],
    checked_in_rows: list[dict[str, str]],
) -> list[StudyAggregate]:
    by_study: dict[str, StudyAggregate] = {}
    for entry in entries:
        matched = match_checked_in_studies(entry.study, checked_in_rows)
        if matched:
            continue
        record = by_study.setdefault(
            entry.study,
            StudyAggregate(
                study=entry.study,
                clean_study=clean_workbook_study_name(entry.study),
                author_year_key=build_author_year_key(entry.study),
            ),
        )
        record.sheets.add(entry.sheet)
        record.conditions.add(entry.condition)
        if entry.data:
            record.data_snippets.append(entry.data)
        if entry.outcome:
            record.outcome_snippets.append(entry.outcome)
        if entry.association:
            record.association_snippets.append(entry.association)
        if entry.region:
            record.region_snippets.append(entry.region)
    return [by_study[key] for key in sorted(by_study)]


def dedupe_snippets(snippets: list[str], limit: int = 3) -> str:
    seen: list[str] = []
    for snippet in snippets:
        if snippet and snippet not in seen:
            seen.append(snippet)
    return " | ".join(seen[:limit])


def has_scope_split_risk(study: StudyAggregate) -> bool:
    condition_values = sorted(study.conditions)
    all_text = " ".join(
        condition_values
        + study.data_snippets
        + study.outcome_snippets
        + study.association_snippets
        + study.region_snippets
    ).lower()

    if len(condition_values) > 1:
        return True

    mixed_tokens = [
        "healthy + lesion",
        "vestibular neuritis + cerebral small vessel disease",
        "review or combined study",
        'bilateral vestibulopathy (bvp), "vestibular experts"',
    ]
    return any(token in all_text for token in mixed_tokens)


def score_extractability(study: StudyAggregate) -> tuple[str, str, str]:
    condition_text = " ".join(sorted(study.conditions)).lower()
    data_text = " ".join(study.data_snippets).lower()
    outcome_text = " ".join(study.outcome_snippets).lower()
    assoc_text = " ".join(study.association_snippets).lower()
    region_text = " ".join(study.region_snippets).lower()
    all_text = " ".join([condition_text, data_text, outcome_text, assoc_text, region_text])

    review_like = any(token in all_text for token in ["review or combined study", "op2 region"])
    mixed_label = any(token in all_text for token in ["healthy + lesion", "vestibular neuritis + cerebral small vessel disease"])
    explicit_regions = bool(region_text and region_text not in {"na", ""})
    multiple_regions = region_text.count(",") >= 1 or region_text.count(";") >= 1
    has_controls = bool(
        re.search(r"\bcontrol", data_text)
        or re.search(r"\bage-matched healthy", data_text)
        or re.search(r"\bhealthy controls?\b", data_text)
    )
    has_numeric_groups = bool(re.search(r"\b\d+\b", data_text))
    direct_difference = any(
        token in assoc_text
        for token in ["reduction", "increase", "lower", "higher", "compared to", "vs.", "significantly worse", "abnormal"]
    )
    roi_metric = any(
        token in outcome_text
        for token in [
            "vbm",
            "manual volumetry",
            "gmv",
            "wmv",
            "cortical thickness",
            "sbm",
            "dti",
            "fa",
            "md",
            "rd",
            "ad",
            "noddi",
            "mk",
            "rk",
            "ak",
        ]
    )
    network_only = any(
        token in outcome_text
        for token in ["graph theory", "fc", "rsfmri", "resting-state", "alff", "reho"]
    ) and not roi_metric
    structural_or_dti_sheet = any(sheet in {"MRI_GM", "MRI_WM", "DTI"} for sheet in study.sheets)

    score = 0
    if explicit_regions:
        score += 2
    if multiple_regions:
        score += 1
    if has_controls:
        score += 2
    if has_numeric_groups:
        score += 1
    if roi_metric:
        score += 2
    if structural_or_dti_sheet:
        score += 1
    if direct_difference:
        score += 1
    if network_only:
        score -= 1
    if mixed_label:
        score -= 2
    if review_like:
        score -= 3

    if review_like:
        return (
            "low",
            "unlikely_extractable_for_current_table",
            "Review or composite framing rather than a single extractable empirical cohort.",
        )
    if mixed_label:
        return (
            "low",
            "unlikely_extractable_for_current_table",
            "Condition label mixes scientific axes and should be resolved before extraction.",
        )
    if score >= 7:
        return (
            "high",
            "likely_extractable_roi_effects",
            "Workbook notes suggest explicit regions, quantitative imaging metrics, and a usable comparison design.",
        )
    if score >= 4:
        return (
            "medium",
            "maybe_extractable_with_manual_review",
            "Workbook notes suggest potential ROI-level findings, but the paper must be checked for convertible statistics.",
        )
    return (
        "low",
        "unlikely_extractable_for_current_table",
        "Workbook notes do not yet suggest a reliable ROI-wise effect-size extraction path.",
    )


def triage_rows(
    missing_studies: list[StudyAggregate],
    crosswalk: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    collision_counts = defaultdict(int)
    for study in missing_studies:
        collision_counts[study.author_year_key] += 1

    rows: list[dict[str, str]] = []
    for study in missing_studies:
        priority, extractability, rationale = score_extractability(study)
        condition_values = sorted(study.conditions)
        primary_condition = condition_values[0]
        condition_crosswalk = crosswalk.get(normalize_text(primary_condition), {})
        proposed_review_group = condition_crosswalk.get("Proposed_Review_Group", "")
        author_year_collision = collision_counts[study.author_year_key] > 1
        scope_split_risk = has_scope_split_risk(study)

        if author_year_collision and scope_split_risk:
            review_queue_status = "hold_author_year_collision_and_scope_split"
        elif author_year_collision:
            review_queue_status = "hold_author_year_collision"
        elif scope_split_risk:
            review_queue_status = "hold_scope_split"
        else:
            review_queue_status = "ready_for_manual_review"

        dedup_note_parts: list[str] = []
        if study.clean_study != study.study:
            dedup_note_parts.append("Workbook study label normalized for year or punctuation noise.")
        if author_year_collision:
            dedup_note_parts.append(
                "Another missing-study row shares this author-year signature; resolve same-year paper versus duplicate before extraction."
            )
        if scope_split_risk:
            dedup_note_parts.append(
                "Workbook entry mixes multiple conditions, frames, or cohort types and should be split or scoped before review."
            )
        dedup_note = " ".join(dedup_note_parts) or "No duplicate or scope warning detected in the workbook triage pass."

        next_action = {
            "high": "Review the paper first for table or supplement statistics and add to the extraction queue if ROI-level group data are present.",
            "medium": "Open the paper to verify whether the reported findings include ROI-wise statistics rather than only narrative or connectivity summaries.",
            "low": "Defer unless the meta-analysis broadens beyond the current ROI and effect-size schema.",
        }[priority]

        if review_queue_status == "hold_author_year_collision":
            next_action = "Resolve the author-year collision first, then decide which record belongs in the manual review queue."
        elif review_queue_status == "hold_scope_split":
            next_action = "Split the workbook entry into a single-cohort or single-frame record before manual paper review."
        elif review_queue_status == "hold_author_year_collision_and_scope_split":
            next_action = "Resolve both the author-year collision and the mixed-scope workbook entry before manual paper review."

        rows.append(
            {
                "Workbook_Study": study.study,
                "Clean_Workbook_Study": study.clean_study,
                "Author_Year_Key": study.author_year_key,
                "Workbook_Conditions": "; ".join(condition_values),
                "Workbook_Sheets": "; ".join(sorted(study.sheets)),
                "Proposed_Review_Group": proposed_review_group,
                "Priority": priority,
                "Extractability": extractability,
                "Review_Queue_Status": review_queue_status,
                "Dedup_And_Scope_Note": dedup_note,
                "Triage_Rationale": rationale,
                "Data_Summary": dedupe_snippets(study.data_snippets),
                "Outcome_Summary": dedupe_snippets(study.outcome_snippets),
                "Region_Summary": dedupe_snippets(study.region_snippets),
                "Suggested_Next_Action": next_action,
            }
        )

    priority_rank = {"high": 0, "medium": 1, "low": 2}
    review_rank = {
        "ready_for_manual_review": 0,
        "hold_author_year_collision": 1,
        "hold_scope_split": 2,
        "hold_author_year_collision_and_scope_split": 3,
    }
    rows.sort(
        key=lambda row: (
            review_rank[row["Review_Queue_Status"]],
            priority_rank[row["Priority"]],
            row["Clean_Workbook_Study"],
        )
    )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "Workbook_Study",
        "Clean_Workbook_Study",
        "Author_Year_Key",
        "Workbook_Conditions",
        "Workbook_Sheets",
        "Proposed_Review_Group",
        "Priority",
        "Extractability",
        "Review_Queue_Status",
        "Dedup_And_Scope_Note",
        "Triage_Rationale",
        "Data_Summary",
        "Outcome_Summary",
        "Region_Summary",
        "Suggested_Next_Action",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    high = [row for row in rows if row["Priority"] == "high"]
    medium = [row for row in rows if row["Priority"] == "medium"]
    low = [row for row in rows if row["Priority"] == "low"]
    ready = [row for row in rows if row["Review_Queue_Status"] == "ready_for_manual_review"]
    hold_collision = [
        row for row in rows if row["Review_Queue_Status"] == "hold_author_year_collision"
    ]
    hold_scope = [row for row in rows if row["Review_Queue_Status"] == "hold_scope_split"]
    hold_both = [
        row
        for row in rows
        if row["Review_Queue_Status"] == "hold_author_year_collision_and_scope_split"
    ]
    normalized_names = [
        row for row in rows if row["Workbook_Study"] != row["Clean_Workbook_Study"]
    ]

    lines: list[str] = []
    lines.append("# Missing Study Triage")
    lines.append("")
    lines.append(
        "This document prioritizes workbook-listed studies that are absent from the checked-in student extraction and are most likely to yield ROI-level effect information after paper review."
    )
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Source workbook: `{WORKBOOK_PATH}`")
    lines.append(f"- Current checked-in study table: `{CURRENT_DECISIONS_PATH.name}`")
    lines.append(f"- Workbook taxonomy crosswalk: `{WORKBOOK_CROSSWALK_PATH.name}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Missing workbook studies triaged: {len(rows)}")
    lines.append(f"- High priority: {len(high)}")
    lines.append(f"- Medium priority: {len(medium)}")
    lines.append(f"- Low priority: {len(low)}")
    lines.append(f"- Ready for manual review: {len(ready)}")
    lines.append(f"- Hold for author-year collision: {len(hold_collision)}")
    lines.append(f"- Hold for scope split: {len(hold_scope)}")
    lines.append(f"- Hold for both issues: {len(hold_both)}")
    lines.append(f"- Workbook study labels normalized: {len(normalized_names)}")
    lines.append("")
    lines.append("## Dedup And Scope Audit")
    lines.append("")
    lines.append(
        "- `ready_for_manual_review` means the workbook row does not show an author-year collision or obvious mixed-scope problem in this triage pass."
    )
    lines.append(
        "- `hold_author_year_collision` means another missing row shares the same normalized author-year signature, so same-paper versus companion-paper status should be resolved before review."
    )
    lines.append(
        "- `hold_scope_split` means the workbook row mixes multiple conditions or design frames and should be split before review."
    )
    lines.append(
        "- `hold_author_year_collision_and_scope_split` means both warnings apply and the row should stay out of the primary review queue."
    )
    lines.append("")
    if hold_collision or hold_scope or hold_both:
        lines.append("### Hold List")
        lines.append("")
        for row in hold_collision + hold_scope + hold_both:
            lines.append(
                f"- `{row['Clean_Workbook_Study']}` | `{row['Workbook_Conditions']}` | `{row['Review_Queue_Status']}`"
            )
            lines.append(f"  Note: {row['Dedup_And_Scope_Note']}")
    lines.append("")
    lines.append("## Reading Strategy")
    lines.append("")
    lines.append(
        "- Start with the `ready_for_manual_review` subset of the high-priority group. Those are the cleanest candidates for ROI-wise extraction with convertible statistics."
    )
    lines.append(
        "- Use the medium-priority group only after the clean high-priority queue is exhausted or if those studies target especially important review bins."
    )
    lines.append(
        "- Resolve all hold-list rows before manual review so the extraction queue does not start with duplicate-risk or mixed-scope studies."
    )
    lines.append(
        "- Defer the low-priority group unless you broaden the table schema beyond ROI-level effect-size extraction."
    )
    lines.append("")
    lines.append("## High Priority")
    lines.append("")
    if high:
        for row in high:
            lines.append(
                f"- `{row['Clean_Workbook_Study']}` | `{row['Workbook_Conditions']}` | `{row['Proposed_Review_Group']}` | `{row['Review_Queue_Status']}`"
            )
            lines.append(f"  Rationale: {row['Triage_Rationale']}")
            lines.append(f"  Dedup/scope note: {row['Dedup_And_Scope_Note']}")
            lines.append(f"  Region summary: {row['Region_Summary'] or 'n/a'}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Medium Priority")
    lines.append("")
    if medium:
        for row in medium[:15]:
            lines.append(
                f"- `{row['Clean_Workbook_Study']}` | `{row['Workbook_Conditions']}` | `{row['Proposed_Review_Group']}` | `{row['Review_Queue_Status']}`"
            )
            lines.append(f"  Rationale: {row['Triage_Rationale']}")
            lines.append(f"  Dedup/scope note: {row['Dedup_And_Scope_Note']}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Low Priority")
    lines.append("")
    if low:
        for row in low[:15]:
            lines.append(
                f"- `{row['Clean_Workbook_Study']}` | `{row['Workbook_Conditions']}` | `{row['Proposed_Review_Group']}` | `{row['Review_Queue_Status']}`"
            )
            lines.append(f"  Rationale: {row['Triage_Rationale']}")
            lines.append(f"  Dedup/scope note: {row['Dedup_And_Scope_Note']}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Machine-Readable Output")
    lines.append("")
    lines.append(f"- See `{OUTPUT_CSV_PATH.name}` for the full triage table.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not WORKBOOK_PATH.exists():
        raise SystemExit(f"Missing workbook: {WORKBOOK_PATH}")
    if not CURRENT_DECISIONS_PATH.exists():
        raise SystemExit(f"Missing decisions table: {CURRENT_DECISIONS_PATH}")
    if not WORKBOOK_CROSSWALK_PATH.exists():
        raise SystemExit(
            f"Missing workbook crosswalk: {WORKBOOK_CROSSWALK_PATH}. Run audit_workbook_review_frame.py first."
        )

    workbook_entries = parse_workbook()
    checked_in_rows = load_checked_in_rows()
    crosswalk = load_crosswalk()
    missing_studies = aggregate_missing_studies(workbook_entries, checked_in_rows)
    rows = triage_rows(missing_studies, crosswalk)
    write_csv(OUTPUT_CSV_PATH, rows)
    write_markdown(OUTPUT_MD_PATH, rows)

    print(f"Wrote {OUTPUT_CSV_PATH}")
    print(f"Wrote {OUTPUT_MD_PATH}")
    print(f"Missing workbook studies triaged: {len(rows)}")


if __name__ == "__main__":
    main()
