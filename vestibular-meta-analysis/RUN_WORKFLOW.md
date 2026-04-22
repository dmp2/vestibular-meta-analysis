# Execution Runbook

This is the top-level execution order for the reconstructed repository workflow.

## 1. Validate Inputs And Eligibility

This step does not require R.

```powershell
python vestibular-meta-analysis/validate_workflow.py
```

It checks:

- required input files
- required master scripts
- expected output paths
- row eligibility for compute, brain, funnel, Baujat, and forest stages

## 2. Compute Effect Sizes And Verified Brain Plots

```powershell
Rscript vestibular-meta-analysis/run_brain_plot_pipeline.R
```

Stable order:

1. [`mycode-11.24/output.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output.csv)
2. [`mycode-11.24/compute_hedges_g.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/compute_hedges_g.R)
3. [`mycode-11.24/output_with_g_computed.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g_computed.csv)
4. [`brain_plots_master.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/brain_plots_master.R)

The stable brain pipeline now preserves the historical [`mycode-11.24/output_with_g.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv) and writes recomputed effect sizes to [`mycode-11.24/output_with_g_computed.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g_computed.csv).

Current verification status:

- Brain plots are the strongest verified runnable branch.
- The pipeline has been rerun successfully in RStudio with repo-relative paths.
- Package build-version notices are expected environment warnings and do not indicate plot-generation failure.

## 3. Funnel, Baujat, And Forest

```powershell
Rscript vestibular-meta-analysis/funnel_plots_master.R
Rscript vestibular-meta-analysis/baujat_plots_master.R
Rscript vestibular-meta-analysis/forest_plots_master.R
```

Secondary-plot input policy:

1. Historical [`mycode-11.24/output_with_g.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv)
2. Recomputed [`mycode-11.24/output_with_g_computed.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g_computed.csv)
3. Hybrid reconciliation in [`meta_plot_helpers.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/meta_plot_helpers.R)

## Required R Packages

- `metafor`
- `readr`
- `dplyr`
- `stringr`
- `tibble`
- `ggplot2`
- `ggseg`
- `patchwork`

## Current Data Reality

- Brain plots have the strongest evidence and are the most trustworthy runnable branch.
- Funnel and Baujat remain variance-limited and now skip ineligible groups instead of writing placeholders.
- Forest plots use rows that have `Hedges_g_exact`, `CI_lower`, and `CI_upper`, so their eligibility is broader than funnel/Baujat eligibility.
- The validator now reports which outputs should exist under the current hybrid secondary-plot rules.
