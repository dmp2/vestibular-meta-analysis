#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(metafor)
  library(readr)
  library(dplyr)
  library(stringr)
  library(tibble)
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
output_dir <- meta_output_dir(root_dir)
meta <- load_verified_meta(root_dir)

plot_specs <- tibble::tribble(
  ~etio,       ~region_type, ~filename,
  "acquired",  "cortex",     "baujat_acquired_cortex.png",
  "acquired",  "subcortex",  "baujat_acquired_subcortex.png",
  "congenital","cortex",     "baujat_congenital_cortex.png",
  "congenital","subcortex",  "baujat_congenital_subcortex.png"
)

make_baujat_plot <- function(meta, etio, region_type, out_file) {
  dat <- subset_meta_region(meta, etio, region_type, require_variance = TRUE)
  title <- paste("Baujat plot -", stringr::str_to_title(etio), ifelse(region_type == "cortex", "cortex", "subcortex + cerebellum"))
  path <- file.path(output_dir, out_file)
  k <- nrow(dat)

  if (k < 2) {
    write_placeholder_plot(
      path,
      title,
      c(
        paste0("Not enough effect sizes with variance (k = ", k, ")."),
        "Baujat plot requires a fitted meta-analytic model."
      ),
      width = 900,
      height = 600
    )
    message("Saved placeholder ", path)
    return(invisible(NULL))
  }

  dat <- make_study_labels(dat)
  fit <- tryCatch(
    metafor::rma(
      yi = dat$Hedges_g_exact,
      vi = dat$Hedges_g_variance,
      data = dat,
      method = "REML",
      slab = dat$Study
    ),
    error = function(err) err
  )

  if (inherits(fit, "error")) {
    write_placeholder_plot(path, title, c("Model fit failed.", fit$message), width = 900, height = 600)
    message("Saved placeholder ", path)
    return(invisible(NULL))
  }

  bj <- tryCatch(metafor::baujat(fit, plot = FALSE), error = function(err) err)
  if (inherits(bj, "error")) {
    write_placeholder_plot(path, title, c("Baujat diagnostics failed.", bj$message), width = 900, height = 600)
    message("Saved placeholder ", path)
    return(invisible(NULL))
  }

  max_x <- max(bj$x, na.rm = TRUE) * 1.2
  max_y <- max(bj$y, na.rm = TRUE) * 1.2
  if (!is.finite(max_x) || max_x <= 0) max_x <- 1
  if (!is.finite(max_y) || max_y <= 0) max_y <- 1

  grDevices::png(path, width = 900, height = 600, res = 150)
  metafor::baujat(
    fit,
    xlim = c(0, max_x),
    ylim = c(0, max_y),
    bty = "l",
    las = 1,
    main = title,
    symbol = "slab",
    grid = TRUE
  )
  grDevices::dev.off()
  message("Saved ", path)
}

for (i in seq_len(nrow(plot_specs))) {
  make_baujat_plot(meta, plot_specs$etio[i], plot_specs$region_type[i], plot_specs$filename[i])
}

message("Finished Baujat plots.")
