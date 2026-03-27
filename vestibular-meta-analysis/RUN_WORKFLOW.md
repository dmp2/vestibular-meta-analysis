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
3. [`brain_plots_master.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/brain_plots_master.R)

## 3. Funnel, Baujat, And Forest

```powershell
Rscript vestibular-meta-analysis/funnel_plots_master.R
Rscript vestibular-meta-analysis/baujat_plots_master.R
Rscript vestibular-meta-analysis/forest_plots_master.R
```

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
- Funnel and Baujat are variance-limited and will produce placeholders for some groups with the current checked-in data.
- Forest plots use rows that have `Hedges_g_exact`, `CI_lower`, and `CI_upper`, which is the strongest currently available forest-plot input.
