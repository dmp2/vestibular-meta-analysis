library(dplyr)
library(readr)

master_file <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24/output_with_g.csv"
json_file   <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24/jsonwithg.csv"
output_file <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24/output_final.csv"

# Load files
master <- read_csv(master_file, show_col_types = FALSE)
json   <- read_csv(json_file, show_col_types = FALSE)

# Keep only rows from json that actually have new effect size info
updates <- json %>%
  filter(
    !is.na(Hedges_g_exact) |
      !is.na(Hedges_g_variance) |
      !is.na(CI_lower) |
      !is.na(CI_upper)
  ) %>%
  select(
    Study_ID,
    ROI_Homogenized,
    Hedges_g_exact_new    = Hedges_g_exact,
    Hedges_g_variance_new = Hedges_g_variance,
    CI_lower_new          = CI_lower,
    CI_upper_new          = CI_upper
  )

# Merge: Study_ID + ROI_Homogenized are the key
merged <- master %>%
  left_join(updates,
            by = c("Study_ID", "ROI_Homogenized")) %>%
  mutate(
    Hedges_g_exact    = ifelse(!is.na(Hedges_g_exact_new),
                               Hedges_g_exact_new,
                               Hedges_g_exact),
    Hedges_g_variance = ifelse(!is.na(Hedges_g_variance_new),
                               Hedges_g_variance_new,
                               Hedges_g_variance),
    CI_lower          = ifelse(!is.na(CI_lower_new),
                               CI_lower_new,
                               CI_lower),
    CI_upper          = ifelse(!is.na(CI_upper_new),
                               CI_upper_new,
                               CI_upper)
  ) %>%
  select(
    -Hedges_g_exact_new,
    -Hedges_g_variance_new,
    -CI_lower_new,
    -CI_upper_new
  )

write_csv(merged, output_file)
cat("✅ Done! Updated file saved as:\n", output_file, "\n")
