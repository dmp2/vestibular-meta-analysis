#!/usr/bin/env Rscript

############################################################
# brain_plots_master.R
#
# Repo-relative master script for the verified acquired brain
# plots. It standardizes on:
#   vestibular-meta-analysis/mycode-11.24/output_with_g.csv
#
# Outputs written to:
#   vestibular-meta-analysis/mycode-11.24/
#
# Verified outputs reproduced:
#   brain_acquired_DK2.png
#   brainpanel_acquired_DK_cortex_only.png
#   acquired_left_lateral_DK.png
#   acquired_left_medial_DK.png
#   acquired_right_lateral_DK.png
#   acquired_right_medial_DK.png
#   acquired_subcortex_cerebellum_ASEG.png
############################################################

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(stringr)
  library(ggplot2)
  library(ggseg)
  library(patchwork)
  library(tibble)
})

get_script_dir <- function() {
  frames <- sys.frames()
  for (i in rev(seq_along(frames))) {
    if (!is.null(frames[[i]]$ofile)) {
      return(dirname(normalizePath(frames[[i]]$ofile)))
    }
  }
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg) > 0) {
    return(dirname(normalizePath(sub("^--file=", "", file_arg[1]))))
  }
  normalizePath(getwd())
}

ROOT_DIR <- get_script_dir()
LEGACY_DIR <- file.path(ROOT_DIR, "mycode-11.24")
INPUT_FILE <- file.path(LEGACY_DIR, "output_with_g.csv")
OUTPUT_DIR <- LEGACY_DIR

if (!file.exists(INPUT_FILE)) {
  stop("Missing input file: ", INPUT_FILE)
}

if (!dir.exists(OUTPUT_DIR)) {
  dir.create(OUTPUT_DIR, recursive = TRUE, showWarnings = FALSE)
}

theme_set(
  theme_void(base_size = 10) +
    theme(
      plot.title.position = "plot",
      plot.title = element_text(hjust = 0.5, size = 11),
      strip.text = element_blank(),
      strip.background = element_blank()
    )
)

message("Reading input: ", INPUT_FILE)
meta <- read_csv(INPUT_FILE, show_col_types = FALSE)

stopifnot(
  "Congenital_or_Acquired" %in% names(meta),
  "ROI_Homogenized" %in% names(meta),
  "Hedges_g_exact" %in% names(meta)
)

meta_acq <- meta %>%
  filter(
    !is.na(ROI_Homogenized),
    !is.na(Hedges_g_exact),
    tolower(Congenital_or_Acquired) == "acquired"
  ) %>%
  mutate(
    ROI_clean = if_else(
      is.na(ROI_Homogenized),
      "",
      str_squish(tolower(ROI_Homogenized))
    )
  )

if (nrow(meta_acq) == 0) {
  stop("No acquired rows with non-missing ROI_Homogenized and Hedges_g_exact.")
}

message("Acquired rows with Hedges g: ", nrow(meta_acq))

dk_map_verified <- tribble(
  ~pattern,                                      ~region,
  "anterior cingulate cortex",                   "rostralanteriorcingulate",
  "cingulate gyrus",                             "posteriorcingulate",
  "cuneus",                                      "cuneus",
  "fusiform gyrus",                              "fusiform",
  "fusiform",                                    "fusiform",
  "insula",                                      "insula",
  "intracalcarine cortex",                       "pericalcarine",
  "intracalcarine",                              "pericalcarine",
  "lingual gyrus",                               "lingual",
  "lateral occipital cortex",                    "lateraloccipital",
  "lateral occipital",                           "lateraloccipital",
  "middle frontal gyrus",                        "rostralmiddlefrontal",
  "middle temporal gyrus (mt/v5)",               "middletemporal",
  "middle temporal gyrus",                       "middletemporal",
  "postcentral gyrus",                           "postcentral",
  "precentral gyrus",                            "precentral",
  "precuneus / superior parietal white matter",  "superiorparietal",
  "precuneus",                                   "precuneus",
  "superior frontal gyrus",                      "superiorfrontal",
  "superior orbitofrontal cortex",               "lateralorbitofrontal",
  "superior orbitofrontal",                      "lateralorbitofrontal",
  "superior temporal gyrus",                     "superiortemporal",
  "supramarginal gyrus",                         "supramarginal"
)

