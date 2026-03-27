##############################
## CONFIG
##############################

input_file  <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24/output_with_g.csv"
output_dir  <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24"

etiology_target <- "acquired"   # change to "congenital" for that group
output_png <- file.path(output_dir,
                        paste0("brainpanel_", etiology_target, "_DK_cortex_only.png"))

##############################
## LIBRARIES
##############################

library(ggseg)
library(dplyr)
library(stringr)
library(ggplot2)
library(patchwork)
library(readr)
library(tibble)

# Clean base theme
theme_set(
  theme_void(base_size = 10) +
    theme(
      plot.title.position = "plot",
      plot.title = element_text(hjust = 0.5, size = 11),
      strip.text = element_blank(),
      strip.background = element_blank()
    )
)

##############################
## LOAD + FILTER DATA
##############################

meta <- read_csv(input_file, show_col_types = FALSE)

meta_etio <- meta %>%
  filter(
    !is.na(ROI_Homogenized),
    !is.na(Hedges_g_exact),
    tolower(Congenital_or_Acquired) == tolower(etiology_target)
  ) %>%
  mutate(
    ROI_clean = ifelse(
      is.na(ROI_Homogenized),
      "",
      str_squish(tolower(ROI_Homogenized))
    )
  )

cat("Rows in dataset with g for", etiology_target, ":", nrow(meta_etio), "\n")

##############################
## DK CORTEX-ONLY MAPPING
## (ONLY the cortical ROIs you listed)
##############################

# Whitelist of cortical patterns → DK regions
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

# Helper to map ROI_clean → DK region, only if it matches one of these patterns
match_dk_region <- function(roi_clean){
  hits <- dk_map$region[
    sapply(dk_map$pattern, function(p) str_detect(roi_clean, p))
  ]
  if (length(hits) == 0) return(NA_character_)
  hits[1]
}

# Attach DK region only for cortical ROIs
meta_cortex <- meta_etio %>%
  rowwise() %>%
  mutate(dk_region = match_dk_region(ROI_clean)) %>%
  ungroup() %>%
  filter(!is.na(dk_region))   # drop anything non-cortical / non-DK

cat("CORTEX-ONLY: ROIs mapped to DK regions:",
    length(unique(meta_cortex$dk_region)), "\n")

##############################
## AGGREGATE HEDGES g PER DK REGION
##############################

cortex_values <- meta_cortex %>%
  mutate(
    w = ifelse(!is.na(Hedges_g_variance) & Hedges_g_variance > 0,
               1 / Hedges_g_variance, 1)
  ) %>%
  group_by(dk_region) %>%
  summarise(
    value = sum(Hedges_g_exact * w, na.rm = TRUE) / sum(w, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  rename(region = dk_region)

dk_atlas <- ggseg::dk
dk_atlas$data <- dk_atlas$data %>%
  left_join(cortex_values, by = "region")

max_abs_cx <- max(abs(cortex_values$value), na.rm = TRUE)
if (!is.finite(max_abs_cx) || max_abs_cx == 0) max_abs_cx <- 1

##############################
## DK CORTEX PLOTTING FUNCTION
##############################

make_dk_plot <- function(hemi, view, subtitle){
  ggseg(
    atlas   = dk_atlas,
    hemi    = hemi,
    view    = view,
    mapping = aes(fill = value),
    colour  = "grey30",  # darker borders
    size    = 0.3        # thicker boundaries
  ) +
    scale_fill_gradient2(
      name     = "Hedges g",
      low      = "#4575B4",
      mid      = "white",
      high     = "#D73027",
      limits   = c(-max_abs_cx, max_abs_cx),
      midpoint = 0,
      na.value = "grey90"
    ) +
    ggtitle(subtitle) +
    theme(
      plot.title = element_text(
        size   = 11,
        hjust  = 0.5,
        margin = margin(b = 4)
      ),
      legend.position = "right",
      plot.margin = margin(5, 5, 5, 5)
    )
}

##############################
## 4 DK CORTEX VIEWS + SAVE
##############################

p_LL <- make_dk_plot("left",  "lateral",
                     paste(etiology_target, "left Lateral"))
p_LM <- make_dk_plot("left",  "medial",
                     paste(etiology_target, "left Medial"))
p_RL <- make_dk_plot("right", "lateral",
                     paste(etiology_target, "right Lateral"))
p_RM <- make_dk_plot("right", "medial",
                     paste(etiology_target, "right Medial"))

# 2×2 panel, no ASEG, so patchwork is safe
panel_cortex <- (p_LL | p_LM) / (p_RL | p_RM)

ggsave(
  filename = output_png,
  plot     = panel_cortex,
  width    = 9,
  height   = 7,
  dpi      = 300,
  bg       = "white"
)

cat("✅ Saved DK cortex-only panel to:\n", output_png, "\n")
