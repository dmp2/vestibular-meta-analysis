# Secondary Meta-Plot Runbook

These scripts cover the non-brain plots reconstructed from the colleague's adapted code.

## Canonical Input

- Historical secondary-plot table: [`mycode-11.24/output_with_g.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv)
- Recomputed secondary-plot table: [`mycode-11.24/output_with_g_computed.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g_computed.csv)
- Reconciliation layer: [`meta_plot_helpers.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/meta_plot_helpers.R)

The secondary plot masters now use a hybrid policy:

- preserve historical `Hedges_g_variance` and CI fields when present
- fall back to recomputed `Hedges_g_exact` when the historical value is missing
- require identical composite keys across historical and recomputed tables

They also now use derived grouping fields instead of the student's all-`Acquired` split:

- funnel and Baujat group by `Review_Group`
- forest groups by `Condition_Normalized`
- `Cohort_Contrast` preserves whether a row still looks like a clinical-vs-control style comparison versus an expertise, aging, or exposure design

## Commands

From the workspace root:

```powershell
Rscript vestibular-meta-analysis/funnel_plots_master.R
Rscript vestibular-meta-analysis/baujat_plots_master.R
Rscript vestibular-meta-analysis/forest_plots_master.R
```

## Expected Outputs

The output names are now dynamic because they are driven by derived grouping fields.

Funnel plots when a `Review_Group` x region subset has at least 2 rows with `Hedges_g_exact` and `Hedges_g_variance` after reconciliation:

- `mycode-11.24/funnel_review_group_<group_slug>_cortex.png`
- `mycode-11.24/funnel_review_group_<group_slug>_subcortex.png`

Baujat plots when a `Review_Group` x region subset has at least 2 rows with `Hedges_g_exact` and `Hedges_g_variance` after reconciliation:

- `mycode-11.24/baujat_review_group_<group_slug>_cortex.png`
- `mycode-11.24/baujat_review_group_<group_slug>_subcortex.png`

Forest plots when a `Condition_Normalized` subgroup has at least 1 row with `Hedges_g_exact`, `CI_lower`, and `CI_upper` after reconciliation:

- `mycode-11.24/forest/forest_condition_normalized_<group_slug>.png`
- `mycode-11.24/forest/forest_condition_normalized_<group_slug>.svg`

Run [`validate_workflow.py`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/validate_workflow.py) to see the exact current output list for the checked-in tables.

Current checked-in table reality from the validator:

- funnel and Baujat are currently eligible only for `Review_Group = Post-traumatic or concussive vestibulopathy` in the `subcortex` subset
- forest is currently eligible for `Condition_Normalized = Vestibular neuritis`
- forest is currently eligible for `Condition_Normalized = Bilateral vestibular failure`
- forest is currently eligible for `Condition_Normalized = Mild traumatic brain injury with vestibular symptoms`

## Notes

- The funnel master is based on [`mycode-11.24/funnelt2.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/funnelt2.R).
- Funnel and Baujat use `metafor::rma(..., method = "REML")`, matching the original random-effects model family.
- The funnel and Baujat masters no longer write placeholder files. They either save a real plot or skip the target with an explicit console reason.
- The forest master is R-based for consistency with the rest of the repo and now produces a table-style layout modeled on the original forest reference.
- Forest plots are CI-driven, not variance-driven. They can therefore be available for groups that are still ineligible for funnel/Baujat.
- `Cohort_Contrast` is intentionally retained so the repo does not throw away possible control-vs-patient style signal from the student's original extraction just because the labels were crude.
- Run [`validate_workflow.py`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/validate_workflow.py) first if you want a non-R readout of current grouped eligibility and exact expected output filenames.
