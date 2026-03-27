#!/usr/bin/env Rscript

############################################################
# run_brain_plot_pipeline.R
#
# Stable repo-relative pipeline for the verified brain plots:
#   1. mycode-11.24/output.csv
#   2. mycode-11.24/compute_hedges_g.R
#   3. brain_plots_master.R
############################################################

get_script_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg) > 0) {
    return(dirname(normalizePath(sub("^--file=", "", file_arg[1]))))
  }
  normalizePath(getwd())
}

ROOT_DIR <- get_script_dir()
legacy_dir <- file.path(ROOT_DIR, "mycode-11.24")
compute_script <- file.path(legacy_dir, "compute_hedges_g.R")
brain_script <- file.path(ROOT_DIR, "brain_plots_master.R")
input_csv <- file.path(legacy_dir, "output.csv")

if (!file.exists(input_csv)) {
  stop("Missing upstream input file: ", input_csv)
}

if (!file.exists(compute_script)) {
  stop("Missing compute script: ", compute_script)
}

if (!file.exists(brain_script)) {
  stop("Missing brain plot script: ", brain_script)
}

message("Stage 1: compute Hedges g from ", input_csv)
source(compute_script, local = new.env(parent = globalenv()))

message("Stage 2: generate verified acquired brain plots")
source(brain_script, local = new.env(parent = globalenv()))

message("Finished stable brain-plot pipeline.")
