# Vestibular Meta-Analysis

This directory contains an in-progress vestibular neuroimaging meta-analysis assembled from older reference code in [`.ref`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/.ref) and newer local rewrites around CSV-based workflows.

The current best-supported workflow is documented in [WORKFLOW_AUDIT.md](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/WORKFLOW_AUDIT.md). That audit treats [`mycode-11.24`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24) as the most faithful historical execution branch.

## Current Status

- Historical working branch: [`mycode-11.24`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24)
- Newer adaptation branch: top-level Python/R scripts in this folder
- Reference-only originals: [`.ref`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/.ref)
- Workflow audit generator: [`audit_workflow.py`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/audit_workflow.py)
- Runnable brain-plot entrypoint: [`brain_plots_master.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/brain_plots_master.R)
- Stable brain-plot pipeline runner: [`run_brain_plot_pipeline.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/run_brain_plot_pipeline.R)
- One-command brain-plot runbook: [`RUN_BRAIN_PLOTS.md`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/RUN_BRAIN_PLOTS.md)
- Funnel master: [`funnel_plots_master.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/funnel_plots_master.R)
- Baujat master: [`baujat_plots_master.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/baujat_plots_master.R)
- Forest master: [`forest_plots_master.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/forest_plots_master.R)
- Secondary meta-plot runbook: [`RUN_META_PLOTS.md`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/RUN_META_PLOTS.md)
- Top-level execution runbook: [`RUN_WORKFLOW.md`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/RUN_WORKFLOW.md)
- Non-R validation script: [`validate_workflow.py`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/validate_workflow.py)
- Generated validator report: `validation_summary.json` after running the validator

## Verified Runnable Branch

The verified runnable branch is now:

1. [`mycode-11.24/output.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output.csv)
2. [`mycode-11.24/compute_hedges_g.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/compute_hedges_g.R)
3. [`mycode-11.24/output_with_g_computed.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g_computed.csv)
4. [`brain_plots_master.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/brain_plots_master.R)
5. [`run_brain_plot_pipeline.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/run_brain_plot_pipeline.R)

This branch has been rerun in RStudio with repo-relative paths and reproduces the saved acquired brain PNGs. The remaining console notices seen on the clean rerun were package build-version warnings, not plot-pipeline failures.

## Strongest Evidence Of A Working Pipeline

The strongest evidence is still the saved brain-map branch in [`mycode-11.24`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24):

- [`Brainsurfacemaps.r`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/Brainsurfacemaps.r) -> [`brain_acquired_DK2.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/brain_acquired_DK2.png)
- [`brainonlydk.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/brainonlydk.R) -> [`brainpanel_acquired_DK_cortex_only.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/brainpanel_acquired_DK_cortex_only.png)
- [`braint3.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/braint3.R) -> the five committed acquired brain PNGs, including [`acquired_subcortex_cerebellum_ASEG.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/acquired_subcortex_cerebellum_ASEG.png)

Those legacy scripts established provenance. The new verified runnable replacement is [`run_brain_plot_pipeline.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/run_brain_plot_pipeline.R), which reproduces the same output family using repo-relative paths.

## Working Assumptions

- `output.csv` is the precursor table with sparse effect-size fields.
- `output_with_g.csv` is the preserved historical analysis table used by the older plotting scripts and audit work.
- `output_with_g_computed.csv` is the recomputed table produced by the verified runnable brain pipeline.
- `output_final.csv` is not currently trusted as canonical because it appears to lose some populated values after the JSON merge step.
- `jsonwithg.csv` now lives inside [`vestibular-meta-analysis`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis) and should still be treated as an auxiliary merge input rather than a trusted master table.
- The top-level scripts are useful adaptations, but not yet confirmed as the scripts that originally produced the committed figures.
- The student's `Congenital_or_Acquired` column is preserved for provenance, but the current secondary plot masters no longer use it as the scientific grouping variable.
- Secondary plot grouping is now derived at runtime:
  funnel and Baujat use `Review_Group`, forest uses `Condition_Normalized`, and cohort-design signal is retained through `Cohort_Contrast`.

## Recommended Next Steps

1. Treat the brain-plot branch as the first stable runnable pipeline:
   `output.csv` -> `compute_hedges_g.R` -> `output_with_g_computed.csv` -> `brain_plots_master.R`.
2. Preserve [`output_with_g.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv) as the historical checked-in table and use [`output_with_g_computed.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g_computed.csv) as the generated table for the verified rerun.
3. Use the hybrid reconciliation in [`meta_plot_helpers.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/meta_plot_helpers.R) for funnel, Baujat, and forest plots so historical variance/CI values are preserved while recomputed effect sizes remain available when needed.
4. Only after the secondary plot masters have been rerun and reviewed should you repair or retire `merge_json_into_master.R` and the newer top-level adaptation scripts.

## Audit Refresh

Run:

```powershell
python vestibular-meta-analysis/audit_workflow.py
python vestibular-meta-analysis/validate_workflow.py
```

This refreshes:

- [`WORKFLOW_AUDIT.md`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/WORKFLOW_AUDIT.md)
- [`audit_summary.json`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/audit_summary.json)
- `validation_summary.json`

Use the audit for historical provenance and artifact-chain inspection. Use the validator for current runnable-state checks, dynamic secondary-plot eligibility, and expected grouped output names.

If you later want to turn this into a true git repository, initialize git at the workspace root after reviewing the workflow audit and deciding which outputs should be tracked versus regenerated.
