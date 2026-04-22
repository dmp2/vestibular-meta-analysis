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
meta <- load_secondary_plot_meta(root_dir, input_policy = "hybrid")

plot_specs <- tibble::tribble(
  ~etio,        ~region_type, ~filename,
  "acquired",   "cortex",     "funnel_acquired_cortex.png",
  "acquired",   "subcortex",  "funnel_acquired_subcortex.png",
  "congenital", "cortex",     "funnel_congenital_cortex.png",
  "congenital", "subcortex",  "funnel_congenital_subcortex.png"
)

describe_skip <- function(etio, region_type, reason) {
  message("Skipping funnel plot for ", etio, " / ", region_type, ": ", reason)
}

make_funnel_plot <- function(meta, etio, region_type, out_file) {
  title <- paste(
    "Funnel plot -",
    stringr::str_to_title(etio),
    ifelse(region_type == "cortex", "cortex", "subcortex + cerebellum")
  )
  path <- file.path(output_dir, out_file)

  base_dat <- subset_meta_region(meta, etio, region_type)
  if (nrow(base_dat) == 0) {
    describe_skip(etio, region_type, "no eligible effect-size rows in the reconciled table")
    return(invisible(NULL))
  }

  dat <- subset_meta_region(meta, etio, region_type, require_variance = TRUE) %>%
    mutate(
      Hedges_g_exact = as.numeric(Hedges_g_exact),
      Hedges_g_variance = as.numeric(Hedges_g_variance)
    ) %>%
    filter(!is.na(Hedges_g_exact), !is.na(Hedges_g_variance))

  k <- nrow(dat)
  if (k == 0) {
    describe_skip(etio, region_type, "no effect sizes with variance available after reconciliation")
    return(invisible(NULL))
  }

  if (k < 2) {
    describe_skip(etio, region_type, paste0("need at least 2 variance-eligible rows, found k = ", k))
    return(invisible(NULL))
  }

  fit <- tryCatch(
    metafor::rma(yi = dat$Hedges_g_exact, vi = dat$Hedges_g_variance, method = "REML"),
    error = function(err) err
  )

  if (inherits(fit, "error")) {
    describe_skip(etio, region_type, paste0("model fit failed: ", fit$message))
    return(invisible(NULL))
  }

  grDevices::png(path, width = 800, height = 800)
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

eligibility <- summarize_plot_eligibility(meta)
message("Secondary-plot eligibility summary:")
print(eligibility)

for (i in seq_len(nrow(plot_specs))) {
  make_funnel_plot(meta, plot_specs$etio[i], plot_specs$region_type[i], plot_specs$filename[i])
}

message("Finished funnel plots.")
