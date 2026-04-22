# Scientific Grouping Audit

This document is the authoritative scientific mapping spec for the grouping fields currently used in the secondary meta-analysis workflow.

It supplements, and now supersedes for scientific interpretation, the earlier implementation-focused proposals in [`GROUPING_AUDIT.md`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/GROUPING_AUDIT.md).

## Scope And Inputs

The audit is based on the preserved historical table [`mycode-11.24/output_with_g.csv`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv).

Scientific grouping decisions were made at the study level, not the ROI-row level.

The top-layer review frame is now also crosschecked against the source workbook in [`WORKBOOK_REVIEW_FRAME_AUDIT.md`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/WORKBOOK_REVIEW_FRAME_AUDIT.md). That workbook crosswalk is useful for auditing missing or reserved review bins, but it does not replace the checked-in extraction table as the runtime analysis input.

- Source table: 129 ROI rows
- Canonical studies after study/title reconciliation: 19
- One explicit title reconciliation was required:
  Cheng 2023 appeared as both `vestibular neuronitis` and `vestibular neuritis` and was treated as one study

Generated supporting artifacts:

- Study-level decision table: [`scientific_grouping_decisions.csv`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/scientific_grouping_decisions.csv)
- Raw-etiology mapping table: [`scientific_grouping_mapping.csv`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/scientific_grouping_mapping.csv)
- Generator: [`audit_scientific_grouping.py`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/audit_scientific_grouping.py)

## Final Semantics

### `Condition_Normalized`

This is the condition-entity label for the specific cohort actually studied.

- It stays fairly fine-grained.
- It preserves clinically distinct present-day entities when the source paper distinguishes them.
- It collapses only obvious nomenclature variants that refer to the same entity.
- It does not absorb study-design information such as expertise cohorts or subgroup structure.

### `Review_Group`

This is the top-layer review bin aligned to the literature-survey design.

- It is broader than `Condition_Normalized`.
- It may reflect causal or review-context framing where that is part of the survey question.
- It may include levels that are currently empty in the checked-in subset if those levels belong to the review protocol.

### `Cohort_Contrast`

This is a study-design field, not a disease label.

- It describes how the cohort comparison is structured.
- It is orthogonal to diagnosis/entity.
- It is retained as a first-class field because later filtering, sensitivity analysis, or descriptive stratification may depend on it.

Locked values:

1. `clinical_vs_control_style`
2. `expertise_vs_control`
3. `healthy_subgroup_comparison`
4. `adaptation_or_exposure_comparison`
5. `within_clinical_subgroup_comparison`
6. `unclear_or_nonstandard`

Only four of those are used in the current checked-in subset:

- `clinical_vs_control_style`
- `expertise_vs_control`
- `within_clinical_subgroup_comparison`
- `unclear_or_nonstandard`

### `Condition_Family`

This is the optional sparse-modeling fallback.

- It is broader than `Condition_Normalized`.
- It should only be used when exact conditions are too sparse for a model or when a broader mechanistic family is required.
- It should not replace `Review_Group` as the main scientific framing layer.

## Final Review-Group Taxonomy

These are the authoritative `Review_Group` levels for this project.

1. `Bilateral vestibulopathy`
2. `Unilateral vestibular loss or deafferentation`
3. `Meniere's disease`
4. `Vestibular migraine`
5. `Post-traumatic or concussive vestibulopathy`
6. `White matter disease or small-vessel lesions`
7. `Stroke or ischemic vestibular-circuit lesions`
8. `Chronic or mild vestibulopathy`
9. `Vestibular experts`
10. `Healthy non-clinical cohorts`
11. `Healthy aging`
12. `Spaceflight-related vestibular adaptation`
13. `Vestibular schwannoma resection`
14. `Other vestibular clinical cohorts`
15. `Unclassified or needs review`

Even though several of these are currently empty in the checked-in subset, they should remain part of the scientific taxonomy because they are part of the intended review frame.

## Resolved Scientific Decisions

### Vestibular neuritis and acute unilateral peripheral vestibular neuritis

Resolved to one normalized condition:

- `Vestibular neuritis`

Reason:

- current consensus language supports treating vestibular neuritis and acute unilateral vestibulopathy as the same clinical entity rather than separate diseases
- the more specific source wording is preserved in raw `Etiology`, `Subtype`, and study context

Anchor:

- Strupp et al. 2022, Barany acute unilateral vestibulopathy / vestibular neuritis consensus
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9661346/

### Bilateral vestibular loss, bilateral vestibular failure, bilateral vestibulopathy

Resolved to three distinct normalized conditions:

- `Bilateral vestibular loss`
- `Bilateral vestibular failure`
- `Bilateral vestibulopathy`

All three map to one review group:

- `Bilateral vestibulopathy`

Reason:

- the current dataset uses these as distinct cohort labels
- the audit is conservative at the condition layer
- broader pooling, if needed, belongs in `Review_Group` or `Condition_Family`, not in forced early collapse

