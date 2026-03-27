#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(metafor)
  library(readr)
  library(dplyr)
  library(stringr)
  library(tibble)
})

bootstrap_script_dir <- function() {
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
  "acquired",  "cortex",     "funnel_acquired_cortex.png",
  "acquired",  "subcortex",  "funnel_acquired_subcortex.png",
  "congenital","cortex",     "funnel_congenital_cortex.png",
  "congenital","subcortex",  "funnel_congenital_subcortex.png"
)

make_funnel_plot <- function(meta, etio, region_type, out_file) {
  dat <- subset_meta_region(meta, etio, region_type, require_variance = TRUE)
  title <- paste("Funnel plot -", stringr::str_to_title(etio), ifelse(region_type == "cortex", "cortex", "subcortex + cerebellum"))
  path <- file.path(output_dir, out_file)
  k <- nrow(dat)

  if (k == 0) {
    write_placeholder_plot(path, title, c("No effect sizes with variance available."))
    message("Saved placeholder ", path)
    return(invisible(NULL))
  }

  if (k == 1) {
    write_placeholder_plot(
      path,
      title,
      c(
        "Only one effect size available.",
        "Funnel plot is not interpretable.",
        paste0("ROI: ", dat$ROI_Homogenized[1]),
        paste0("Hedges g = ", round(dat$Hedges_g_exact[1], 3))
      )
    )
    message("Saved placeholder ", path)
    return(invisible(NULL))
  }

  grDevices::png(path, width = 800, height = 800)
  fit <- tryCatch(
    metafor::rma(yi = dat$Hedges_g_exact, vi = dat$Hedges_g_variance, method = "REML"),
    error = function(err) err
  )

  if (inherits(fit, "error")) {
    grDevices::dev.off()
    write_placeholder_plot(path, title, c("Model fit failed.", fit$message))
    message("Saved placeholder ", path)
    return(invisible(NULL))
  }

  metafor::funnel(
    fit,
    level = c(90, 95, 99),
    refline = 0,
    yaxis = "sei",
    xlab = "Effect size (Hedges g, residuals)",
    ylab = "Standard error",
    shade = c("grey90", "grey70", "grey50"),
    legend = TRUE,
    pch = 19,
    cex = 1.2,
    main = title
  )
  graphics::abline(v = fit$b[1], lty = 1, lwd = 2)
  graphics::mtext(
    paste0("k = ", k, ", I2 = ", round(fit$I2, 1), "%"),
    side = 3,
    adj = 1,
    line = -1,
    cex = 0.9
  )
  grDevices::dev.off()

  if (k >= 3) {
    message("Egger test for ", etio, " / ", region_type, ":")
    print(metafor::regtest(fit, model = "rma"))
  }

  message("Saved ", path)
}

purrr_like_loop <- seq_len(nrow(plot_specs))
for (i in purrr_like_loop) {
  make_funnel_plot(meta, plot_specs$etio[i], plot_specs$region_type[i], plot_specs$filename[i])
}

message("Finished funnel plots.")
