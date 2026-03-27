############################################################
## CONFIG
############################################################

input_file <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24/output_with_g.csv"
output_dir <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24"
if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

############################################################
## LIBRARIES
############################################################

library(metafor)
library(readr)
library(dplyr)
library(stringr)
library(tibble)

############################################################
## LOAD + BASIC CLEANING
############################################################

meta <- read_csv(input_file, show_col_types = FALSE) %>%
  mutate(
    Congenital_or_Acquired = tolower(Congenital_or_Acquired),
    ROI_clean = ifelse(
      is.na(ROI_Homogenized),
      "",
      str_squish(tolower(ROI_Homogenized))
    )
  )

############################################################
## DK CORTEX MAPPING  (same as cortex-only brain plot)
############################################################

dk_map <- tribble(
  ~pattern,                    ~region,
  "anterior cingulate cortex", "rostralanteriorcingulate",
  "cingulate gyrus",           "posteriorcingulate",
  "cuneus",                    "cuneus",
  "fusiform gyrus",            "fusiform",
  "insula",                    "insula",
  "lateral occipital cortex",  "lateraloccipital",
  "lingual gyrus",             "lingual",
  "middle frontal gyrus",      "rostralmiddlefrontal",
  "middle temporal gyrus",     "middletemporal",
  "precentral gyrus",          "precentral",
  "postcentral gyrus",         "postcentral",
  "precuneus",                 "precuneus",
  "superior frontal gyrus",    "superiorfrontal",
  "superior temporal gyrus",   "superiortemporal",
  "superior orbitofrontal",    "lateralorbitofrontal",
  "superior orbitofrontal cortex", "lateralorbitofrontal",
  "supramarginal gyrus",       "supramarginal"
)

match_dk_region <- function(roi_clean) {
  hits <- dk_map$region[
    sapply(dk_map$pattern, function(p) str_detect(roi_clean, p))
  ]
  if (length(hits) == 0) return(NA_character_)
  hits[1]
}

############################################################
## ASEG SUBCORTEX / CEREBELLUM MAPPING  (FIXED VERMIS)
############################################################

sub_map <- tribble(
  ~pattern,        ~label,
  "hippocampus",   "hippocampus",
  "parahippocamp", "hippocampus",
  "amygdala",      "amygdala",
  "caudate",       "caudate",
  "putamen",       "putamen",
  "pallid",        "pallidum",
  "accumb",        "accumbens",
  "thalam",        "thalamus",
  "brainstem",     "brainstem",
  "pons",          "brainstem",
  "cerebell",      "cerebellum",
  "vermi",         "cerebellum"   # catches 'vermian', 'vermis', etc.
)

match_sub_label <- function(roi_clean) {
  hits <- sub_map$label[
    sapply(sub_map$pattern, function(p) str_detect(roi_clean, p))
  ]
  if (length(hits) == 0) return(NA_character_)
  hits[1]
}

############################################################
## ADD REGION LABELS TO EVERY ROW
############################################################

meta_regions <- meta %>%
  rowwise() %>%
  mutate(
    dk_region = match_dk_region(ROI_clean),
    sub_label = match_sub_label(ROI_clean)
  ) %>%
  ungroup()

############################################################
## GENERAL FUNNEL PLOT HELPER
##   etio = "acquired" / "congenital"
##   type = "cortex" / "subcortex"
############################################################

make_funnel <- function(etio, type, filename) {
  
  dat <- meta_regions %>%
    filter(
      Congenital_or_Acquired == etio,
      !is.na(Hedges_g_exact),
      !is.na(Hedges_g_variance)
    )
  
  if (type == "cortex") {
    dat <- dat %>% filter(!is.na(dk_region))
    region_desc <- "cortex"
  } else {
    dat <- dat %>% filter(!is.na(sub_label))
    region_desc <- "subcortex + cerebellum"
  }
  
  k <- nrow(dat)
  
  png(file.path(output_dir, filename), width = 800, height = 800)
  
  if (k == 0) {
    ## no data at all
    plot.new()
    title(main = paste(
      "Funnel plot –", str_to_title(etio), region_desc
    ))
    text(0.5, 0.5,
         labels = "No effect sizes with variance available.",
         cex = 1)
    dev.off()
    message("No data for ", etio, " (", region_desc, ")")
    return(invisible(NULL))
  }
  
  if (k == 1) {
    ## cannot run metafor::rma, show a clear warning figure
    plot.new()
    title(main = paste(
      "Funnel plot –", str_to_title(etio), region_desc
    ))
    text(0.5, 0.6,
         labels = paste0("Only one effect size (k = 1).\n",
                         "Funnel plot not interpretable."),
         cex = 1)
    # also show its g value for completeness
    g1 <- round(dat$Hedges_g_exact[1], 3)
    roi1 <- dat$ROI_Homogenized[1]
    text(0.5, 0.35,
         labels = paste0("ROI: ", roi1, "\nHedges g = ", g1),
         cex = 0.9)
    dev.off()
    message("Only k = 1 for ", etio, " (", region_desc, ")")
    return(invisible(NULL))
  }
  
  ## k >= 2 → run random-effects model + proper funnel
  yi <- dat$Hedges_g_exact
  vi <- dat$Hedges_g_variance
  m  <- rma(yi = yi, vi = vi, method = "REML")
  
  funnel(
    m,
    level   = c(90, 95, 99),
    refline = 0,
    yaxis   = "sei",
    xlab    = "Effect size (Hedges g, residuals)",
    ylab    = "Standard error",
    shade   = c("grey90", "grey70", "grey50"),
    legend  = TRUE,
    pch     = 19,
    cex     = 1.2,
    main    = paste("Funnel plot –",
                    str_to_title(etio), region_desc)
  )
  
  # vertical line for pooled g
  abline(v = m$b[1], lty = 1, lwd = 2)
  
  # display k and I²
  info <- paste0("k = ", k, ", I² = ", round(m$I2, 1), "%")
  mtext(info, side = 3, adj = 1, line = -1, cex = 0.9)
  
  # (optional) Egger test output to console
  message("Egger test for ", etio, " (", type, "):")
  print(regtest(m, model = "rma"))
  
  dev.off()
  message("Saved ", filename)
}

############################################################
## MAKE THE 4 FUNNEL PLOTS
############################################################

make_funnel("acquired",   "cortex",    "funnel_acquired_cortex.png")
make_funnel("acquired",   "subcortex", "funnel_acquired_subcortex.png")
make_funnel("congenital", "cortex",    "funnel_congenital_cortex.png")
make_funnel("congenital", "subcortex", "funnel_congenital_subcortex.png")
