# Vestibular Meta-Analysis

This directory contains an in-progress vestibular neuroimaging meta-analysis assembled from older reference code in [`.ref`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/.ref) and newer local rewrites around CSV-based workflows.

The current best-supported workflow is documented in [WORKFLOW_AUDIT.md](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/WORKFLOW_AUDIT.md). That audit treats [`mycode-11.24`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24) as the most faithful historical execution branch and treats [`output_with_g.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv) as the provisional source-of-truth analysis table.

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

## Strongest Evidence Of A Working Pipeline

The most trustworthy evidence is the saved brain-map branch that uses [`output_with_g.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv):

- [`Brainsurfacemaps.r`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/Brainsurfacemaps.r) -> [`brain_acquired_DK2.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/brain_acquired_DK2.png)
- [`brainonlydk.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/brainonlydk.R) -> [`brainpanel_acquired_DK_cortex_only.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/brainpanel_acquired_DK_cortex_only.png)
- [`braint3.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/braint3.R) -> the five committed acquired brain PNGs, including [`acquired_subcortex_cerebellum_ASEG.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/acquired_subcortex_cerebellum_ASEG.png)

These scripts should be the first target when making the project runnable, because they already have matching committed outputs.

## Working Assumptions

- `output.csv` is the precursor table with sparse effect-size fields.
- `output_with_g.csv` is the main analysis table used by the older plotting scripts.
- `output_final.csv` is not currently trusted as canonical because it appears to lose some populated values after the JSON merge step.
- `jsonwithg.csv` now lives inside [`vestibular-meta-analysis`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis) and should still be treated as an auxiliary merge input rather than a trusted master table.
- The top-level scripts are useful adaptations, but not yet confirmed as the scripts that originally produced the committed figures.

## Recommended Next Steps

1. Run the stable verified pipeline:
   `output.csv` -> `compute_hedges_g.R` -> `brain_plots_master.R`.
2. Treat [`output_with_g.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv) as the generated canonical analysis table for the verified brain outputs.
3. Only after the brain-plot branch runs end-to-end should you repair or retire `merge_json_into_master.R`, the funnel scripts, and the newer top-level adaptation scripts.

## Audit Refresh

Run:

```powershell
python vestibular-meta-analysis/audit_workflow.py
```

This refreshes:

- [`WORKFLOW_AUDIT.md`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/WORKFLOW_AUDIT.md)
- [`audit_summary.json`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/audit_summary.json)

If you later want to turn this into a true git repository, initialize git at the workspace root after reviewing the workflow audit and deciding which outputs should be tracked versus regenerated.
