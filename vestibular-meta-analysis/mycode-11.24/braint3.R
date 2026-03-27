##############################
## CONFIG
##############################

input_file  <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24/output_with_g.csv"
output_dir  <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24"
etiology_target <- "acquired"

# Output figure paths
png_LL  <- file.path(output_dir, "acquired_left_lateral_DK.png")
png_LM  <- file.path(output_dir, "acquired_left_medial_DK.png")
png_RL  <- file.path(output_dir, "acquired_right_lateral_DK.png")
png_RM  <- file.path(output_dir, "acquired_right_medial_DK.png")
png_SUB <- file.path(output_dir, "acquired_subcortex_cerebellum_ASEG.png")

##############################
## LIBRARIES
##############################

library(ggseg)
library(dplyr)
library(stringr)
library(ggplot2)
library(readr)
library(tibble)

# Compact, clean base theme
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

meta_acq <- meta %>%
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


cat("Rows in acquired dataset with g:", nrow(meta_acq), "\n")

##############################
## DK CORTEX MAPPING
##############################

dk_map <- tribble(
  ~pattern,                                      ~region,
  "anterior cingulate cortex",                   "rostralanteriorcingulate",
  "cingulate gyrus",                             "posteriorcingulate",
  "cuneus",                                      "cuneus",
  "fusiform gyrus",                              "fusiform",
  "insula",                                      "insula",
  "intracalcarine cortex",                       "pericalcarine",
  "lingual gyrus",                               "lingual",
  "lateral occipital cortex",                    "lateraloccipital",
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

match_dk_region <- function(roi_clean){
  hits <- dk_map$region[
    sapply(dk_map$pattern, function(p) str_detect(roi_clean, p))
  ]
  if (length(hits) == 0) return(NA_character_)
  hits[1]
}

meta_cortex <- meta_acq %>%
  rowwise() %>%
  mutate(dk_region = match_dk_region(ROI_clean)) %>%
  ungroup() %>%
  filter(!is.na(dk_region))

cat("CORTEX: ROIs mapped to DK regions:", length(unique(meta_cortex$dk_region)), "\n")

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
    colour  = "grey30",  # darker parcel borders
    size    = 0.3        # thicker outlines
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
## SAVE DK CORTEX PANELS (4 PNGs)
##############################

p_LL <- make_dk_plot("left",  "lateral", "acquired – left lateral")
p_LM <- make_dk_plot("left",  "medial",  "acquired – left medial")
p_RL <- make_dk_plot("right", "lateral", "acquired – right lateral")
p_RM <- make_dk_plot("right", "medial",  "acquired – right medial")

ggsave(png_LL, p_LL, width = 4, height = 3, dpi = 300, bg = "white")
ggsave(png_LM, p_LM, width = 4, height = 3, dpi = 300, bg = "white")
ggsave(png_RL, p_RL, width = 4, height = 3, dpi = 300, bg = "white")
ggsave(png_RM, p_RM, width = 4, height = 3, dpi = 300, bg = "white")

cat("✅ Saved cortex PNGs:\n",
    png_LL, "\n", png_LM, "\n", png_RL, "\n", png_RM, "\n")

##############################
## ASEG SUBCORTEX + CEREBELLUM
##############################

sub_map <- tribble(
  ~pattern,                    ~label,
  "hippocampus",               "hippocamp",
  "parahippocampus",           "hippocamp",
  "amygdala",                  "amygdala",
  "caudate",                   "caudate",
  "putamen",                   "putamen",
  "pallidum",                  "pallidum",
  "accumbens",                 "accumbens-area",
  "thalamus",                  "thalamus",
  "brainstem",                 "brain-stem",
  "pons",                      "brain-stem",
  "cerebell",                  "cerebellum-cortex",
  "vermis",                    "cerebellum-cortex"
)

match_sub_label <- function(roi_clean){
  hits <- sub_map$label[
    sapply(sub_map$pattern, function(p) str_detect(roi_clean, p))
  ]
  if (length(hits) == 0) return(NA_character_)
  hits[1]
}

meta_sub <- meta_acq %>%
  rowwise() %>%
  mutate(sub_label = match_sub_label(ROI_clean)) %>%
  ungroup() %>%
  filter(!is.na(sub_label))

cat("SUB+CEREB: ROIs mapped:", length(unique(meta_sub$sub_label)), "\n")

sub_values <- meta_sub %>%
  mutate(
    w = ifelse(!is.na(Hedges_g_variance) & Hedges_g_variance > 0,
               1 / Hedges_g_variance, 1)
  ) %>%
  group_by(sub_label) %>%
  summarise(
    value = sum(Hedges_g_exact * w, na.rm = TRUE) / sum(w, na.rm = TRUE),
    .groups = "drop"
  )

aseg_atlas <- ggseg::aseg

aseg_atlas$data <- aseg_atlas$data %>%
  mutate(region_clean = tolower(region)) %>%
  left_join(
    sub_values %>%
      mutate(region_clean = sub_label),
    by = "region_clean"
  )

max_abs_sub <- max(abs(aseg_atlas$data$value), na.rm = TRUE)
if (!is.finite(max_abs_sub) || max_abs_sub == 0) max_abs_sub <- max_abs_cx

p_sub <- ggseg(
  atlas   = aseg_atlas,
  mapping = aes(fill = value),
  colour  = "grey30",  # darker subcortical boundaries
  size    = 0.3
) +
  scale_fill_gradient2(
    name     = "Hedges g",
    low      = "#4575B4",
    mid      = "white",
    high     = "#D73027",
    limits   = c(-max_abs_sub, max_abs_sub),
    midpoint = 0,
    na.value = "grey90"
  ) +
  ggtitle("acquired – subcortex + cerebellum") +
  theme(
    plot.title = element_text(
      size   = 11,
      hjust  = 0.5,
      margin = margin(b = 4)
    ),
    legend.position = "right",
    plot.margin = margin(5, 5, 5, 5)
  )

ggsave(png_SUB, p_sub, width = 4.5, height = 3.2, dpi = 300, bg = "white")
cat("✅ Saved subcortex+cerebellum PNG:\n", png_SUB, "\n")
