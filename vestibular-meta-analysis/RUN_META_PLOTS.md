# Secondary Meta-Plot Runbook

These scripts cover the non-brain plots reconstructed from the colleague's adapted code.

## Canonical Input

- [`mycode-11.24/output_with_g.csv`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/output_with_g.csv)

## Commands

From the workspace root:

```powershell
Rscript vestibular-meta-analysis/funnel_plots_master.R
Rscript vestibular-meta-analysis/baujat_plots_master.R
Rscript vestibular-meta-analysis/forest_plots_master.R
```

## Expected Outputs

Funnel plots:

- `mycode-11.24/funnel_acquired_cortex.png`
- `mycode-11.24/funnel_acquired_subcortex.png`
- `mycode-11.24/funnel_congenital_cortex.png`
- `mycode-11.24/funnel_congenital_subcortex.png`

Baujat plots:

- `mycode-11.24/baujat_acquired_cortex.png`
- `mycode-11.24/baujat_acquired_subcortex.png`
- `mycode-11.24/baujat_congenital_cortex.png`
- `mycode-11.24/baujat_congenital_subcortex.png`

Forest plots:

- `mycode-11.24/forest/forest_acquired.png`
- `mycode-11.24/forest/forest_acquired.svg`
- `mycode-11.24/forest/forest_congenital.png`
- `mycode-11.24/forest/forest_congenital.svg`

## Notes

- The funnel master is based on [`mycode-11.24/funnelt2.R`](/c:/Users/dpado/Documents/git/vestibular_meta_analysis/vestibular-meta-analysis/mycode-11.24/funnelt2.R).
- Funnel and Baujat plots currently have very sparse meta-analytic input in `output_with_g.csv`, so the scripts generate placeholder plots when there is insufficient variance data for a real model.
- The forest master is now R-based for consistency with the rest of the repo.
- The forest script uses rows with `Hedges_g_exact`, `CI_lower`, and `CI_upper`, because that is the strongest currently available forest-plot input.
- With the current checked-in data, the most likely outcome is:
  `acquired_subcortex` produces a real funnel/Baujat plot, `acquired_cortex` produces a placeholder, and both congenital outputs produce placeholders.
