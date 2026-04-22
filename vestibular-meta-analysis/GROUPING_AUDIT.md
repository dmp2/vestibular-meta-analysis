# Grouping Audit

This document audits the grouping-related columns in [`mycode-11.24/output_with_g.csv`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv) and proposes a replacement for the current use of `Congenital_or_Acquired` in the secondary meta-analysis plots.

## Main Finding

`Congenital_or_Acquired` is not a meaningful analysis grouping variable in this table.

- It has exactly one populated level across all 129 rows: `Acquired`.
- Using it for funnel, Baujat, and forest plots collapses all studies into a single pseudo-group.
- That is inconsistent with the original reference scripts in [`.ref/funnel plot`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/.ref/funnel plot), [`.ref/baujat plot`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/.ref/baujat plot), and [`.ref/forest plot`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/.ref/forest plot), which grouped by `Etiology`.

So the student's `Congenital_or_Acquired` split is not just suboptimal. In this dataset it is functionally wrong.

## Implementation Status

The repo now implements this cautiously at runtime instead of overwriting the student's raw CSV.

- [`meta_plot_helpers.R`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/meta_plot_helpers.R) derives `Condition_Normalized`, `Review_Group`, `Condition_Family`, and `Cohort_Contrast`.
- [`funnel_plots_master.R`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/funnel_plots_master.R) and [`baujat_plots_master.R`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/baujat_plots_master.R) now group by `Review_Group`.
- [`forest_plots_master.R`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/forest_plots_master.R) now groups by `Condition_Normalized`.
- [`validate_workflow.py`](/C:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/validate_workflow.py) mirrors those derived fields without modifying the checked-in CSVs.

This was done deliberately so the original extraction remains intact and any residual cohort-design signal, including possible patient-vs-control style structure, is not thrown away prematurely.

## Relevant Columns

The condition-related columns are:

- `Etiology`
- `Subtype`
- `Congenital_or_Acquired`
- `Side_deaf_or_lesion`

What they actually encode:

- `Etiology` is the primary study-condition label.
- `Subtype` adds within-condition details for a minority of studies.
- `Congenital_or_Acquired` is effectively a constant and is not useful for analysis.
- `Side_deaf_or_lesion` describes lesion laterality or cohort composition, not disease class.

## Raw `Etiology` Values

The checked-in table currently contains 16 raw `Etiology` labels:

1. `Vestibular neuritis`
2. `Acute unilateral peripheral vestibular neuritis`
3. `Post-concussive vestibular dysfunction`
4. `Mild traumatic brain injury with vestibular symptoms`
5. `Sports-related concussion with persistent post-concussive symptoms`
6. `Bilateral vestibular loss`
7. `Bilateral vestibular failure`
8. `Bilateral vestibulopathy`
9. `Chronic bilateral vestibular loss due to neurofibromatosis 2 after bilateral vestibular neurectomy`
10. `Unilateral vestibulo-cochlear lesion due to acoustic neuroma surgery`
11. `Unilateral vestibular deafferentation due to acoustic neurinoma surgery`
12. `Chronic complete unilateral vestibular deafferentation due to vestibular schwannoma removal`
13. `Peripheral vestibular dysfunction`
14. `Meniere's disease`
15. `Persistent postural perceptual dizziness`
16. `Long-term vestibular adaptation in professional ballet dancers`

These are much closer to the real scientific grouping structure than `Congenital_or_Acquired`.

## Study-Level Reality

At the study/title level, the table spans a mix of:

- vestibular neuritis studies
- concussion/post-concussive vestibular dysfunction studies
- bilateral vestibular loss/failure/vestibulopathy studies
- unilateral post-surgical vestibular deafferentation studies
- peripheral vestibular dysfunction studies
- Meniere's disease studies
- PPPD
- one non-clinical adaptation cohort in professional ballet dancers

This is why the current two-level acquired/congenital framing feels wrong: the real heterogeneity is clinical condition, not developmental status.

## Why A Direct Swap To Raw `Etiology` Is Not Enough

