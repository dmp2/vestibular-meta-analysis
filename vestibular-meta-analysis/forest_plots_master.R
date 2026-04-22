#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(stringr)
  library(patchwork)
})

bootstrap_script_dir <- function() {
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

source(file.path(bootstrap_script_dir(), "meta_plot_helpers.R"))

root_dir <- get_script_dir()
output_dir <- file.path(meta_output_dir(root_dir), "forest")

if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
}

display_text <- function(x, fallback = "") {
  ifelse(has_value(x), trimws(as.character(x)), fallback)
}

display_side <- function(x) {
  out <- stringr::str_to_title(display_text(x, "NA"))
  out[out %in% c("Bilateral", "Both")] <- "Bilat."
  out
}

order_side_rows <- function(dat) {
  separator_row <- function(template) {
    blank <- template[1, , drop = FALSE]
    for (column in names(blank)) {
      if (is.numeric(blank[[column]])) {
        blank[[column]] <- NA_real_
      } else {
        blank[[column]] <- ""
      }
    }
    blank
  }

  right_rows <- dat %>%
    filter(stringr::str_to_lower(display_text(Side)) == "right") %>%
    arrange(desc(Hedges_g_exact), Study)

  left_rows <- dat %>%
    filter(stringr::str_to_lower(display_text(Side)) == "left") %>%
    arrange(desc(Hedges_g_exact), Study)

  other_rows <- dat %>%
    filter(!stringr::str_to_lower(display_text(Side)) %in% c("left", "right")) %>%
    arrange(desc(Hedges_g_exact), Study)

  blocks <- list()
  if (nrow(right_rows) > 0) {
    blocks <- c(blocks, list(right_rows))
  }
  if (nrow(left_rows) > 0) {
    if (length(blocks) > 0) {
      blocks <- c(blocks, list(separator_row(dat)))
    }
    blocks <- c(blocks, list(left_rows))
  }
  if (nrow(other_rows) > 0) {
    if (length(blocks) > 0) {
      blocks <- c(blocks, list(separator_row(dat)))
    }
    blocks <- c(blocks, list(other_rows))
  }

  combined <- dplyr::bind_rows(blocks)
  if (nrow(combined) == 0) {
    return(combined)
  }

  combined %>%
    mutate(is_separator = !has_value(Study)) %>%
    mutate(row_id = rev(seq_len(n())))
}

prepare_forest_rows <- function(meta, etio) {
  dat <- meta %>%
    filter(
      Congenital_or_Acquired == etio,
      has_value(Hedges_g_exact),
      has_value(CI_lower),
      has_value(CI_upper)
    ) %>%
    mutate(
      Hedges_g_exact = as.numeric(Hedges_g_exact),
      CI_lower = as.numeric(CI_lower),
      CI_upper = as.numeric(CI_upper)
    ) %>%
    filter(!is.na(Hedges_g_exact), !is.na(CI_lower), !is.na(CI_upper)) %>%
    make_study_labels() %>%
    mutate(
      ROI_label = display_text(ROI_Homogenized, "Unknown ROI"),
      Big_Area_label = display_text(Big_Area, "NA"),
      Side_label = display_side(Side),
      N_label = format_n_label(Sample_Size_Patients, Sample_Size_Controls),
      Estimate_label = sprintf("%.2f [%.2f, %.2f]", Hedges_g_exact, CI_lower, CI_upper)
    )

  ordered <- order_side_rows(dat)
  if (nrow(ordered) == 0) {
    return(ordered)
  }

  ordered
}

base_text_theme <- function(n_rows) {
  list(
    theme_void(base_size = 10),
    theme(
      plot.title = element_text(face = "bold", hjust = 0, size = 10),
      plot.margin = margin(t = 6, r = 2, b = 6, l = 2)
    )
  )
}

make_text_column <- function(dat, column, title, hjust = 0) {
  ggplot(dat, aes(x = 0, y = row_id)) +
    geom_text(
      data = dat %>% filter(!is_separator),
      aes(label = .data[[column]]),
      hjust = hjust,
      size = 3
    ) +
    scale_x_continuous(limits = c(0, 1), expand = c(0, 0)) +
    scale_y_continuous(limits = c(0.5, nrow(dat) + 0.5), expand = c(0, 0)) +
    labs(title = title) +
    base_text_theme(nrow(dat))
}