sub_map_verified <- tribble(
  ~pattern,          ~label,
  "hippocampus",     "hippocamp",
  "parahippocampus", "hippocamp",
  "parahippocamp",   "hippocamp",
  "amygdala",        "amygdala",
  "caudate",         "caudate",
  "putamen",         "putamen",
  "pallidum",        "pallidum",
  "pallid",          "pallidum",
  "accumbens",       "accumbens-area",
  "accumb",          "accumbens-area",
  "thalamus",        "thalamus",
  "thalam",          "thalamus",
  "brainstem",       "brain-stem",
  "pons",            "brain-stem",
  "cerebell",        "cerebellum-cortex",
  "vermis",          "cerebellum-cortex",
  "vermi",           "cerebellum-cortex"
)

match_from_map <- function(value, map_df, label_col) {
  hits <- map_df[[label_col]][
    vapply(map_df$pattern, function(pattern) str_detect(value, pattern), logical(1))
  ]
  if (length(hits) == 0) {
    return(NA_character_)
  }
  hits[1]
}

weighted_value <- function(effect, variance) {
  weight <- ifelse(!is.na(variance) & variance > 0, 1 / variance, 1)
  sum(effect * weight, na.rm = TRUE) / sum(weight, na.rm = TRUE)
}

save_simple_mean_panel <- function(df_panel) {
  meta_roi <- df_panel %>%
    group_by(ROI_Homogenized, ROI_clean) %>%
    summarise(
      g = mean(Hedges_g_exact, na.rm = TRUE),
      k = sum(!is.na(Hedges_g_exact)),
      .groups = "drop"
    ) %>%
    filter(!is.na(g), k > 0) %>%
    rowwise() %>%
    mutate(dk_region = match_from_map(ROI_clean, dk_map_verified, "region")) %>%
    ungroup() %>%
    filter(!is.na(dk_region))

  if (nrow(meta_roi) == 0) {
    stop("No acquired cortical ROIs mapped for the simple-mean DK panel.")
  }

  meta_region <- meta_roi %>%
    group_by(dk_region) %>%
    summarise(
      value = mean(g, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    rename(region = dk_region)

  max_abs <- max(abs(meta_region$value), na.rm = TRUE)
  if (!is.finite(max_abs) || max_abs == 0) {
    max_abs <- 1
  }

  dk_atlas <- ggseg::dk
  dk_atlas$data <- dk_atlas$data %>%
    left_join(meta_region, by = "region")

  make_view <- function(hemi, view, subtitle) {
    ggseg(
      atlas = dk_atlas,
      hemi = hemi,
      view = view,
      mapping = aes(fill = value),
      color = "black",
      size = 0.3
    ) +
      scale_fill_gradient2(
        low = "#08306b",
        mid = "white",
        high = "#a50026",
        midpoint = 0,
        limits = c(-max_abs, max_abs),
        na.value = "grey85",
        name = "Hedges g"
      ) +
      ggtitle(paste("acquired", subtitle)) +
      theme_void() +
      theme(
        plot.title = element_text(hjust = 0.5, size = 11),
        legend.position = "right"
      )
  }

  panel <- (
    make_view("left", "lateral", "left Lateral") |
      make_view("left", "medial", "left Medial")
  ) / (
    make_view("right", "lateral", "right Lateral") |
      make_view("right", "medial", "right Medial")
  )

  out_file <- file.path(OUTPUT_DIR, "brain_acquired_DK2.png")
  ggsave(out_file, panel, width = 10, height = 8, dpi = 300)
  message("Saved ", out_file)
}

build_weighted_cortex <- function(df_panel) {
  cortex_values <- df_panel %>%
    rowwise() %>%
    mutate(dk_region = match_from_map(ROI_clean, dk_map_verified, "region")) %>%
    ungroup() %>%
    filter(!is.na(dk_region)) %>%
    group_by(dk_region) %>%
    summarise(
      value = weighted_value(Hedges_g_exact, Hedges_g_variance),
      .groups = "drop"
    ) %>%
    rename(region = dk_region)

  if (nrow(cortex_values) == 0) {
    stop("No acquired cortical ROIs mapped for weighted DK outputs.")
  }

  cortex_values
}

make_weighted_dk_plot <- function(atlas, limits, hemi, view, subtitle) {
  ggseg(
    atlas = atlas,
    hemi = hemi,
    view = view,
    mapping = aes(fill = value),
    colour = "grey30",
    size = 0.3
  ) +
    scale_fill_gradient2(
      name = "Hedges g",
      low = "#4575B4",
      mid = "white",
      high = "#D73027",
      limits = limits,
      midpoint = 0,
      na.value = "grey90"
    ) +
    ggtitle(subtitle) +
    theme(
      plot.title = element_text(size = 11, hjust = 0.5, margin = margin(b = 4)),
      legend.position = "right",
      plot.margin = margin(5, 5, 5, 5)
    )
}

save_weighted_cortex_outputs <- function(df_panel) {
  cortex_values <- build_weighted_cortex(df_panel)
  dk_atlas <- ggseg::dk
  dk_atlas$data <- dk_atlas$data %>%
    left_join(cortex_values, by = "region")

  max_abs <- max(abs(cortex_values$value), na.rm = TRUE)
  if (!is.finite(max_abs) || max_abs == 0) {
    max_abs <- 1
  }
  limits <- c(-max_abs, max_abs)

  p_ll <- make_weighted_dk_plot(dk_atlas, limits, "left", "lateral", "acquired - left lateral")
  p_lm <- make_weighted_dk_plot(dk_atlas, limits, "left", "medial", "acquired - left medial")
  p_rl <- make_weighted_dk_plot(dk_atlas, limits, "right", "lateral", "acquired - right lateral")
  p_rm <- make_weighted_dk_plot(dk_atlas, limits, "right", "medial", "acquired - right medial")

  ggsave(file.path(OUTPUT_DIR, "acquired_left_lateral_DK.png"), p_ll, width = 4, height = 3, dpi = 300, bg = "white")
  ggsave(file.path(OUTPUT_DIR, "acquired_left_medial_DK.png"), p_lm, width = 4, height = 3, dpi = 300, bg = "white")
  ggsave(file.path(OUTPUT_DIR, "acquired_right_lateral_DK.png"), p_rl, width = 4, height = 3, dpi = 300, bg = "white")
  ggsave(file.path(OUTPUT_DIR, "acquired_right_medial_DK.png"), p_rm, width = 4, height = 3, dpi = 300, bg = "white")

  panel_cortex <- (p_ll | p_lm) / (p_rl | p_rm)
  ggsave(
    file.path(OUTPUT_DIR, "brainpanel_acquired_DK_cortex_only.png"),
    panel_cortex,
    width = 9,
    height = 7,
    dpi = 300,
    bg = "white"
  )

  message("Saved weighted cortical outputs in ", OUTPUT_DIR)
}

save_weighted_subcortex_output <- function(df_panel) {
  sub_values <- df_panel %>%
    rowwise() %>%
    mutate(sub_label = match_from_map(ROI_clean, sub_map_verified, "label")) %>%
    ungroup() %>%
    filter(!is.na(sub_label)) %>%
    group_by(sub_label) %>%
    summarise(
      value = weighted_value(Hedges_g_exact, Hedges_g_variance),
      .groups = "drop"
    )

  if (nrow(sub_values) == 0) {
    stop("No acquired subcortical or cerebellar ROIs mapped for ASEG output.")
  }

  aseg_atlas <- ggseg::aseg
  aseg_atlas$data <- aseg_atlas$data %>%
    mutate(region_clean = tolower(region)) %>%
    left_join(
      sub_values %>% mutate(region_clean = sub_label),
      by = "region_clean"
    )

  max_abs <- max(abs(aseg_atlas$data$value), na.rm = TRUE)
  if (!is.finite(max_abs) || max_abs == 0) {
    max_abs <- 1
  }

  p_sub <- ggseg(
    atlas = aseg_atlas,
    mapping = aes(fill = value),
    colour = "grey30",
    size = 0.3
  ) +
    scale_fill_gradient2(
      name = "Hedges g",
      low = "#4575B4",
      mid = "white",
      high = "#D73027",
      limits = c(-max_abs, max_abs),
      midpoint = 0,
      na.value = "grey90"
    ) +
    ggtitle("acquired - subcortex + cerebellum") +
    theme(
      plot.title = element_text(size = 11, hjust = 0.5, margin = margin(b = 4)),
      legend.position = "right",
      plot.margin = margin(5, 5, 5, 5)
    )

  out_file <- file.path(OUTPUT_DIR, "acquired_subcortex_cerebellum_ASEG.png")
  ggsave(out_file, p_sub, width = 4.5, height = 3.2, dpi = 300, bg = "white")
  message("Saved ", out_file)
}

save_simple_mean_panel(meta_acq)
save_weighted_cortex_outputs(meta_acq)
save_weighted_subcortex_output(meta_acq)

message("Finished generating verified acquired brain plots.")