Replacing `Congenital_or_Acquired` with raw `Etiology` is scientifically closer to the truth, but it is not sufficient as an implementation strategy.

Reason:

- The raw `Etiology` labels include wording variants that are really the same disease family.
- Funnel and Baujat require enough variance-bearing rows to fit a meta-analytic model.
- Exact-condition grouping will often be too sparse for these plots.

So the repo should not move from one bad field to one rigid field. It should move to an explicit multi-level grouping design.

## Review-Scope Context

Your survey scope is broader than the currently observed raw `Etiology` strings. The review framework you described includes:

1. bilateral vestibulopathy
2. unilateral vestibular loss/deafferentation
3. Meniere's disease
4. vestibular migraine
5. post-traumatic/concussive vestibulopathy
6. white matter disease/small-vessel lesions
7. stroke/ischemic lesions in vestibular circuits
8. chronic/mild vestibulopathy
9. vestibular experts
10. healthy adults (younger vs older)
11. spaceflight-related vestibular adaptations
12. vestibular schwannoma resection

That means the grouping system should be anchored to the review design, not only to the current CSV wording.

It also means the checked-in table may underrepresent parts of the intended review frame. Based on the current rows, the following survey categories are not clearly present as explicit cohorts:

- vestibular migraine
- white matter disease/small-vessel lesions
- stroke/ischemic vestibular-circuit lesions
- healthy aging
- spaceflight-related vestibular adaptation

So there are two distinct tasks:

1. build a correct grouping system for the rows that are currently present
2. keep the schema broad enough to absorb additional in-scope cohorts later without refactoring again

## Proposed Replacement Design

Do not overwrite the original columns. Keep `Etiology`, `Subtype`, and `Congenital_or_Acquired` for provenance.

Add three derived grouping fields:

1. `Condition_Normalized`
   This is the corrected condition-level label to use for descriptive summaries and condition-aware outputs.

2. `Review_Group`
   This is the review-defined grouping field aligned to your literature survey categories.

3. `Condition_Family`
   This is the broader analysis family to use when exact conditions are too sparse for funnel/Baujat-style modeling.

## Proposed `Review_Group` Levels

This is the field that should drive the scientific framing of the repository because it reflects your actual review question.

Proposed levels:

1. `Bilateral vestibulopathy`
2. `Unilateral vestibular loss or deafferentation`
3. `Meniere's disease`
4. `Vestibular migraine`
5. `Post-traumatic or concussive vestibulopathy`
6. `White matter disease or small-vessel lesions`
7. `Stroke or ischemic vestibular-circuit lesions`
8. `Chronic or mild vestibulopathy`
9. `Vestibular experts`
10. `Healthy aging`
11. `Spaceflight-related vestibular adaptation`
12. `Vestibular schwannoma resection`
13. `Other vestibular clinical cohorts`
14. `Unclassified or needs review`

This field should exist even if some levels are currently empty in the checked-in table. Empty levels are acceptable because they represent review scope, not just present data.

## Proposed `Condition_Normalized` Levels

This is the concrete replacement for the current pseudo-grouping logic. It preserves clinically meaningful distinctions while collapsing only obvious wording variants.

Proposed normalized levels:

1. `Vestibular neuritis`
   Raw labels collapsed:
   `Vestibular neuritis`
   `Acute unilateral peripheral vestibular neuritis`

2. `Post-concussive vestibular dysfunction`

3. `Mild traumatic brain injury with vestibular symptoms`

4. `Sports-related concussion with persistent post-concussive symptoms`

5. `Bilateral vestibular loss`

6. `Bilateral vestibular failure`

7. `Bilateral vestibulopathy`

8. `NF2 bilateral vestibular loss after neurectomy`
   Raw label:
   `Chronic bilateral vestibular loss due to neurofibromatosis 2 after bilateral vestibular neurectomy`

9. `Unilateral vestibular deafferentation after vestibular schwannoma surgery`
   Raw labels collapsed:
   `Unilateral vestibulo-cochlear lesion due to acoustic neuroma surgery`
   `Unilateral vestibular deafferentation due to acoustic neurinoma surgery`
   `Chronic complete unilateral vestibular deafferentation due to vestibular schwannoma removal`