Anchor:

- Strupp et al. 2017, Barany bilateral vestibulopathy criteria
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9249284/

### Concussion-related labels

These remain distinct at `Condition_Normalized`:

- `Post-concussive vestibular dysfunction`
- `Mild traumatic brain injury with vestibular symptoms`
- `Sports-related concussion with persistent post-concussive symptoms`

All map to:

- `Post-traumatic or concussive vestibulopathy`

Reason:

- the extracted studies are not interchangeable cohorts
- condition-level conservatism matters more than forcing plot density

### Schwannoma and deafferentation labels

The three unilateral surgical labels are merged to:

- `Unilateral vestibular deafferentation after vestibular schwannoma surgery`

They map to:

- `Vestibular schwannoma resection`

The NF2 bilateral postoperative study is resolved as:

- `Condition_Normalized = NF2 bilateral vestibular loss after neurectomy`
- `Review_Group = Vestibular schwannoma resection`
- `Condition_Family = Bilateral vestibular syndromes`

Reason:

- the review explicitly included vestibular schwannoma resection
- the unilateral surgical cohorts are clearly one causal-context family
- the NF2 study is best framed by surgical cause at the top layer, while its bilateral vestibular physiology is preserved in the fallback family layer

### Peripheral vestibular dysfunction

Resolved as:

- `Condition_Normalized = Peripheral vestibular dysfunction`
- `Review_Group = Chronic or mild vestibulopathy`

Reason:

- the source study explicitly mixes bilateral and unilateral peripheral cohorts
- the audit should not invent a narrower diagnosis than the paper itself supports
- the review-group placement is the closest fit to the survey design, not a claim that this is a single consensus disease entity

### PPPD

Resolved as:

- `Condition_Normalized = Persistent postural perceptual dizziness`
- `Review_Group = Other vestibular clinical cohorts`
- `Condition_Family = Functional vestibular disorders`

Reason:

- PPPD is a recognized diagnostic entity and should remain distinct
- it was not one of the original named top-level survey categories, so it remains in the residual review bucket for now

Anchor:

- Staab et al. 2017, Barany PPPD criteria
  https://pubmed.ncbi.nlm.nih.gov/29036855/

### Meniere's disease

Resolved as:

- `Condition_Normalized = Meniere's disease`
- `Review_Group = Meniere's disease`

Reason:

- normalize spelling and diacritics only
- keep the disease entity intact
- retain unilateral or mixed unilateral/bilateral composition in context or subtype, not in the normalized name

Anchor:

- Lopez-Escamez et al. 2015 diagnostic criteria for Meniere's disease
  https://pubmed.ncbi.nlm.nih.gov/25882471/

### Professional ballet dancers

Resolved as:

- `Condition_Normalized = Professional ballet dancers`
- `Review_Group = Vestibular experts`
- `Cohort_Contrast = expertise_vs_control`

Reason:

- this is a non-clinical expertise cohort
- it should not be absorbed into disease nosology

### Healthy non-clinical cohorts versus healthy aging

Resolved as:

- `Healthy aging` remains the review bin for age-comparison and age-related normative vestibular cohorts
- `Healthy non-clinical cohorts` is added as a separate review bin for generic healthy adults, healthy young adults, and training-based non-clinical cohorts that are not primarily aging comparisons

Reason:

- the source workbook contains healthy and training cohorts that are in-scope for the broader review frame but are not well represented by the narrower `Healthy aging` label
- keeping these bins separate preserves the ontology: aging comparisons remain distinct from other healthy non-clinical designs
- both review bins still roll up naturally to the broader non-clinical `Condition_Family` layer when sparse modeling requires it

## Cohort-Contrast Rules

The audit uses these decision rules for `Cohort_Contrast`:

- Use `clinical_vs_control_style` when the study presents a conventional patient/cohort versus control structure and the checked-in extraction supports both sides.
- Use `expertise_vs_control` for non-clinical expertise cohorts such as professional dancers.
- Use `healthy_subgroup_comparison` for healthy or age-related subgroup comparisons where the design is fundamentally a healthy-group contrast rather than a patient-versus-control study.
- Use `adaptation_or_exposure_comparison` for non-clinical training or exposure-defined cohorts such as balance-training or spaceflight studies.
- Use `within_clinical_subgroup_comparison` when the extraction clearly preserves subgrouped clinical contrasts or multiple patient subgroup structures rather than one simple case-control design.
- Use `unclear_or_nonstandard` when the checked-in extraction does not support a defensible comparison label without re-opening the source paper.

Specific current examples:

- `within_clinical_subgroup_comparison`
  was assigned to the subgrouped vestibular neuritis study by zu Eulenburg 2010 and to the mixed peripheral vestibular dysfunction study by Schone 2022.
