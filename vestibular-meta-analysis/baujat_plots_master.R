#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(metafor)
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

group_field <- "Review_Group"
region_types <- c("cortex", "subcortex")

describe_skip <- function(group_value, region_type, reason) {
  message("Skipping Baujat plot for ", group_value, " / ", region_type, ": ", reason)
}

make_baujat_plot <- function(meta, group_field, group_value, region_type) {
  title <- paste(
    "Baujat plot -",
    group_value,
    ifelse(region_type == "cortex", "cortex", "subcortex + cerebellum")
  )
  path <- file.path(
    output_dir,
    paste0("baujat_", safe_slug(group_field), "_", safe_slug(group_value), "_", region_type, ".png")
  )

  base_dat <- subset_meta_group(meta, group_field, group_value, region_type = region_type)
  if (nrow(base_dat) == 0) {
    describe_skip(group_value, region_type, "no eligible effect-size rows in the reconciled table")
    return(invisible(NULL))
  }

  dat <- subset_meta_group(meta, group_field, group_value, region_type = region_type, require_variance = TRUE) %>%
    mutate(
      Hedges_g_exact = as.numeric(Hedges_g_exact),
      Hedges_g_variance = as.numeric(Hedges_g_variance)
    ) %>%
    filter(!is.na(Hedges_g_exact), !is.na(Hedges_g_variance)) %>%
    make_study_labels()

  k <- nrow(dat)
  if (k == 0) {
    describe_skip(group_value, region_type, "no effect sizes with variance available after reconciliation")
    return(invisible(NULL))
  }

  if (k < 2) {
    describe_skip(group_value, region_type, paste0("need at least 2 variance-eligible rows, found k = ", k))
    return(invisible(NULL))
  }

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
    describe_skip(group_value, region_type, paste0("model fit failed: ", fit$message))
    return(invisible(NULL))
  }

  plot_result <- tryCatch({
    grDevices::png(path, width = 900, height = 600, res = 150)
    metafor::baujat(
      fit,
      bty = "l",
      las = 1,
      main = title,
      symbol = "slab",
      grid = TRUE
    )
    grDevices::dev.off()
    NULL
  }, error = function(err) {
    if (grDevices::dev.cur() > 1) {
      grDevices::dev.off()
    }
    err
  })

  if (inherits(plot_result, "error")) {
    describe_skip(group_value, region_type, paste0("Baujat plotting failed: ", plot_result$message))
    return(invisible(NULL))
  }

  message("Saved ", path)
}

eligibility <- summarize_plot_eligibility(meta, group_field = group_field)
message("Secondary-plot eligibility summary:")
print(eligibility)

for (group_value in available_group_values(meta, group_field)) {
  for (region_type in region_types) {
    make_baujat_plot(meta, group_field, group_value, region_type)
  }
}

message("Finished Baujat plots.")