10. `Peripheral vestibular dysfunction`

11. `Meniere's disease`

12. `Persistent postural perceptual dizziness`

13. `Professional ballet dancers`
   This should remain distinct because it is not a patient disease cohort.

This yields 13 normalized condition levels, which matches your recollection much better than the current all-`Acquired` field.

## Proposed Mapping From `Condition_Normalized` To `Review_Group`

This is the concrete bridge from the observed table to the review design.

- `Vestibular neuritis`
  -> `Unilateral vestibular loss or deafferentation`

- `Post-concussive vestibular dysfunction`
  -> `Post-traumatic or concussive vestibulopathy`

- `Mild traumatic brain injury with vestibular symptoms`
  -> `Post-traumatic or concussive vestibulopathy`

- `Sports-related concussion with persistent post-concussive symptoms`
  -> `Post-traumatic or concussive vestibulopathy`

- `Bilateral vestibular loss`
  -> `Bilateral vestibulopathy`

- `Bilateral vestibular failure`
  -> `Bilateral vestibulopathy`

- `Bilateral vestibulopathy`
  -> `Bilateral vestibulopathy`

- `NF2 bilateral vestibular loss after neurectomy`
  -> `Bilateral vestibulopathy`
  or `Vestibular schwannoma resection`

This is the one ambiguous case. If you want the review to emphasize causal context, place it under `Vestibular schwannoma resection`. If you want it grouped by physiologic vestibular state, place it under `Bilateral vestibulopathy`. I would keep a separate flag for surgical context if you choose the latter.

- `Unilateral vestibular deafferentation after vestibular schwannoma surgery`
  -> `Vestibular schwannoma resection`

- `Peripheral vestibular dysfunction`
  -> `Chronic or mild vestibulopathy`
  or `Other vestibular clinical cohorts`

This depends on whether you want to reserve `Chronic or mild vestibulopathy` for less precisely specified peripheral cohorts. Given the current data, that is probably the best fit.

- `Meniere's disease`
  -> `Meniere's disease`

- `Persistent postural perceptual dizziness`
  -> `Other vestibular clinical cohorts`
  or its own future `PPPD` review group

PPPD is diagnostically well established and may deserve its own review group if more rows are added later.

- `Professional ballet dancers`
  -> `Vestibular experts`

## Proposed `Condition_Family` Levels

This is the field I would actually use as the first replacement in funnel and Baujat code, because those methods need broader aggregation.

1. `Vestibular neuritis`
   Covers normalized:
   `Vestibular neuritis`

2. `Concussion-related vestibular dysfunction`
   Covers normalized:
   `Post-concussive vestibular dysfunction`
   `Mild traumatic brain injury with vestibular symptoms`
   `Sports-related concussion with persistent post-concussive symptoms`

3. `Bilateral vestibular loss syndromes`
   Covers normalized:
   `Bilateral vestibular loss`
   `Bilateral vestibular failure`
   `Bilateral vestibulopathy`
   `NF2 bilateral vestibular loss after neurectomy`

4. `Unilateral post-surgical vestibular deafferentation`
   Covers normalized:
   `Unilateral vestibular deafferentation after vestibular schwannoma surgery`

5. `Peripheral vestibular dysfunction`

6. `Meniere's disease`

7. `Persistent postural perceptual dizziness`

8. `Vestibular adaptation / non-clinical`
   Covers normalized:
   `Professional ballet dancers`

## Literature-Guided Coarsening

If you later need to coarsen the labels beyond `Condition_Normalized`, that coarsening should follow recognized clinical entities where such entities exist.

The main principle should be:

- keep exact study conditions in `Condition_Normalized`
- keep review-scope bins in `Review_Group`
- use `Condition_Family` as the minimum coarsening needed for sparse modeling

For several of your categories, consensus-style disease entities already exist in the literature. That makes them better coarsening anchors than ad hoc student labels.