- `unclear_or_nonstandard`
  was assigned to Hufner 2009 because the checked-in table lacks a control sample size and the audit should not infer one.

## Handling Rules

### Spelling and title variants

- Normalize obvious nomenclature variants that do not change the underlying condition entity.
- Preserve the source wording in raw fields and study context.
- For study reconciliation, title-level spelling variants can be merged when author, year, condition, and sample structure all support a single underlying paper.

### Diacritics

- Normalize diacritics in the scientific abstraction fields when the goal is entity standardization, for example by standardizing accented source spellings of Meniere's disease to the canonical `Meniere's disease` label.
- Preserve original source spelling in raw fields where possible.

### Surgical cause versus physiologic state

- Use `Review_Group` to capture the review-relevant causal context when that context is part of the survey design.
- Use `Condition_Family` to preserve broader physiologic affinity when that matters for sparse-modeling fallback.

### Non-clinical cohorts

- Keep non-clinical cohorts outside disease nosology at `Condition_Normalized`.
- Place them into review-design categories such as `Vestibular experts`, `Healthy non-clinical cohorts`, and `Healthy aging`.

### Missing or unclear controls

- Do not infer a case-control design from disease class alone.
- If the checked-in extraction does not support a clear comparison structure, mark it explicitly in `Cohort_Contrast`.

## Raw-Etiology Mapping Table

The authoritative raw-to-final mapping is tracked in [`scientific_grouping_mapping.csv`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/scientific_grouping_mapping.csv).

At a high level:

| Raw `Etiology` pattern | Final `Condition_Normalized` | Final `Review_Group` |
| --- | --- | --- |
| `Vestibular neuritis` | `Vestibular neuritis` | `Unilateral vestibular loss or deafferentation` |
| `Acute unilateral peripheral vestibular neuritis` | `Vestibular neuritis` | `Unilateral vestibular loss or deafferentation` |
| `Post-concussive vestibular dysfunction` | `Post-concussive vestibular dysfunction` | `Post-traumatic or concussive vestibulopathy` |
| `Mild traumatic brain injury with vestibular symptoms` | `Mild traumatic brain injury with vestibular symptoms` | `Post-traumatic or concussive vestibulopathy` |
| `Sports-related concussion with persistent post-concussive symptoms` | `Sports-related concussion with persistent post-concussive symptoms` | `Post-traumatic or concussive vestibulopathy` |
| `Bilateral vestibular loss` | `Bilateral vestibular loss` | `Bilateral vestibulopathy` |
| `Bilateral vestibular failure` | `Bilateral vestibular failure` | `Bilateral vestibulopathy` |
| `Bilateral vestibulopathy` | `Bilateral vestibulopathy` | `Bilateral vestibulopathy` |
| `Chronic bilateral vestibular loss due to neurofibromatosis 2 after bilateral vestibular neurectomy` | `NF2 bilateral vestibular loss after neurectomy` | `Vestibular schwannoma resection` |
| `Unilateral vestibulo-cochlear lesion due to acoustic neuroma surgery` | `Unilateral vestibular deafferentation after vestibular schwannoma surgery` | `Vestibular schwannoma resection` |
| `Unilateral vestibular deafferentation due to acoustic neurinoma surgery` | `Unilateral vestibular deafferentation after vestibular schwannoma surgery` | `Vestibular schwannoma resection` |
| `Chronic complete unilateral vestibular deafferentation due to vestibular schwannoma removal` | `Unilateral vestibular deafferentation after vestibular schwannoma surgery` | `Vestibular schwannoma resection` |
| `Peripheral vestibular dysfunction` | `Peripheral vestibular dysfunction` | `Chronic or mild vestibulopathy` |
| `Meniere's disease` spelling variants | `Meniere's disease` | `Meniere's disease` |
| `Persistent postural perceptual dizziness` | `Persistent postural perceptual dizziness` | `Other vestibular clinical cohorts` |
| `Long-term vestibular adaptation in professional ballet dancers` | `Professional ballet dancers` | `Vestibular experts` |

## Relationship To The Current Plot Workflow

This scientific audit now governs the current runtime grouping code.

The shared runtime helper and validator have been aligned to this specification.

Current intended behavior remains:

- `forest` should remain condition-led
- `funnel` and `Baujat` should remain broader-group-led
- `Cohort_Contrast` should remain available for filtering, sensitivity analysis, or descriptive stratification

If a later code pass changes runtime mappings again, this document should remain the source of truth that governs those changes.

## Acceptance Check

This audit satisfies the current scientific acceptance requirements:

- every canonical study has exactly one proposed `Condition_Normalized`
- every canonical study has exactly one proposed `Review_Group`
- every canonical study has exactly one proposed `Cohort_Contrast`
- every currently observed raw `Etiology` value is mapped
- grouping decisions are study-level, not ROI-row-level
- each merged or split decision has a written rationale
- consensus anchors are used when a recognized consensus entity exists