make_forest_panel <- function(dat, title) {
  plot_dat <- dat %>% filter(!is_separator)
  x_min <- min(c(plot_dat$CI_lower, plot_dat$Hedges_g_exact, 0), na.rm = TRUE)
  x_max <- max(c(plot_dat$CI_upper, plot_dat$Hedges_g_exact, 0), na.rm = TRUE)
  padding <- max(0.15, (x_max - x_min) * 0.08)

  ggplot(plot_dat, aes(y = row_id)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey55", linewidth = 0.5) +
    geom_segment(
      aes(x = CI_lower, xend = CI_upper, yend = row_id),
      linewidth = 0.6,
      color = "grey35"
    ) +
    geom_point(aes(x = Hedges_g_exact), size = 1.8, shape = 21, fill = "black", color = "black") +
    scale_x_continuous(
      limits = c(x_min - padding, x_max + padding),
      expand = c(0, 0)
    ) +
    scale_y_continuous(limits = c(0.5, nrow(dat) + 0.5), expand = c(0, 0)) +
    labs(title = title, x = "Hedges g", y = NULL) +
    theme_bw(base_size = 10) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0, size = 10),
      panel.grid.major.y = element_blank(),
      panel.grid.minor = element_blank(),
      axis.text.y = element_blank(),
      axis.ticks.y = element_blank(),
      plot.margin = margin(t = 6, r = 6, b = 6, l = 6)
    )
}

make_forest_plot <- function(meta, etio) {
  dat <- prepare_forest_rows(meta, etio)
  if (nrow(dat) == 0) {
    message("Skipping forest plot for ", etio, ": no effect rows with confidence intervals in the reconciled table")
    return(invisible(NULL))
  }

  study_col <- make_text_column(dat, "Study", "Study")
  roi_col <- make_text_column(dat, "ROI_label", "ROI")
  area_col <- make_text_column(dat, "Big_Area_label", "Big Area")
  side_col <- make_text_column(dat, "Side_label", "Side")
  n_col <- make_text_column(dat, "N_label", "N (P/C)")
  forest_col <- make_forest_panel(dat, "Estimate")
  est_col <- make_text_column(dat, "Estimate_label", "Est. (95% CI)")

  composed <- study_col + roi_col + area_col + side_col + n_col + forest_col + est_col +
    patchwork::plot_layout(widths = c(1.5, 1.6, 1.0, 0.8, 0.9, 1.8, 1.6)) +
    patchwork::plot_annotation(
      title = paste("Forest Plot (", stringr::str_to_title(etio), ")", sep = ""),
      subtitle = "Hybrid secondary-plot table; rows require Hedges g with confidence intervals",
      theme = theme(
        plot.title = element_text(face = "bold", hjust = 0.5, size = 14),
        plot.subtitle = element_text(hjust = 0.5, size = 10)
      )
    )

  file_stub <- file.path(output_dir, paste0("forest_", etio))
  width_in <- 15
  height_in <- max(4.5, 0.28 * nrow(dat) + 1.8)

  ggsave(
    paste0(file_stub, ".png"),
    composed,
    width = width_in,
    height = height_in,
    dpi = 300,
    bg = "white",
    limitsize = FALSE
  )
  ggsave(
    paste0(file_stub, ".svg"),
    composed,
    width = width_in,
    height = height_in,
    bg = "white",
    limitsize = FALSE
  )

  message("Saved ", paste0(file_stub, ".png"))
  message("Saved ", paste0(file_stub, ".svg"))
}

meta <- load_secondary_plot_meta(root_dir, input_policy = "hybrid")

eligibility <- forest_group_eligibility(meta)
message("Forest-plot eligibility summary:")
print(eligibility)

for (etio in c("acquired", "congenital")) {
  make_forest_plot(meta, etio)
}

message("Finished forest plots.")