Examples:

- `Vestibular neuritis` can be anchored to the modern Barany concept of acute unilateral vestibulopathy / vestibular neuritis.
- `Bilateral vestibulopathy` should preferentially use the Barany term `bilateral vestibulopathy` rather than mixing `loss`, `failure`, and `vestibulopathy` without a rule.
- `Meniere's disease` already has consensus diagnostic criteria and should remain its own entity.
- `Vestibular migraine` should remain its own entity if it enters the table later.
- `Persistent postural perceptual dizziness` is a recognized diagnostic entity and should not be silently collapsed into generic chronic dizziness if you later add more PPPD rows.
- `Healthy aging` and `Vestibular experts` are not disease entities, so these should remain review-design categories rather than clinical diagnoses.
- `Spaceflight-related vestibular adaptation` is also a study-context category, not a standard clinic diagnosis.

So the future coarsening rule should be:

- use consensus clinical entities where they exist
- use review-design exposure/context groups where they do not

This avoids mixing disease nosology with study-population design.

## Recommended Use By Output Type

Use different grouping fields for different jobs.

### Descriptive counts and study inventory

Use `Review_Group` by default, with optional drill-down to `Condition_Normalized`.

Reason:

- this is where your literature-survey framework matters most
- it keeps the repository aligned to the way the studies were actually selected
- `Condition_Normalized` can still be used when you want finer within-group inspection

### Forest plots

Start with `Condition_Normalized`, but report or facet within `Review_Group` when useful.

Reason:

- forest plots can tolerate smaller groups better than funnel/Baujat
- they are a reasonable place to show condition-specific results, even when exact conditions are sparse

### Funnel and Baujat

Start with `Review_Group`. Fall back to `Condition_Family` only if `Review_Group` remains too sparse for model fitting.

Reason:

- exact conditions will often be too sparse
- `Review_Group` is closer to your scientific review question than the raw student field
- `Condition_Family` should be a sparse-data fallback, not the first semantic layer

## Important Caution

Changing the grouping field will not automatically make funnel/Baujat dense.

The current table is intrinsically sparse in variance-bearing rows:

- many studies have effect sizes but no variance
- many studies have confidence intervals but no variance
- several conditions are represented by a single study

So the likely outcome is:

- condition-level forest outputs become scientifically cleaner
- funnel/Baujat may remain sparse, but for valid reasons
- any remaining sparsity will then reflect data reality rather than a mislabeled grouping field

## Recommended Implementation Order

1. Add derived grouping columns without deleting or overwriting original columns.
2. Implement the explicit mapping from raw `Etiology` to `Condition_Normalized` and `Review_Group`.
3. Add optional `Condition_Family` coarsening for sparse-model use.
4. Update validation/audit code to report counts by all three derived grouping fields.
5. Update forest plots to group by `Condition_Normalized`, with `Review_Group` available for filtering or faceting.
6. Update funnel and Baujat to try `Review_Group` first and fall back to `Condition_Family` when needed.
7. Regenerate outputs and reevaluate which groups are model-eligible.

## When To Open The PR

Do not open the grouping PR yet if all you have is the suspicion that the current grouping is wrong.

Open the PR when the branch contains all of the following:

1. This audit and the accepted mapping table.
2. The derived grouping fields implemented in code.
3. The plot scripts updated to use the new grouping fields.
4. Regenerated outputs and refreshed audit/validation artifacts.
5. Documentation that explains why `Congenital_or_Acquired` is no longer the operative analysis grouping.
6. A short justification for any `Condition_Family` coarsening decisions that cites either review-scope logic or consensus clinical entities.

That is the point where review becomes concrete rather than speculative.

## Recommendation

The next branch should implement a three-level grouping system:

- `Condition_Normalized` as the corrected study-condition field
- `Review_Group` as the literature-survey field
- `Condition_Family` as the broader sparse-modeling field

That is better than both of the alternatives:

- better than keeping `Congenital_or_Acquired`
- better than blindly swapping every script to raw `Etiology`
