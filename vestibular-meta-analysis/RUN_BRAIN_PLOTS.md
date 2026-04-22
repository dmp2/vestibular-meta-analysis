# Brain Plot Runbook

This runbook is for the stable verified acquired brain-plot pipeline.

## Stable Order

1. [`mycode-11.24/output.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output.csv)
2. [`mycode-11.24/compute_hedges_g.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/compute_hedges_g.R)
3. [`mycode-11.24/output_with_g_computed.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g_computed.csv)
4. [`brain_plots_master.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/brain_plots_master.R)

## Tables

- Preserved historical table: [`mycode-11.24/output_with_g.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv)
- Generated rerun table used by the stable brain pipeline: [`mycode-11.24/output_with_g_computed.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g_computed.csv)

## One Command

From the workspace root, run:

```powershell
Rscript vestibular-meta-analysis/run_brain_plot_pipeline.R
```

## Outputs

The script writes these verified PNGs into [`mycode-11.24`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24):

- [`brain_acquired_DK2.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/brain_acquired_DK2.png)
- [`brainpanel_acquired_DK_cortex_only.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/brainpanel_acquired_DK_cortex_only.png)
- [`acquired_left_lateral_DK.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/acquired_left_lateral_DK.png)
- [`acquired_left_medial_DK.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/acquired_left_medial_DK.png)
- [`acquired_right_lateral_DK.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/acquired_right_lateral_DK.png)
- [`acquired_right_medial_DK.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/acquired_right_medial_DK.png)
- [`acquired_subcortex_cerebellum_ASEG.png`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/acquired_subcortex_cerebellum_ASEG.png)

## Verification Status

- The pipeline has been rerun successfully in RStudio from the repo root with repo-relative paths.
- The cortical branch now uses a manual atlas join for stable rendering.
- The only warning on the clean rerun was package build-version notices such as `package 'dplyr' was built under R version 4.5.3`.
- The single ASEG console line `Merging atlas and data by label.` is expected for the remaining subcortical plotting path and did not block output generation.

## Required R Packages

- `dplyr`
- `readr`
- `stringr`
- `ggplot2`
- `ggseg`
- `patchwork`
- `tibble`

## Notes

- The pipeline is repo-relative and does not depend on the original desktop paths in the older scripts.
- [`compute_hedges_g.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/compute_hedges_g.R) now runs against repo-local `output.csv` and writes repo-local `output_with_g_computed.csv`.
- [`brain_plots_master.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/brain_plots_master.R) is overridable and the stable pipeline points it at `output_with_g_computed.csv`.
- The historical [`output_with_g.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv) is preserved instead of being overwritten.
- The legacy plotting scripts remain useful as provenance, but the pipeline runner and master script are the new runnable entrypoints.
