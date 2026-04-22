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
      ofile <- frames[[i]]$ofile
      if (file.exists(ofile)) {
        return(dirname(normalizePath(ofile)))
      }
      if (file.exists(file.path(getwd(), basename(ofile)))) {
        return(normalizePath(getwd()))
      }
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
INPUT_FILE <- if (exists("BRAIN_META_INPUT", inherits = TRUE)) get("BRAIN_META_INPUT", inherits = TRUE) else file.path(LEGACY_DIR, "output_with_g.csv")
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

dk_atlas <- ggseg::dk()
dk_regions <- unique(as.data.frame(dk_atlas)$region)
dk_hemis <- unique(as.data.frame(dk_atlas)$hemi)

aseg_atlas <- ggseg::aseg()
aseg_labels <- unique(aseg_atlas$data$sf$label)

dk_map_verified <- tribble(
  ~pattern,                                      ~region,
  "anterior cingulate cortex",                   "rostral anterior cingulate",
  "cingulate gyrus",                             "posterior cingulate",
  "cuneus",                                      "cuneus",
  "fusiform gyrus",                              "fusiform",
  "fusiform",                                    "fusiform",
  "insula",                                      "insula",
  "intracalcarine cortex",                       "pericalcarine",
  "intracalcarine",                              "pericalcarine",
  "lingual gyrus",                               "lingual",
  "lateral occipital cortex",                    "lateral occipital",
  "lateral occipital",                           "lateral occipital",
  "middle frontal gyrus",                        "rostral middle frontal",
  "middle temporal gyrus \\(mt/v5\\)",           "middle temporal",
  "middle temporal visual area \\(mt/v5\\)",     "middle temporal",
  "middle temporal gyrus",                       "middle temporal",
  "^mt/v5$",                                     "middle temporal",
  "postcentral gyrus",                           "postcentral",
  "precentral gyrus",                            "precentral",
  "precuneus / superior parietal white matter",  "superior parietal",
  "precuneus",                                   "precuneus",
  "superior frontal gyrus",                      "superior frontal",
  "superior orbitofrontal cortex",               "lateral orbitofrontal",
  "superior orbitofrontal",                      "lateral orbitofrontal",
  "orbital gyrus",                               "lateral orbitofrontal",
  "superior temporal gyrus",                     "superior temporal",
  "primary somatosensory cortex",                "postcentral",
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

normalize_side <- function(side_value) {
  side_clean <- str_squish(tolower(if_else(is.na(side_value), "", side_value)))

  if (side_clean %in% c("l", "left")) {
    return("left")
  }
  if (side_clean %in% c("r", "right")) {
    return("right")
  }
  if (side_clean %in% c("", "na", "n/a", "bilateral", "both", "midline")) {
    return("both")
  }
  "both"
}

build_dk_rows <- function(region, side_value) {
  if (is.na(region) || region == "") {
    return(tibble(region = character(0), hemi = character(0)))
  }

  side_key <- normalize_side(side_value)
  hemi_values <- switch(
    side_key,
    left = "left",
    right = "right",
    both = c("left", "right")
  )

  tibble(region = region, hemi = hemi_values)
}

build_aseg_labels <- function(sub_label, side_value) {
  if (is.na(sub_label) || sub_label == "") {
    return(character(0))
  }

  if (sub_label == "brain-stem") {
    return("Brain-Stem")
  }

  label_core <- dplyr::case_when(
    sub_label == "hippocamp" ~ "Hippocampus",
    sub_label == "amygdala" ~ "Amygdala",
    sub_label == "caudate" ~ "Caudate",
    sub_label == "putamen" ~ "Putamen",
    sub_label == "pallidum" ~ "Pallidum",
    sub_label == "accumbens-area" ~ "Accumbens-area",
    sub_label == "thalamus" ~ "Thalamus",
    sub_label == "cerebellum-cortex" ~ "Cerebellum-Cortex",
    TRUE ~ NA_character_
  )

  if (is.na(label_core)) {
    return(character(0))
  }

  side_key <- normalize_side(side_value)
  if (side_key == "left") {
    return(paste0("Left-", label_core))
  }
  if (side_key == "right") {
    return(paste0("Right-", label_core))
  }

  c(paste0("Left-", label_core), paste0("Right-", label_core))
}

expand_plot_labels <- function(df, label_builder) {
  expanded_rows <- lapply(seq_len(nrow(df)), function(i) {
    labels <- label_builder(df[i, , drop = FALSE])
    if (length(labels) == 0) {
      return(NULL)
    }

    row <- df[rep(i, length(labels)), , drop = FALSE]
    row$label <- labels
    row
  })

  bind_rows(expanded_rows)
}

expand_plot_rows <- function(df, row_builder) {
  expanded_rows <- lapply(seq_len(nrow(df)), function(i) {
    built <- row_builder(df[i, , drop = FALSE])
    if (nrow(built) == 0) {
      return(NULL)
    }

    row <- df[rep(i, nrow(built)), , drop = FALSE]
    bind_cols(row, built)
  })

  bind_rows(expanded_rows)
}

filter_known_labels <- function(df, atlas_labels, context) {
  unmatched <- setdiff(unique(df$label), atlas_labels)
  if (length(unmatched) > 0) {
    message(
      context,
      " dropped atlas labels with no current ggseg match: ",
      paste(sort(unmatched), collapse = ", ")
    )
  }

  df %>%
    filter(label %in% atlas_labels)
}

filter_known_dk_regions <- function(df, context) {
  unmatched_regions <- setdiff(unique(df$region), dk_regions)
  unmatched_hemis <- setdiff(unique(df$hemi), dk_hemis)

  if (length(unmatched_regions) > 0) {
    message(
      context,
      " dropped DK regions with no current ggseg match: ",
      paste(sort(unmatched_regions), collapse = ", ")
    )
  }
  if (length(unmatched_hemis) > 0) {
    message(
      context,
      " dropped DK hemis with no current ggseg match: ",
      paste(sort(unmatched_hemis), collapse = ", ")
    )
  }

  df %>%
    filter(region %in% dk_regions, hemi %in% dk_hemis)
}

make_dk_plot <- function(data, limits, hemi, view, title,
                         border_colour = "grey30", border_size = 0.3,
                         low = "#4575B4", mid = "white", high = "#D73027",
                         na_value = "grey90", use_void = FALSE) {
  plot_data <- data %>%
    filter(hemi == !!hemi)

  atlas_plot_data <- as.data.frame(dk_atlas) %>%
    filter(
      !is.na(region),
      hemi == !!hemi,
      view == !!view
    ) %>%
    left_join(plot_data, by = c("region", "hemi"))

  p <- ggplot(atlas_plot_data) +
    geom_sf(
      aes(fill = value),
      colour = border_colour,
      linewidth = border_size
    ) +
    scale_fill_gradient2(
      name = "Hedges g",
      low = low,
      mid = mid,
      high = high,
      limits = limits,
      midpoint = 0,
      na.value = na_value
    ) +
    ggtitle(title) +
    coord_sf(datum = NA)

  if (use_void) {
    p <- p + theme_void()
  }

  p
}

make_aseg_plot <- function(data, limits, title) {
  ggplot(data) +
    geom_brain(
      atlas = aseg_atlas,
      aes(fill = value),
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
    ggtitle(title)
}

save_simple_mean_panel <- function(df_panel) {
  meta_roi <- df_panel %>%
    group_by(ROI_Homogenized, ROI_clean, Side) %>%
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

  meta_region <- expand_plot_rows(
    meta_roi,
    function(row) build_dk_rows(row$dk_region[[1]], row$Side[[1]])
  ) %>%
    filter_known_dk_regions("Simple-mean cortex") %>%
    group_by(region, hemi) %>%
    summarise(
      value = mean(g, na.rm = TRUE),
      .groups = "drop"
    )

  if (nrow(meta_region) == 0) {
    stop("No acquired cortical ROIs mapped to current ggseg DK labels for the simple-mean panel.")
  }

  max_abs <- max(abs(meta_region$value), na.rm = TRUE)
  if (!is.finite(max_abs) || max_abs == 0) {
    max_abs <- 1
  }
  limits <- c(-max_abs, max_abs)

  p_ll <- make_dk_plot(meta_region, limits, "left", "lateral", "acquired left Lateral",
                       border_colour = "black", border_size = 0.3,
                       low = "#08306b", high = "#a50026", na_value = "grey85", use_void = TRUE)
  p_lm <- make_dk_plot(meta_region, limits, "left", "medial", "acquired left Medial",
                       border_colour = "black", border_size = 0.3,
                       low = "#08306b", high = "#a50026", na_value = "grey85", use_void = TRUE)
  p_rl <- make_dk_plot(meta_region, limits, "right", "lateral", "acquired right Lateral",
                       border_colour = "black", border_size = 0.3,
                       low = "#08306b", high = "#a50026", na_value = "grey85", use_void = TRUE)
  p_rm <- make_dk_plot(meta_region, limits, "right", "medial", "acquired right Medial",
                       border_colour = "black", border_size = 0.3,
                       low = "#08306b", high = "#a50026", na_value = "grey85", use_void = TRUE)

  panel <- (p_ll | p_lm) / (p_rl | p_rm)

  out_file <- file.path(OUTPUT_DIR, "brain_acquired_DK2.png")
  ggsave(out_file, panel, width = 10, height = 8, dpi = 300, bg = "white")
  message("Saved ", out_file)
}

build_weighted_cortex <- function(df_panel) {
  cortex_rows <- df_panel %>%
    rowwise() %>%
    mutate(dk_region = match_from_map(ROI_clean, dk_map_verified, "region")) %>%
    ungroup() %>%
    filter(!is.na(dk_region))

  cortex_values <- expand_plot_rows(
    cortex_rows,
    function(row) build_dk_rows(row$dk_region[[1]], row$Side[[1]])
  ) %>%
    filter_known_dk_regions("Weighted cortex") %>%
    group_by(region, hemi) %>%
    summarise(
      value = weighted_value(Hedges_g_exact, Hedges_g_variance),
      .groups = "drop"
    )

  if (nrow(cortex_values) == 0) {
    stop("No acquired cortical ROIs mapped for weighted DK outputs.")
  }

  cortex_values
}

save_weighted_cortex_outputs <- function(df_panel) {
  cortex_values <- build_weighted_cortex(df_panel)

  max_abs <- max(abs(cortex_values$value), na.rm = TRUE)
  if (!is.finite(max_abs) || max_abs == 0) {
    max_abs <- 1
  }
  limits <- c(-max_abs, max_abs)

  theme_bits <- theme(
    plot.title = element_text(size = 11, hjust = 0.5, margin = margin(b = 4)),
    legend.position = "right",
    plot.margin = margin(5, 5, 5, 5)
  )

  p_ll <- make_dk_plot(cortex_values, limits, "left", "lateral", "acquired - left lateral") + theme_bits
  p_lm <- make_dk_plot(cortex_values, limits, "left", "medial", "acquired - left medial") + theme_bits
  p_rl <- make_dk_plot(cortex_values, limits, "right", "lateral", "acquired - right lateral") + theme_bits
  p_rm <- make_dk_plot(cortex_values, limits, "right", "medial", "acquired - right medial") + theme_bits

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
  sub_rows <- df_panel %>%
    rowwise() %>%
    mutate(sub_label = match_from_map(ROI_clean, sub_map_verified, "label")) %>%
    ungroup() %>%
    filter(!is.na(sub_label))

  sub_values <- expand_plot_labels(
    sub_rows,
    function(row) build_aseg_labels(row$sub_label[[1]], row$Side[[1]])
  ) %>%
    filter_known_labels(aseg_labels, "Weighted subcortex") %>%
    group_by(label) %>%
    summarise(
      value = weighted_value(Hedges_g_exact, Hedges_g_variance),
      .groups = "drop"
    )

  if (nrow(sub_values) == 0) {
    stop("No acquired subcortical or cerebellar ROIs mapped for ASEG output.")
  }

  max_abs <- max(abs(sub_values$value), na.rm = TRUE)
  if (!is.finite(max_abs) || max_abs == 0) {
    max_abs <- 1
  }

  p_sub <- make_aseg_plot(sub_values, c(-max_abs, max_abs), "acquired - subcortex + cerebellum") +
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
