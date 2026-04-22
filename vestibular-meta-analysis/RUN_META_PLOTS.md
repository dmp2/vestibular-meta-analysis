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

## Commands

From the workspace root:

```powershell
Rscript vestibular-meta-analysis/funnel_plots_master.R
Rscript vestibular-meta-analysis/baujat_plots_master.R
Rscript vestibular-meta-analysis/forest_plots_master.R
```

## Expected Outputs

Funnel plots when a subgroup has at least 2 rows with `Hedges_g_exact` and `Hedges_g_variance` after reconciliation:

- `mycode-11.24/funnel_acquired_cortex.png`
- `mycode-11.24/funnel_acquired_subcortex.png`
- `mycode-11.24/funnel_congenital_cortex.png`
- `mycode-11.24/funnel_congenital_subcortex.png`

Baujat plots when a subgroup has at least 2 rows with `Hedges_g_exact` and `Hedges_g_variance` after reconciliation:

- `mycode-11.24/baujat_acquired_cortex.png`
- `mycode-11.24/baujat_acquired_subcortex.png`
- `mycode-11.24/baujat_congenital_cortex.png`
- `mycode-11.24/baujat_congenital_subcortex.png`

Forest plots when an etiology has at least 1 row with `Hedges_g_exact`, `CI_lower`, and `CI_upper` after reconciliation:

- `mycode-11.24/forest/forest_acquired.png`
- `mycode-11.24/forest/forest_acquired.svg`
- `mycode-11.24/forest/forest_congenital.png`
- `mycode-11.24/forest/forest_congenital.svg`

## Notes

- The funnel master is based on [`mycode-11.24/funnelt2.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/funnelt2.R).
- Funnel and Baujat use `metafor::rma(..., method = "REML")`, matching the original random-effects model family.
- The funnel and Baujat masters no longer write placeholder files. They either save a real plot or skip the target with an explicit console reason.
- The forest master is R-based for consistency with the rest of the repo and now produces a table-style layout modeled on the original forest reference.
- Forest plots are CI-driven, not variance-driven. They can therefore be available for groups that are still ineligible for funnel/Baujat.
- Run [`validate_workflow.py`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/validate_workflow.py) first if you want a non-R readout of which secondary outputs should exist for the current tables.
