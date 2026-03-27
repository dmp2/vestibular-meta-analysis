# ======================
# 3. FUNNEL PLOTS (R)
# ======================
# install.packages(c("metafor", "readr", "dplyr"))
library(metafor)
library(readr)
library(dplyr)

input_file <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24/output_with_g.csv"
output_dir <- "C:/Users/rjmod/Desktop/THESIS WORK/mycode-11.24"   
if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

dat <- read_csv(input_file, show_col_types = FALSE) %>%
  mutate(Etiology = tolower(Etiology))

etiologies <- sort(unique(dat$Etiology))

for (et in etiologies) {
  sub <- dat %>%
    filter(Etiology == et,
           !is.na(Hedges_g_exact),
           !is.na(Hedges_g_variance))

  if (nrow(sub) < 3) next

  yi <- sub$Hedges_g_exact
  vi <- sub$Hedges_g_variance

  m <- rma(yi = yi, vi = vi, method = "REML")

  png(file.path(output_dir, paste0("funnel_", et, ".png")),
      width = 800, height = 800)
  funnel(
    m,
    level = c(90, 95, 99),
    refline = 0,
    yaxis = "sei",
    xlab = "Residual value",
    ylab = "Standard error",
    shade = c("grey90", "grey70", "grey50"),
    legend = TRUE,
    main = paste0("Funnel Plot (", et, ")")
  )
  dev.off()
}
