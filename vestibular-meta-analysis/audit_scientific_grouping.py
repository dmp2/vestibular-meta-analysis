#!/usr/bin/env python3
"""Generate study-level scientific grouping audit artifacts.

This script intentionally does not modify the source analysis tables.
It collapses ROI-level rows from ``mycode-11.24/output_with_g.csv`` to
canonical studies, applies a manually curated scientific mapping spec,
and writes tracked audit artifacts for review and later code use.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT_CSV = ROOT / "mycode-11.24" / "output_with_g.csv"
DECISIONS_CSV = ROOT / "scientific_grouping_decisions.csv"
MAPPING_CSV = ROOT / "scientific_grouping_mapping.csv"


def norm_space(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def norm_title(text: str) -> str:
    text = text.strip().lower()
    text = text.replace("neuronitis", "neuritis")
    text = text.replace("ménière", "meniere")
    text = text.replace("’", "'")
    text = text.replace("“", "\"")
    text = text.replace("”", "\"")
    text = text.replace("\"", "'")
    return norm_space(text)


def norm_author(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return norm_space(text.lower())


def canonical_study_key(author: str, year: str, title: str) -> str:
    return f"{norm_author(author)}|{year.strip()}|{norm_title(title)}"


def display_join(values: set[str]) -> str:
    cleaned = sorted(v for v in values if v and v != "NA")
    return "; ".join(cleaned)


def summarize_context(record: dict[str, object]) -> str:
    parts: list[str] = []
    n_pat = display_join(record["sample_sizes_patients"])
    n_ctl = display_join(record["sample_sizes_controls"])
    laterality = display_join(record["side_deaf_or_lesion"])
    subtype = display_join(record["subtypes"])
    titles = sorted(record["titles"])

    if n_pat or n_ctl:
        parts.append(f"N patients={n_pat or 'NA'}; controls={n_ctl or 'NA'}")
    if laterality:
        parts.append(f"Laterality/cohort side={laterality}")
    if subtype:
        parts.append(f"Subtype={subtype}")
    if len(titles) > 1:
        parts.append("Title reconciliation=" + " || ".join(titles))

    return " | ".join(parts)


LIT = {
    "auvp_vn": "Strupp et al. 2022 Barany acute unilateral vestibulopathy / vestibular neuritis consensus | https://pmc.ncbi.nlm.nih.gov/articles/PMC9661346/",
    "bvp": "Strupp et al. 2017 Barany bilateral vestibulopathy diagnostic criteria | https://pmc.ncbi.nlm.nih.gov/articles/PMC9249284/",
    "meniere": "Lopez-Escamez et al. 2015 Diagnostic criteria for Menière's disease | https://pubmed.ncbi.nlm.nih.gov/25882471/",
    "pppd": "Staab et al. 2017 Barany PPPD diagnostic criteria | https://pubmed.ncbi.nlm.nih.gov/29036855/",
    "study_specific": "Study-specific cohort label retained; no separate Barany consensus entity was imposed for this subgroup.",
    "non_clinical": "Non-clinical expertise/adaptation cohort defined by study design rather than disease nosology.",
}


STUDY_DECISIONS = {
    "alhilali|2014|detection of central white matter injury underlying vestibulopathy after mild traumatic brain injury": {
        "Proposed_Condition_Normalized": "Mild traumatic brain injury with vestibular symptoms",
        "Proposed_Review_Group": "Post-traumatic or concussive vestibulopathy",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Concussion-related vestibulopathy",
        "Rationale": "Retain the mTBI vestibular cohort as its own condition-level entity rather than merging it into generic post-concussive cohorts.",
        "Literature_Anchor": LIT["study_specific"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "behnke|2024|assessment of white matter microstructure integrity in subacute postconcussive vestibular dysfunction using noddi": {
        "Proposed_Condition_Normalized": "Post-concussive vestibular dysfunction",
        "Proposed_Review_Group": "Post-traumatic or concussive vestibulopathy",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Concussion-related vestibulopathy",
        "Rationale": "Keep post-concussive vestibular dysfunction distinct from mTBI and sports-related concussion cohorts because the study itself names a specific post-concussive vestibular syndrome.",
        "Literature_Anchor": LIT["study_specific"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "brandt|2005|vestibular loss causes hippocampal atrophy and impaired spatial memory in humans": {
        "Proposed_Condition_Normalized": "NF2 bilateral vestibular loss after neurectomy",
        "Proposed_Review_Group": "Vestibular schwannoma resection",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Bilateral vestibular syndromes",
        "Rationale": "Keep the bilateral postoperative NF2 cohort distinct at the condition layer, place it in the review's schwannoma-resection bucket because the causal surgical context is explicit, and preserve its bilateral-loss physiology in the fallback family layer.",
        "Literature_Anchor": LIT["bvp"],
        "Confidence": "Medium",
        "Open_Question": "Future expansions may warrant a separate surgical-context flag if more bilateral postoperative cohorts enter the table.",
    },
    "cheng|2023|assessment of functional and structural brain abnormalities with resting-state functional mri in patients with vestibular neuritis": {
        "Proposed_Condition_Normalized": "Vestibular neuritis",
        "Proposed_Review_Group": "Unilateral vestibular loss or deafferentation",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Acute unilateral vestibular syndromes",
        "Rationale": "Collapse the neuritis/neuronitis title spelling variant to a single study and retain the cohort as vestibular neuritis at the condition layer.",
        "Literature_Anchor": LIT["auvp_vn"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "cutfield|2014|visual and proprioceptive interaction in patients with bilateral vestibular loss": {
        "Proposed_Condition_Normalized": "Bilateral vestibular loss",
        "Proposed_Review_Group": "Bilateral vestibulopathy",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Bilateral vestibular syndromes",
        "Rationale": "Keep bilateral vestibular loss separate from bilateral vestibular failure and bilateral vestibulopathy because the paper uses an explicit cohort label and the audit is conservative at the condition layer.",
        "Literature_Anchor": LIT["bvp"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "gard|2022|post-concussive vestibular dysfunction is related to injury to the inferior vestibular nerve": {
        "Proposed_Condition_Normalized": "Sports-related concussion with persistent post-concussive symptoms",
        "Proposed_Review_Group": "Post-traumatic or concussive vestibulopathy",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Concussion-related vestibulopathy",
        "Rationale": "Retain the sports-related persistent post-concussive cohort as a distinct condition-level entity within the broader concussive review group.",
        "Literature_Anchor": LIT["study_specific"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "gottlich|2016|hippocampal gray matter volume in bilateral vestibular failure": {
        "Proposed_Condition_Normalized": "Bilateral vestibular failure",
        "Proposed_Review_Group": "Bilateral vestibulopathy",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Bilateral vestibular syndromes",
        "Rationale": "Preserve the paper's bilateral vestibular failure label at the condition layer while grouping it with the bilateral vestibular disorders selected by the review.",
        "Literature_Anchor": LIT["bvp"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "helmchen|2009|structural changes in the human brain following vestibular neuritis indicate central vestibular compensation": {
        "Proposed_Condition_Normalized": "Vestibular neuritis",
        "Proposed_Review_Group": "Unilateral vestibular loss or deafferentation",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Acute unilateral vestibular syndromes",
        "Rationale": "The paper's acute unilateral peripheral vestibular neuritis label is treated as the same clinical entity as vestibular neuritis, with the more specific wording retained in raw subtype/context rather than the normalized name.",
        "Literature_Anchor": LIT["auvp_vn"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "helmchen|2011|structural brain changes following peripheral vestibulo-cochlear lesion may indicate multisensory compensation": {
        "Proposed_Condition_Normalized": "Unilateral vestibular deafferentation after vestibular schwannoma surgery",
        "Proposed_Review_Group": "Vestibular schwannoma resection",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Vestibular schwannoma resection or deafferentation",
        "Rationale": "Unify the unilateral post-surgical acoustic neuroma/acoustic neurinoma/vestibular schwannoma cohorts under one normalized unilateral deafferentation entity because the clinical state and causal pathway are the same.",
        "Literature_Anchor": LIT["study_specific"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "hufner|2007|spatial memory and hippocampal volume in humans with unilateral vestibular deafferentation": {
        "Proposed_Condition_Normalized": "Unilateral vestibular deafferentation after vestibular schwannoma surgery",
        "Proposed_Review_Group": "Vestibular schwannoma resection",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Vestibular schwannoma resection or deafferentation",
        "Rationale": "This unilateral acoustic neurinoma surgery cohort is scientifically equivalent to the other unilateral post-surgical deafferentation studies and should not remain split only by wording.",
        "Literature_Anchor": LIT["study_specific"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "hufner|2009|gray-matter atrophy after chronic complete unilateral vestibular deafferentation": {
        "Proposed_Condition_Normalized": "Unilateral vestibular deafferentation after vestibular schwannoma surgery",
        "Proposed_Review_Group": "Vestibular schwannoma resection",
        "Proposed_Cohort_Contrast": "unclear_or_nonstandard",
        "Condition_Family_If_Needed": "Vestibular schwannoma resection or deafferentation",
        "Rationale": "The disease entity aligns with the unilateral post-surgical deafferentation cluster, but the checked-in extraction lacks a control sample size and therefore the comparison structure should remain explicit as unclear rather than inferred.",
        "Literature_Anchor": LIT["study_specific"],
        "Confidence": "Medium",
        "Open_Question": "If the source paper is revisited, confirm whether the missing control count reflects extraction loss or a genuine non-standard comparison design.",
    },
    "kremmyda|2016|beyond dizziness: virtual navigation, spatial anxiety and hippocampal volume in bilateral vestibulopathy": {
        "Proposed_Condition_Normalized": "Bilateral vestibulopathy",
        "Proposed_Review_Group": "Bilateral vestibulopathy",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Bilateral vestibular syndromes",
        "Rationale": "Keep the explicit bilateral vestibulopathy label because it matches modern diagnostic language and the review's bilateral vestibular disease bucket.",
        "Literature_Anchor": LIT["bvp"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "nigmatullina|2013|the neuroanatomical correlates of training-related perceptuo-reflex uncoupling in dancers": {
        "Proposed_Condition_Normalized": "Professional ballet dancers",
        "Proposed_Review_Group": "Vestibular experts",
        "Proposed_Cohort_Contrast": "expertise_vs_control",
        "Condition_Family_If_Needed": "Adaptive or non-clinical cohorts",
        "Rationale": "This is a non-clinical expertise cohort and should remain outside disease nosology while still occupying an explicit review-design category.",
        "Literature_Anchor": LIT["non_clinical"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "schone|2022|hippocampal volume in patients with bilateral and unilateral peripheral vestibular dysfunction": {
        "Proposed_Condition_Normalized": "Peripheral vestibular dysfunction",
        "Proposed_Review_Group": "Chronic or mild vestibulopathy",
        "Proposed_Cohort_Contrast": "within_clinical_subgroup_comparison",
        "Condition_Family_If_Needed": "Peripheral vestibular syndromes",
        "Rationale": "Retain the broad peripheral vestibular dysfunction label because the paper explicitly mixes unilateral and bilateral peripheral cohorts; place it in the chronic/mild vestibulopathy review bin as the closest survey-fit category without pretending it is a single narrow diagnosis.",
        "Literature_Anchor": LIT["study_specific"],
        "Confidence": "Medium",
        "Open_Question": "If more heterogeneous peripheral vestibular cohorts are added, consider whether this should become its own review-group rather than remaining inside chronic or mild vestibulopathy.",
    },
    "seo|2016|the change of hippocampal volume and its relevance with inner ear function in meniere's disease patients": {
        "Proposed_Condition_Normalized": "Meniere's disease",
        "Proposed_Review_Group": "Meniere's disease",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Meniere's disease",
        "Rationale": "Keep Ménière's disease as its own condition and review group, normalizing only spelling/diacritics.",
        "Literature_Anchor": LIT["meniere"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "smith|2022|the 'vestibular neuromatrix': a proposed, expanded vestibular network from graph theory in post-concussive vestibular dysfunction": {
        "Proposed_Condition_Normalized": "Post-concussive vestibular dysfunction",
        "Proposed_Review_Group": "Post-traumatic or concussive vestibulopathy",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Concussion-related vestibulopathy",
        "Rationale": "This graph-theory study uses the same post-concussive vestibular dysfunction cohort concept and should remain aligned with the other post-concussive study at the condition layer.",
        "Literature_Anchor": LIT["study_specific"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "wurthmann|2017|cerebral gray matter changes in persistent postural perceptual dizziness": {
        "Proposed_Condition_Normalized": "Persistent postural perceptual dizziness",
        "Proposed_Review_Group": "Other vestibular clinical cohorts",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Functional vestibular disorders",
        "Rationale": "Keep PPPD as its own recognized diagnostic entity at the condition layer while placing it in the residual review bucket because PPPD was not one of the original survey's named top-level categories.",
        "Literature_Anchor": LIT["pppd"],
        "Confidence": "High",
        "Open_Question": "If additional PPPD studies are added later, reconsider whether PPPD should become its own dedicated review-group.",
    },
    "van cruijsen|2007|hippocampal volume measurement in patients with meniere's disease: a pilot study": {
        "Proposed_Condition_Normalized": "Meniere's disease",
        "Proposed_Review_Group": "Meniere's disease",
        "Proposed_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Meniere's disease",
        "Rationale": "The mixed unilateral/bilateral patient composition stays in context/subtype, while the disease entity remains Meniere's disease.",
        "Literature_Anchor": LIT["meniere"],
        "Confidence": "High",
        "Open_Question": "",
    },
    "zu eulenburg|2010|voxel-based morphometry depicts central compensation after vestibular neuritis": {
        "Proposed_Condition_Normalized": "Vestibular neuritis",
        "Proposed_Review_Group": "Unilateral vestibular loss or deafferentation",
        "Proposed_Cohort_Contrast": "within_clinical_subgroup_comparison",
        "Condition_Family_If_Needed": "Acute unilateral vestibular syndromes",
        "Rationale": "The disease entity is vestibular neuritis, but the extracted rows reflect subgrouped unilateral cohorts with different patient/control counts, so the comparison structure should remain explicitly marked as within-clinical-subgroup rather than generic patient-vs-control.",
        "Literature_Anchor": LIT["auvp_vn"],
        "Confidence": "High",
        "Open_Question": "",
    },
}


RAW_ETIOLOGY_MAPPING = {
    "Acute unilateral peripheral vestibular neuritis": {
        "Final_Condition_Normalized": "Vestibular neuritis",
        "Final_Review_Group": "Unilateral vestibular loss or deafferentation",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Acute unilateral vestibular syndromes",
        "Mapping_Rationale": "Collapsed with vestibular neuritis because Bárány acute unilateral vestibulopathy / vestibular neuritis criteria treat the naming variants as one clinical entity.",
        "Literature_Anchor": LIT["auvp_vn"],
        "Notes": "",
    },
    "Bilateral vestibular failure": {
        "Final_Condition_Normalized": "Bilateral vestibular failure",
        "Final_Review_Group": "Bilateral vestibulopathy",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Bilateral vestibular syndromes",
        "Mapping_Rationale": "Kept distinct at the condition layer but grouped under the bilateral vestibular disorder review bucket.",
        "Literature_Anchor": LIT["bvp"],
        "Notes": "",
    },
    "Bilateral vestibular loss": {
        "Final_Condition_Normalized": "Bilateral vestibular loss",
        "Final_Review_Group": "Bilateral vestibulopathy",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Bilateral vestibular syndromes",
        "Mapping_Rationale": "Kept distinct at the condition layer but grouped under the bilateral vestibular disorder review bucket.",
        "Literature_Anchor": LIT["bvp"],
        "Notes": "",
    },
    "Bilateral vestibulopathy": {
        "Final_Condition_Normalized": "Bilateral vestibulopathy",
        "Final_Review_Group": "Bilateral vestibulopathy",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Bilateral vestibular syndromes",
        "Mapping_Rationale": "Already matches the modern bilateral vestibulopathy entity and review bucket.",
        "Literature_Anchor": LIT["bvp"],
        "Notes": "",
    },
    "Chronic bilateral vestibular loss due to neurofibromatosis 2 after bilateral vestibular neurectomy": {
        "Final_Condition_Normalized": "NF2 bilateral vestibular loss after neurectomy",
        "Final_Review_Group": "Vestibular schwannoma resection",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Bilateral vestibular syndromes",
        "Mapping_Rationale": "Top-layer grouping follows the explicit surgical-causal context in the review scope; fallback family preserves bilateral vestibular physiology.",
        "Literature_Anchor": LIT["bvp"],
        "Notes": "Resolved toward surgical-context at Review_Group, not generic bilateral vestibulopathy.",
    },
    "Chronic complete unilateral vestibular deafferentation due to vestibular schwannoma removal": {
        "Final_Condition_Normalized": "Unilateral vestibular deafferentation after vestibular schwannoma surgery",
        "Final_Review_Group": "Vestibular schwannoma resection",
        "Default_Cohort_Contrast": "unclear_or_nonstandard",
        "Condition_Family_If_Needed": "Vestibular schwannoma resection or deafferentation",
        "Mapping_Rationale": "Merged with the other unilateral post-surgical deafferentation labels because the cohort state and surgical pathway are the same.",
        "Literature_Anchor": LIT["study_specific"],
        "Notes": "Current extraction lacks control sample size for this study.",
    },
    "Long-term vestibular adaptation in professional ballet dancers": {
        "Final_Condition_Normalized": "Professional ballet dancers",
        "Final_Review_Group": "Vestibular experts",
        "Default_Cohort_Contrast": "expertise_vs_control",
        "Condition_Family_If_Needed": "Adaptive or non-clinical cohorts",
        "Mapping_Rationale": "Explicitly treated as a non-clinical expertise cohort rather than a disease entity.",
        "Literature_Anchor": LIT["non_clinical"],
        "Notes": "",
    },
    "Ménière’s disease": {
        "Final_Condition_Normalized": "Meniere's disease",
        "Final_Review_Group": "Meniere's disease",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Meniere's disease",
        "Mapping_Rationale": "Normalize spelling/diacritics only; do not collapse Ménière's disease into a broader chronic dizziness bucket.",
        "Literature_Anchor": LIT["meniere"],
        "Notes": "",
    },
    "Mild traumatic brain injury with vestibular symptoms": {
        "Final_Condition_Normalized": "Mild traumatic brain injury with vestibular symptoms",
        "Final_Review_Group": "Post-traumatic or concussive vestibulopathy",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Concussion-related vestibulopathy",
        "Mapping_Rationale": "Retained as its own traumatic vestibular cohort rather than merged into generic post-concussive dysfunction.",
        "Literature_Anchor": LIT["study_specific"],
        "Notes": "",
    },
    "Peripheral vestibular dysfunction": {
        "Final_Condition_Normalized": "Peripheral vestibular dysfunction",
        "Final_Review_Group": "Chronic or mild vestibulopathy",
        "Default_Cohort_Contrast": "within_clinical_subgroup_comparison",
        "Condition_Family_If_Needed": "Peripheral vestibular syndromes",
        "Mapping_Rationale": "Retained because the source study explicitly spans bilateral and unilateral peripheral cohorts; the review-group placement is a survey-fit decision, not a claim that this is a single narrow diagnosis.",
        "Literature_Anchor": LIT["study_specific"],
        "Notes": "",
    },
    "Persistent postural perceptual dizziness": {
        "Final_Condition_Normalized": "Persistent postural perceptual dizziness",
        "Final_Review_Group": "Other vestibular clinical cohorts",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Functional vestibular disorders",
        "Mapping_Rationale": "Keep PPPD as its own recognized condition while placing it in the residual review bucket because PPPD was not a named top-level survey category.",
        "Literature_Anchor": LIT["pppd"],
        "Notes": "Future expansion could justify a dedicated PPPD review-group.",
    },
    "Post-concussive vestibular dysfunction": {
        "Final_Condition_Normalized": "Post-concussive vestibular dysfunction",
        "Final_Review_Group": "Post-traumatic or concussive vestibulopathy",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Concussion-related vestibulopathy",
        "Mapping_Rationale": "Retained as a distinct post-concussive vestibular cohort inside the broader traumatic review group.",
        "Literature_Anchor": LIT["study_specific"],
        "Notes": "",
    },
    "Sports-related concussion with persistent post-concussive symptoms": {
        "Final_Condition_Normalized": "Sports-related concussion with persistent post-concussive symptoms",
        "Final_Review_Group": "Post-traumatic or concussive vestibulopathy",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Concussion-related vestibulopathy",
        "Mapping_Rationale": "Retained as a distinct sports-related persistent post-concussive cohort inside the broader traumatic review group.",
        "Literature_Anchor": LIT["study_specific"],
        "Notes": "",
    },
    "Unilateral vestibular deafferentation due to acoustic neurinoma surgery": {
        "Final_Condition_Normalized": "Unilateral vestibular deafferentation after vestibular schwannoma surgery",
        "Final_Review_Group": "Vestibular schwannoma resection",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Vestibular schwannoma resection or deafferentation",
        "Mapping_Rationale": "Merged with the other unilateral post-surgical deafferentation labels because the cohort state and surgical pathway are the same.",
        "Literature_Anchor": LIT["study_specific"],
        "Notes": "",
    },
    "Unilateral vestibulo-cochlear lesion due to acoustic neuroma surgery": {
        "Final_Condition_Normalized": "Unilateral vestibular deafferentation after vestibular schwannoma surgery",
        "Final_Review_Group": "Vestibular schwannoma resection",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Vestibular schwannoma resection or deafferentation",
        "Mapping_Rationale": "Merged with the other unilateral post-surgical deafferentation labels because the cohort state and surgical pathway are the same.",
        "Literature_Anchor": LIT["study_specific"],
        "Notes": "",
    },
    "Vestibular neuritis": {
        "Final_Condition_Normalized": "Vestibular neuritis",
        "Final_Review_Group": "Unilateral vestibular loss or deafferentation",
        "Default_Cohort_Contrast": "clinical_vs_control_style",
        "Condition_Family_If_Needed": "Acute unilateral vestibular syndromes",
        "Mapping_Rationale": "Retained as vestibular neuritis; the current dataset includes one subgrouped study that should override the default contrast to within_clinical_subgroup_comparison.",
        "Literature_Anchor": LIT["auvp_vn"],
        "Notes": "Study-specific contrast override for zu Eulenburg 2010.",
    },
}


def aggregate_studies(rows: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    studies: dict[str, dict[str, object]] = {}
    for row in rows:
        key = canonical_study_key(row["Author"], row["Year"], row["Title"])
        record = studies.setdefault(
            key,
            {
                "Canonical_Study_Key": key,
                "Author": row["Author"].strip(),
                "Year": row["Year"].strip(),
                "titles": set(),
                "study_ids": set(),
                "etiologies": set(),
                "subtypes": set(),
                "side_deaf_or_lesion": set(),
                "sample_sizes_patients": set(),
                "sample_sizes_controls": set(),
                "rows": 0,
            },
        )
        record["rows"] += 1
        record["titles"].add(norm_space(row["Title"]))
        record["study_ids"].add(row["Study_ID"].strip())
        if row["Etiology"].strip() and row["Etiology"].strip() != "NA":
            record["etiologies"].add(norm_space(row["Etiology"]))
        if row["Subtype"].strip() and row["Subtype"].strip() != "NA":
            record["subtypes"].add(norm_space(row["Subtype"]))
        if row["Side_deaf_or_lesion"].strip() and row["Side_deaf_or_lesion"].strip() != "NA":
            record["side_deaf_or_lesion"].add(norm_space(row["Side_deaf_or_lesion"]))
        if row["Sample_Size_Patients"].strip() and row["Sample_Size_Patients"].strip() != "NA":
            record["sample_sizes_patients"].add(norm_space(row["Sample_Size_Patients"]))
        if row["Sample_Size_Controls"].strip() and row["Sample_Size_Controls"].strip() != "NA":
            record["sample_sizes_controls"].add(norm_space(row["Sample_Size_Controls"]))
    return studies


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with INPUT_CSV.open("r", newline="", encoding="utf-8-sig") as handle:
        source_rows = list(csv.DictReader(handle))

    studies = aggregate_studies(source_rows)
    study_keys = set(studies)
    decision_keys = set(STUDY_DECISIONS)

    if study_keys != decision_keys:
        missing = sorted(study_keys - decision_keys)
        extra = sorted(decision_keys - study_keys)
        raise SystemExit(
            "Study decision coverage mismatch. "
            f"Missing={missing} Extra={extra}"
        )

    decision_rows: list[dict[str, str]] = []
    raw_to_studies: dict[str, list[str]] = defaultdict(list)

    for key in sorted(studies):
        study = studies[key]
        decision = STUDY_DECISIONS[key]
        raw_etiology = display_join(study["etiologies"])
        raw_to_studies[raw_etiology].append(key)

        canonical_title = sorted(study["titles"])[0]
        decision_rows.append(
            {
                "Canonical_Study_Key": key,
                "Author": study["Author"],
                "Year": study["Year"],
                "Canonical_Title": canonical_title,
                "Source_Title_Variants": " || ".join(sorted(study["titles"])),
                "Source_Study_ID_Count": str(len(study["study_ids"])),
                "Source_Study_IDs": "; ".join(sorted(study["study_ids"])),
                "Raw_Etiology": raw_etiology,
                "Raw_Subtype": display_join(study["subtypes"]),
                "Study_Level_Context": summarize_context(study),
                **decision,
            }
        )

    decision_fields = [
        "Canonical_Study_Key",
        "Author",
        "Year",
        "Canonical_Title",
        "Source_Title_Variants",
        "Source_Study_ID_Count",
        "Source_Study_IDs",
        "Raw_Etiology",
        "Raw_Subtype",
        "Study_Level_Context",
        "Proposed_Condition_Normalized",
        "Proposed_Review_Group",
        "Proposed_Cohort_Contrast",
        "Condition_Family_If_Needed",
        "Rationale",
        "Literature_Anchor",
        "Confidence",
        "Open_Question",
    ]
    write_csv(DECISIONS_CSV, decision_fields, decision_rows)

    raw_values = {row["Etiology"].strip() for row in source_rows if row["Etiology"].strip()}
    if raw_values != set(RAW_ETIOLOGY_MAPPING):
        missing = sorted(raw_values - set(RAW_ETIOLOGY_MAPPING))
        extra = sorted(set(RAW_ETIOLOGY_MAPPING) - raw_values)
        raise SystemExit(
            "Raw etiology mapping coverage mismatch. "
            f"Missing={missing} Extra={extra}"
        )

    mapping_rows: list[dict[str, str]] = []
    for raw_etiology in sorted(raw_values):
        spec = RAW_ETIOLOGY_MAPPING[raw_etiology]
        mapping_rows.append(
            {
                "Raw_Etiology": raw_etiology,
                "N_Canonical_Studies": str(len(set(raw_to_studies[raw_etiology]))),
                "Canonical_Study_Keys": "; ".join(sorted(set(raw_to_studies[raw_etiology]))),
                **spec,
            }
        )

    mapping_fields = [
        "Raw_Etiology",
        "N_Canonical_Studies",
        "Canonical_Study_Keys",
        "Final_Condition_Normalized",
        "Final_Review_Group",
        "Default_Cohort_Contrast",
        "Condition_Family_If_Needed",
        "Mapping_Rationale",
        "Literature_Anchor",
        "Notes",
    ]
    write_csv(MAPPING_CSV, mapping_fields, mapping_rows)

    print(f"Wrote {DECISIONS_CSV.relative_to(ROOT.parent)}")
    print(f"Wrote {MAPPING_CSV.relative_to(ROOT.parent)}")
    print(f"Canonical studies: {len(decision_rows)}")
    print(f"Raw etiology values: {len(mapping_rows)}")


if __name__ == "__main__":
    main()
