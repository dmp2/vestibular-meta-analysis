# ==========================================================
# compute_hedges_g.R (FIXED VERSION — NO LIST COLUMN ERRORS)
# Computes Hedges g from t / z / F + n1 + n2 + Direction
# ==========================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(stringr)
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

SCRIPT_DIR <- get_script_dir()
input_file <- file.path(SCRIPT_DIR, "output.csv")
output_file <- file.path(SCRIPT_DIR, "output_with_g_computed.csv")

if (!file.exists(input_file)) {
  stop("Missing input file: ", input_file)
}

dat <- read_csv(input_file, show_col_types = FALSE)

# -----------------------
# Helper: sign from Direction
# -----------------------
get_sign <- function(direction) {
  if (is.na(direction)) return(NA_real_)
  direction <- trimws(direction)
  if (direction == "↑ Patients > Controls") return(1)
  if (direction == "↓ Patients < Controls") return(-1)
  return(NA_real_)
}

# -----------------------
# Compute Cohen's d from t/z/F
# -----------------------
compute_d <- function(type, stat, n1, n2, direction) {
  if (is.na(type) || is.na(stat) || is.na(n1) || is.na(n2) ||
      n1 <= 0 || n2 <= 0) {
    return(NA_real_)
  }
  
  type <- tolower(trimws(type))
  
  # allow only t, z, f
  if (!(type %in% c("t", "z", "f"))) {
    return(NA_real_)
  }
  
  # convert F to t
  if (type == "f") {
    stat <- sqrt(stat)
  }
  
  se_factor <- sqrt(1/n1 + 1/n2)
  d_raw <- stat * se_factor
  
  sgn <- get_sign(direction)
  
  if (!is.na(sgn)) {
    return(sgn * abs(d_raw))
  } else {
    return(d_raw)  # if we cannot infer sign
  }
}

# -----------------------
# Compute Hedges g + variance
# -----------------------
compute_g <- function(d, n1, n2) {
  if (is.na(d) || is.na(n1) || is.na(n2) || n1 <= 0 || n2 <= 0) {
    return(c(NA_real_, NA_real_))
  }
  
  N <- n1 + n2
  if (N <= 2) return(c(NA_real_, NA_real_))
  
  J <- 1 - 3 / (4 * N - 9)  # correction
  g <- J * d
  var_g <- J^2 * ((N / (n1 * n2)) + (g^2 / (2 * (N - 2))))
  
  return(c(g, var_g))
}

# -----------------------
# APPLY to every row safely
# -----------------------
dat2 <- dat %>%
  mutate(
    n1 = Sample_Size_Patients,
    n2 = Sample_Size_Controls
  ) %>%
  rowwise() %>%
  mutate(
    # Step 1 — compute d if needed
    d_calc = compute_d(Statistic_type, Statistic_value, n1, n2, Direction),
    
    # Step 2 — compute g + var
    g_out  = list(compute_g(d_calc, n1, n2)),  # list to hold the pair
    
    g_calc     = g_out[[1]][1],
    var_g_calc = g_out[[1]][2],
    
    # Step 3 — fill in missing values only
    Hedges_g_exact     = ifelse(is.na(Hedges_g_exact), g_calc, Hedges_g_exact),
    Hedges_g_variance  = ifelse(is.na(Hedges_g_variance), var_g_calc, Hedges_g_variance)
  ) %>%
  ungroup() %>%
  select(-n1, -n2, -d_calc, -g_out, -g_calc, -var_g_calc)

# -----------------------
# Summary
# -----------------------
filled_n <- sum(!is.na(dat2$Hedges_g_exact))
total_n  <- sum(!is.na(dat2$ROI_Homogenized))

message("Computed Hedges g for ", filled_n, " rows out of ", total_n, " ROIs.")

write_csv(dat2, output_file)
message("Saved ", output_file)
