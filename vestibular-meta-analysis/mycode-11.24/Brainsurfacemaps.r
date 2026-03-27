############################################################
# brainsurfacemaps.R
# Acquired vestibular disorders – cortical brain map (DK)
# Pools Hedges g per ROI (simple mean) and plots:
#   left/right × lateral/medial (4 panels)
############################################################

## ---- 0. Packages ----
## Run these once if needed:
## install.packages(c("dplyr","readr","ggseg","ggplot2","stringr","patchwork"))

library(dplyr)
library(readr)
library(ggseg)
library(ggplot2)
library(stringr)
library(patchwork)

## ---- 1. File paths ----
INPUT_FILE <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24/output_with_g.csv"
OUTPUT_PNG <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24/brain_acquired_DK2.png"

## ---- 2. Load data ----
dat_all <- read_csv(INPUT_FILE, show_col_types = FALSE)

stopifnot(
  "Congenital_or_Acquired" %in% names(dat_all),
  "ROI_Homogenized"       %in% names(dat_all),
  "Hedges_g_exact"        %in% names(dat_all)
)

## ---- 3. Filter to acquired + non-missing g ----
dat_acq <- dat_all %>%
  filter(
    tolower(Congenital_or_Acquired) == "acquired",
    !is.na(ROI_Homogenized),
    !is.na(Hedges_g_exact)
  ) %>%
  mutate(
    ROI_clean = tolower(ROI_Homogenized)
  )

cat("Rows in acquired dataset (with g):", nrow(dat_acq), "\n")
if (nrow(dat_acq) == 0) {
  stop("No acquired rows with non-NA Hedges_g_exact.")
}

## ---- 4. Simple pooled Hedges g per ROI (mean) ----
meta_acq <- dat_acq %>%
  group_by(ROI_Homogenized, ROI_clean) %>%
  summarise(
    g  = mean(Hedges_g_exact, na.rm = TRUE),
    k  = sum(!is.na(Hedges_g_exact)),
    .groups = "drop"
  ) %>%
  filter(!is.na(g), k > 0)

cat("Unique ROIs in acquired meta:", nrow(meta_acq), "\n")
cat("ROI list:\n")
print(unique(meta_acq$ROI_Homogenized))

## ---- 5. Map ROIs to DK atlas regions (custom to your ROIs) ----
dk_map <- tribble(
  ~pattern,                                      ~region,
  "anterior cingulate cortex",                   "rostralanteriorcingulate",
  "cingulate gyrus",                             "posteriorcingulate",
  "cuneus",                                      "cuneus",
  "fusiform",                                    "fusiform",
  "insula",                                      "insula",
  "intracalcarine",                              "pericalcarine",
  "lateral occipital",                           "lateraloccipital",
  "lingual gyrus",                               "lingual",
  "middle frontal gyrus",                        "rostralmiddlefrontal",
  "middle temporal gyrus (mt/v5)",               "middletemporal",
  "middle temporal gyrus",                       "middletemporal",
  "postcentral gyrus",                           "postcentral",
  "precentral gyrus",                            "precentral",
  "precuneus / superior parietal white matter",  "superiorparietal",
  "precuneus",                                   "precuneus",
  "superior frontal gyrus",                      "superiorfrontal",
  "superior orbitofrontal cortex",               "lateralorbitofrontal",
  "superior temporal gyrus",                     "superiortemporal",
  "supramarginal gyrus",                         "supramarginal"
)

match_dk_region <- function(roi_clean) {
  hits <- dk_map$region[
    sapply(dk_map$pattern, function(p) str_detect(roi_clean, p))
  ]
  if (length(hits) == 0) return(NA_character_)
  hits[1]
}

meta_acq <- meta_acq %>%
  rowwise() %>%
  mutate(
    dk_region = match_dk_region(ROI_clean)
  ) %>%
  ungroup() %>%
  filter(!is.na(dk_region))

cat("ROIs mapped to DK regions:", nrow(meta_acq), "\n")

## ---- 6. Aggregate by DK region (avoid many-to-many) ----
meta_acq_region <- meta_acq %>%
  group_by(dk_region) %>%
  summarise(
    value = mean(g, na.rm = TRUE),
    k_sum = sum(k),
    .groups = "drop"
  ) %>%
  rename(region = dk_region)

cat("DK regions with data:", nrow(meta_acq_region), "\n")

## ---- 7. Colour scale ----
max_abs <- max(abs(meta_acq_region$value), na.rm = TRUE)
if (!is.finite(max_abs) || max_abs == 0) max_abs <- 1
col_limits <- c(-max_abs, max_abs)
cat("Colour scale limits:", col_limits, "\n")

## ---- 8. Join pooled g with DK atlas ----
dk_atlas <- ggseg::dk
dk_atlas$data <- dk_atlas$data %>%
  left_join(meta_acq_region, by = "region")

## ---- 9. Helper for one hemisphere/view ----
plot_hemi_view <- function(hemi, view, subtitle) {
  ggseg(
    atlas   = dk_atlas,
    hemi    = hemi,
    view    = view,
    mapping = aes(fill = value),
    color   = "black",
    size    = 0.3
  ) +
    scale_fill_gradient2(
      low       = "#08306b",
      mid       = "white",
      high      = "#a50026",
      midpoint  = 0,
      limits    = col_limits,
      na.value  = "grey85",
      name      = "Hedges g"
    ) +
    ggtitle(paste("acquired", subtitle)) +
    theme_void() +
    theme(
      plot.title      = element_text(hjust = 0.5, size = 11),
      legend.position = "right"
    )
}

p_LL <- plot_hemi_view("left",  "lateral", "left Lateral")
p_LM <- plot_hemi_view("left",  "medial",  "left Medial")
p_RL <- plot_hemi_view("right", "lateral", "right Lateral")
p_RM <- plot_hemi_view("right", "medial",  "right Medial")

## ---- 10. Combine panels and save ----
panel <- (p_LL | p_LM) / (p_RL | p_RM)

ggsave(
  filename = OUTPUT_PNG,
  plot     = panel,
  width    = 10,
  height   = 8,
  dpi      = 300
)

cat("✅ Saved acquired brain map to:\n", OUTPUT_PNG, "\n")
