############################################################
# make_brain_panels.R
#
# Requires:
#   - all_meta_rows.csv  (your master meta file)
#   - brain_plot.R       (from Dr. Manno's project)
#
# Outputs (files):
#   GM_brain_map.png / .pdf
#   GM_funnel.png
#   GM_baujat.png
#   GM_roi_per_area.png
#   WM_brain_map.png
#   WM_funnel.png
#   WM_baujat.png
#   WM_roi_per_area.png
############################################################

library(tidyverse)
library(metafor)

# ---- 0. Load data ----
meta <- readr::read_csv("all_meta_rows.csv")

# Quick sanity check
cat("Rows:", nrow(meta), "\n")
cat("Unique Study_ID:", length(unique(meta$Study_ID)), "\n")

# Coerce key numeric columns
meta <- meta %>%
  mutate(
    Hedges_g_exact    = as.numeric(`Hedges_g_exact`),
    Hedges_g_variance = as.numeric(`Hedges_g_variance`)
  )


# ==========================================================
# Helper 1: subset definitions for panels
# ==========================================================

subset_gm_volume <- function(df) {
  df %>%
    filter(
      Matter == "Gray",
      !is.na(Measure),
      str_detect(Measure, "volume|gmv", ignore_case = TRUE)
    )
}

subset_wm_fa <- function(df) {
  df %>%
    filter(
      Matter == "White",
      !is.na(Measure),
      str_detect(Measure, "FA|fractional anisotropy", ignore_case = TRUE)
    )
}


# ==========================================================
# Helper 2: meta-analysis + funnel + baujat
# ==========================================================

run_meta_and_plots <- function(df_panel, panel_label_prefix) {

  es <- df_panel %>%
    filter(!is.na(Hedges_g_exact), !is.na(Hedges_g_variance))

  if (nrow(es) < 3) {
    message("[", panel_label_prefix, "] Not enough rows with Hedges_g_exact & variance (n = ",
            nrow(es), "); skipping metafor plots.")
    return(invisible(NULL))
  }

  # Random-effects meta-analysis
  res <- rma(
    yi = Hedges_g_exact,
    vi = Hedges_g_variance,
    data = es,
    method = "REML"
  )

  print(paste0("=== ", panel_label_prefix, " ==="))
  print(res)

  # Funnel plot
  png(paste0(panel_label_prefix, "_funnel.png"), width = 1400, height = 1800, res = 300)
  funnel(res, main = paste(panel_label_prefix, "- funnel plot"))
  dev.off()

  # Baujat plot
  png(paste0(panel_label_prefix, "_baujat.png"), width = 1400, height = 1800, res = 300)
  baujat(res, main = paste(panel_label_prefix, "- Baujat plot"))
  dev.off()

  invisible(res)
}


# ==========================================================
# Helper 3: ROI per area (Big_Area barplot)
# ==========================================================

plot_roi_per_area <- function(df_panel, panel_label_prefix) {
  area_counts <- df_panel %>%
    filter(!is.na(Big_Area)) %>%
    count(Big_Area, name = "N_ROI") %>%
    arrange(desc(N_ROI))

  if (nrow(area_counts) == 0) {
    message("[", panel_label_prefix, "] No Big_Area values; skipping ROI-per-area plot.")
    return(invisible(NULL))
  }

  p <- ggplot(area_counts, aes(x = reorder(Big_Area, N_ROI), y = N_ROI)) +
    geom_col(fill = "gray40") +
    coord_flip() +
    labs(
      title = paste(panel_label_prefix, "- ROI per area"),
      x = "Big Area",
      y = "Number of ROIs"
    ) +
    theme_bw(base_size = 12)

  ggsave(paste0(panel_label_prefix, "_roi_per_area.png"),
         plot = p, width = 4, height = 4, dpi = 300)
}


# ==========================================================
# Helper 4: Brain surface map (using brain_plot.R)
# ==========================================================
# IMPORTANT:
#   This assumes brain_plot.R defines a function that can take
#   ROI + Side + value and return a ggplot or save a figure.
#
#   I will call it `plot_brain_surface()` with arguments:
#        df, roi_col, side_col, value_col, title, out_file
#
#   If your function name or arguments are different, just
#   edit the call inside brain_map_panel() accordingly.
# ==========================================================

source("brain_plot.R")   # make sure this is in the same folder

brain_map_panel <- function(df_panel, panel_label_prefix) {
  # Aggregate to one value per ROI x Side
  roi_df <- df_panel %>%
    filter(!is.na(ROI_Homogenized),
           !is.na(Side),
           !is.na(Hedges_g_exact)) %>%
    group_by(ROI_Homogenized, Side) %>%
    summarise(
      Hedges_g = mean(Hedges_g_exact, na.rm = TRUE),
      .groups = "drop"
    )

  if (nrow(roi_df) == 0) {
    message("[", panel_label_prefix, "] No ROI + Side with Hedges_g; skipping brain map.")
    return(invisible(NULL))
  }

  # ---- EDIT THIS CALL TO MATCH YOUR brain_plot.R ----
  # Example: if brain_plot.R defines:
  #   plot_brain_surface(df, roi_col, side_col, value_col, title, out_file)
  # then this call is correct.
  plot_brain_surface(
    df        = roi_df,
    roi_col   = "ROI_Homogenized",
    side_col  = "Side",
    value_col = "Hedges_g",
    title     = panel_label_prefix,
    out_file  = paste0(panel_label_prefix, "_brain_map.png")
  )
}


# ==========================================================
#  Panel A: Gray matter volume
# ==========================================================

gm <- subset_gm_volume(meta)

cat("Panel A (GM volume): n rows =", nrow(gm), "\n")

# brain surface
brain_map_panel(gm, "GM")

# funnel + baujat
run_meta_and_plots(gm, "GM")

# ROI per area
plot_roi_per_area(gm, "GM")


# ==========================================================
#  Panel B: White matter / FA
# ==========================================================

wm <- subset_wm_fa(meta)

cat("Panel B (WM / FA): n rows =", nrow(wm), "\n")

brain_map_panel(wm, "WM")
run_meta_and_plots(wm, "WM")
plot_roi_per_area(wm, "WM")

cat("✅ Finished generating GM/WM panels.\n")
