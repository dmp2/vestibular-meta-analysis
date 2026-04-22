# Workbook Review-Frame Audit

This document crosswalks the original workbook review frame against the current scientific grouping audit and runtime taxonomy.

## Inputs

- Source workbook: `C:\Users\dpado\Documents\jhu\Oto-HNS\meta_analysis\meta_analysis_vestibular_gm_wm.xlsx`
- Checked-in scientific mapping source: `scientific_grouping_decisions.csv`

## Summary

- Workbook study-condition pairs: 86
- Unique workbook studies: 66
- Unique workbook condition labels: 61
- Condition labels covered directly by the current runtime taxonomy: 57
- Condition labels suggesting taxonomy expansion: 0
- Condition labels requiring manual review because they are composite or ambiguous: 3
- Condition labels that should not drive runtime grouping as written: 1

## Main Findings

- The workbook strongly supports retaining the current clinical review bins for bilateral vestibular disorders, unilateral peripheral loss, schwannoma-related deafferentation, traumatic vestibulopathy, Meniere's disease, vestibular migraine, vascular or ischemic cohorts, white-matter disease, vestibular experts, and spaceflight adaptation.
- The workbook supports separating age-comparison cohorts from other healthy or training-based non-clinical cohorts. `Healthy aging` should stay narrow, while generic healthy adults and training cohorts can be incorporated through a broader `Healthy non-clinical cohorts` review bin.
- The workbook contains mixed or composite labels such as `vestibular neuritis + cerebral small vessel disease` and `bilateral vestibulopathy (bvp), "vestibular experts"`. Those labels are scientifically useful context, but they should not be used directly as runtime grouping values.
- Several review-protocol categories are supported by the workbook even though they are absent or sparse in the checked-in CSV subset. That means the top-layer taxonomy should continue to reflect the review protocol, not only the currently instantiated extraction rows.

## Proposed Review-Group Coverage

- Bilateral vestibulopathy: 3 workbook condition labels
- Chronic or mild vestibulopathy: 2 workbook condition labels
- Healthy aging: 8 workbook condition labels
- Healthy non-clinical cohorts: 3 workbook condition labels
- Meniere's disease: 3 workbook condition labels
- Needs manual scope decision: 3 workbook condition labels
- Needs split across vestibular and vascular axes: 1 workbook condition labels
- Other vestibular clinical cohorts: 3 workbook condition labels
- Post-traumatic or concussive vestibulopathy: 5 workbook condition labels
- Spaceflight-related vestibular adaptation: 2 workbook condition labels
- Stroke or ischemic vestibular-circuit lesions: 12 workbook condition labels
- Unilateral vestibular loss or deafferentation: 5 workbook condition labels
- Vestibular experts: 3 workbook condition labels
- Vestibular migraine: 2 workbook condition labels
- Vestibular schwannoma resection: 5 workbook condition labels
- White matter disease or small-vessel lesions: 1 workbook condition labels

## Covered But Not Yet Represented In The Checked-In CSV

- `acute vestibular neuritis recovery` -> `Unilateral vestibular loss or deafferentation`
- `age-related saccular loss` -> `Healthy aging`
- `age-related saccular, utricular, and horizontal semicircular canal loss` -> `Healthy aging`
- `brainstem / cerebellar stroke` -> `Stroke or ischemic vestibular-circuit lesions`
- `cerebellar infarction` -> `Stroke or ischemic vestibular-circuit lesions`
- `cerebellar lesion` -> `Stroke or ischemic vestibular-circuit lesions`
- `chronic tinnitus after vestibular schwannoma resection` -> `Vestibular schwannoma resection`
- `chronic, mild vestibulopathy` -> `Chronic or mild vestibulopathy`
- `healthy adults` -> `Healthy non-clinical cohorts`
- `healthy adults (balance training)` -> `Healthy non-clinical cohorts`
- `healthy older adults` -> `Healthy aging`
- `healthy young adults` -> `Healthy non-clinical cohorts`
- `healthy young vs healthy older adults` -> `Healthy aging`
- `healthy young vs. healthy older adults` -> `Healthy aging`
- `healthy younger & older adults` -> `Healthy aging`
- `healthy younger vs. older` -> `Healthy aging`
- `healthy younger vs. older adults` -> `Healthy aging`
- `idiopathic dizziness in older adults` -> `Other vestibular clinical cohorts`
- `infarcts of the subcortical vestibular circuitry` -> `Stroke or ischemic vestibular-circuit lesions`
- `lateral medullary (wallenberg) syndrome` -> `Stroke or ischemic vestibular-circuit lesions`

## Taxonomy Expansion Candidates

- None. The current runtime taxonomy now has a `Healthy non-clinical cohorts` review layer for these workbook labels.

## Manual-Review Labels

- `bilateral vestibulopathy (bvp), "vestibular experts"`: This label appears to combine a patient cohort and a non-clinical expert cohort in one workbook entry.
- `healthy + lesion or normal variants`: This workbook label mixes lesion and normative states and should be resolved manually before any runtime use.
- `vestibular neuritis + cerebral small vessel disease`: This label spans two different scientific axes and should not be imported as a single runtime group value.
- `review or combined study on op2 region`: This label describes a review or composite framing rather than a single empirical vestibular cohort and should not drive runtime grouping.

## Recommendation

- Keep the current runtime grouping logic unchanged for the checked-in subset.
- Use the workbook as the scientific reference frame for whether top-layer review bins are missing or misnamed.
- Keep `Healthy aging` for age-comparison cohorts and route generic healthy or training-based cohorts through `Healthy non-clinical cohorts` when those studies are added to the extraction table.

## Machine-Readable Crosswalk

- See `workbook_review_frame_crosswalk.csv` for the full workbook-condition crosswalk.
