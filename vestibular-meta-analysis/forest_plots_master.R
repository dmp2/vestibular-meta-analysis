#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
  library(dplyr)
  library(stringr)
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
input_file <- file.path(root_dir, "mycode-11.24", "output_with_g.csv")
output_dir <- file.path(root_dir, "mycode-11.24", "forest")

if (!file.exists(input_file)) {
  stop("Missing input file: ", input_file)
}

if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
}

clean_text <- function(x, fallback = "") {
  ifelse(is.na(x) | trimws(as.character(x)) == "" | tolower(as.character(x)) == "nan", fallback, as.character(x))
}

write_placeholder_forest <- function(path_stub, group_name, message_lines) {
  png_file <- paste0(path_stub, ".png")
  svg_file <- paste0(path_stub, ".svg")

  for (target in c(png_file, svg_file)) {
    if (grepl("\\.png$", target)) {
      grDevices::png(target, width = 1100, height = 700, res = 150)
    } else {
      grDevices::svg(target, width = 11, height = 7)
    }
    graphics::plot.new()
    graphics::title(main = paste("Forest Plot (", stringr::str_to_title(group_name), ")", sep = ""))
    y_positions <- seq(0.62, 0.42, length.out = length(message_lines))
    for (i in seq_along(message_lines)) {
      graphics::text(0.5, y_positions[i], labels = message_lines[[i]], cex = 1)
    }
    grDevices::dev.off()
  }
}

make_forest_plot <- function(meta, group_name) {
  plot_df <- meta %>%
    filter(
      Congenital_or_Acquired == group_name,
      !is.na(Hedges_g_exact),
      !is.na(CI_lower),
      !is.na(CI_upper)
    ) %>%
    mutate(
      Year = as.numeric(Year),
      Hedges_g_exact = as.numeric(Hedges_g_exact),
      CI_lower = as.numeric(CI_lower),
      CI_upper = as.numeric(CI_upper)
    ) %>%
    filter(!is.na(Hedges_g_exact), !is.na(CI_lower), !is.na(CI_upper))

  path_stub <- file.path(output_dir, paste0("forest_", group_name))

  if (nrow(plot_df) == 0) {
    write_placeholder_forest(
      path_stub,
      group_name,
      c("No rows with Hedges g and confidence bounds available.")
    )
    message("Saved placeholder forest outputs for ", group_name)
    return(invisible(NULL))
  }

  plot_df <- make_study_labels(plot_df) %>%
    mutate(
      ROI_label = clean_text(ROI_Homogenized, "Unknown ROI"),
      Side_label = clean_text(Side, "NA"),
      label = paste(Study, ROI_label, Side_label, sep = " | ")
    ) %>%
    arrange(Hedges_g_exact, Study) %>%
    mutate(label = factor(label, levels = label))

  p <- ggplot(plot_df, aes(x = Hedges_g_exact, y = label)) +
    geom_segment(
      aes(x = CI_lower, xend = CI_upper, y = label, yend = label),
      color = "grey45",
      linewidth = 0.8
    ) +
    geom_point(size = 2.2, color = "black") +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey60") +
    labs(
      title = paste("Forest Plot (", stringr::str_to_title(group_name), ")", sep = ""),
      x = "Hedges g",
      y = NULL
    ) +
    theme_bw(base_size = 10) +
    theme(
      panel.grid.minor = element_blank(),
      panel.grid.major.y = element_blank(),
      plot.title = element_text(hjust = 0.5),
      axis.text.y = element_text(size = 8)
    )

  png_file <- paste0(path_stub, ".png")
  svg_file <- paste0(path_stub, ".svg")
  ggsave(png_file, p, width = 12, height = max(4, 0.35 * nrow(plot_df)), dpi = 300, bg = "white")
  ggsave(svg_file, p, width = 12, height = max(4, 0.35 * nrow(plot_df)), bg = "white")
  message("Saved ", png_file)
  message("Saved ", svg_file)
}

meta <- load_verified_meta(root_dir)

groups <- c("acquired", "congenital")
for (group_name in groups) {
  make_forest_plot(meta, group_name)
}

message("Finished forest plots.")
