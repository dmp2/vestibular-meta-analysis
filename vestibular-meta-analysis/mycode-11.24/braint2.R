##############################
## CONFIG
##############################

input_file  <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24/output_with_g.csv"
output_dir  <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24"
etiology_target <- "acquired"
output_png <- file.path(output_dir, "brainpanel_acquired_DK_ASEG.png")

##############################
## LIBRARIES
##############################

library(ggseg)
library(dplyr)
library(stringr)
library(ggplot2)
library(patchwork)
library(readr)

##############################
## LOAD DATA
##############################

meta <- read_csv(input_file, show_col_types = FALSE)

meta_acq <- meta %>%
  filter(
    !is.na(ROI_Homogenized),
    !is.na(Hedges_g_exact),
    tolower(Congenital_or_Acquired) == tolower(etiology_target)
  ) %>%
  mutate(
    ROI_clean = ROI_Homogenized %>%
      tolower() %>%
      str_squish() %>%
      ifelse(is.na(.), "", .)
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
  "lingual gyrus",                                "lingual",
  "lateral occipital cortex",                    "lateraloccipital",
  "middle frontal gyrus",                        "rostralmiddlefrontal",
  "middle temporal gyrus",                       "middletemporal",
  "postcentral gyrus",                           "postcentral",
  "precentral gyrus",                             "precentral",
  "precuneus",                                    "precuneus",
  "superior frontal gyrus",                      "superiorfrontal",
  "superior temporal gyrus",                      "superiortemporal",
  "supramarginal gyrus",                          "supramarginal",
  "superior parietal",                            "superiorparietal"
)

match_dk_region <- function(roi_clean){
  hits <- dk_map$region[sapply(dk_map$pattern, function(p) str_detect(roi_clean,p))]
  if (length(hits)==0) return(NA_character_)
  hits[1]
}

meta_cortex <- meta_acq %>%
  rowwise() %>%
  mutate(
    dk_region = match_dk_region(ROI_clean)
  ) %>%
  ungroup() %>%
  filter(!is.na(dk_region))

cat("CORTEX regions mapped:", length(unique(meta_cortex$dk_region)), "\n")

cortex_values <- meta_cortex %>%
  mutate(w = ifelse(!is.na(Hedges_g_variance)&Hedges_g_variance>0,
                    1/Hedges_g_variance,1)) %>%
  group_by(dk_region) %>%
  summarise(value = sum(Hedges_g_exact*w)/sum(w), .groups="drop") %>%
  rename(region = dk_region)

# attach value to dk atlas
dk_atlas <- ggseg::dk
dk_atlas$data <- dk_atlas$data %>%
  left_join(cortex_values, by = "region")

# symmetric scale
mx <- max(abs(cortex_values$value), na.rm=TRUE); mx <- ifelse(mx==0,1,mx)

make_dk_plot <- function(hemi, view, title){
  ggseg(
    atlas = dk_atlas,
    hemi  = hemi,
    view  = view,
    mapping = aes(fill = value)
  ) +
    scale_fill_gradient2(low="#4575B4", mid="white", high="#D73027",
                         limits=c(-mx,mx), midpoint=0, na.value="grey85") +
    ggtitle(title) +
    theme_void() +
    theme(plot.title=element_text(size=10,hjust=0.5),
          legend.position="right")
}

p_LL <- make_dk_plot("left","lateral","Left lateral")
p_LM <- make_dk_plot("left","medial","Left medial")
p_RL <- make_dk_plot("right","lateral","Right lateral")
p_RM <- make_dk_plot("right","medial","Right medial")

panel_cortex <- (p_LL | p_LM) / (p_RL | p_RM)

##############################
## ASEG SUBCORTEX + CEREBELLUM
##############################

sub_map <- tribble(
  ~pattern,                    ~label,
  "hippocampus",               "hippocampus",
  "amygdala",                  "amygdala",
  "caudate",                   "caudate",
  "putamen",                   "putamen",
  "pallidum",                  "pallidum",
  "accumb",                    "accumbens",
  "thalam",                    "thalamus",
  "brainstem",                 "brainstem",
  "pons",                      "brainstem",
  "cerebell",                  "cerebellum",
  "vermis",                    "cerebellum"
)

match_sub_label <- function(roi_clean){
  hits <- sub_map$label[sapply(sub_map$pattern, function(p) str_detect(roi_clean,p))]
  if(length(hits)==0) return(NA_character_)
  hits[1]
}

meta_sub <- meta_acq %>%
  rowwise() %>%
  mutate(sub_label = match_sub_label(ROI_clean)) %>%
  ungroup() %>%
  filter(!is.na(sub_label))

cat("SUB+CEREB regions mapped:", length(unique(meta_sub$sub_label)), "\n")

sub_values <- meta_sub %>%
  mutate(w = ifelse(!is.na(Hedges_g_variance)&Hedges_g_variance>0,
                    1/Hedges_g_variance,1)) %>%
  group_by(sub_label) %>%
  summarise(value = sum(Hedges_g_exact*w)/sum(w), .groups="drop")

aseg_atlas <- ggseg::aseg
aseg_atlas$data <- aseg_atlas$data %>%
  mutate(region_clean = tolower(region)) %>%
  left_join(
    sub_values %>% mutate(
      region_clean = case_when(
        sub_label=="hippocampus" ~ "hippocamp",
        sub_label=="amygdala"    ~ "amyg",
        sub_label=="caudate"     ~ "caudate",
        sub_label=="putamen"     ~ "putamen",
        sub_label=="pallidum"    ~ "pallid",
        sub_label=="accumbens"   ~ "accumb",
        sub_label=="thalamus"    ~ "thalam",
        sub_label=="brainstem"   ~ "brain-stem",
        sub_label=="cerebellum"  ~ "cerebell",
        TRUE ~ NA_character_
      )
    ),
    by="region_clean"
  )

mx2 <- max(abs(aseg_atlas$data$value),na.rm=TRUE); mx2 <- ifelse(mx2==0,mx,mx2)

p_sub <- ggseg(
  atlas = aseg_atlas,
  mapping = aes(fill=value)
) +
  scale_fill_gradient2(low="#4575B4", mid="white", high="#D73027",
                       limits=c(-mx2,mx2), midpoint=0, na.value="grey85") +
  ggtitle(paste(etiology_target,"Subcortex + Cerebellum")) +
  theme_void() +
  theme(plot.title=element_text(size=10,hjust=0.5),
        legend.position="right")

##############################
## FINAL PANEL (SAFE)
##############################

final_panel <- panel_cortex / p_sub

ggsave(output_png, final_panel, width=12, height=10, dpi=300)

cat("✅ Saved combined DK + ASEG panel:\n", output_png, "\n")
