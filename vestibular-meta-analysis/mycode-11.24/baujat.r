# =======================
# 4. BAUJAT PLOTS (R)
# =======================
# install.packages(c("metafor", "readr", "dplyr", "stringr"))
library(metafor)
library(readr)
library(dplyr)
library(stringr)

input_file <- "C:/PATH/TO/all_meta_rows.csv"      # <---- CHANGE
output_dir <- "C:/PATH/TO/output/baujat/"        # <---- CHANGE
if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

dat <- read_csv(input_file, show_col_types = FALSE) %>%
  mutate(Etiology = tolower(Etiology))

etiologies <- sort(unique(dat$Etiology))

for (et in etiologies) {
  sub <- dat %>%
    filter(Etiology == et,
           !is.na(Hedges_g_exact),
           !is.na(Hedges_g_variance))

  if (nrow(sub) < 3) {
    message("Skipping ", et, " (not enough data)")
    next
  }

  # nice study labels: Year-Author.n
  sub <- sub %>%
    mutate(
      Author_clean = str_remove_all(Author, ",") %>% str_split(" ", simplify = TRUE) %>% .[,1],
      StudyBase = paste0(Year, "-", Author_clean)
    )

  sub$Study <- ave(sub$StudyBase, sub$StudyBase,
                   FUN = function(x) paste0(x, ".", seq_along(x)))

  m <- rma(yi = Hedges_g_exact,
           vi = Hedges_g_variance,
           data = sub,
           method = "REML",
           slab = sub$Study)

  # get Baujat data to scale axes
  bj <- baujat(m, plot = FALSE)
  max_x <- max(bj$x, na.rm = TRUE) * 1.2
  max_y <- max(bj$y, na.rm = TRUE) * 1.2

  png(file.path(output_dir, paste0("baujat_", et, ".png")),
      width = 800, height = 600, res = 150)
  baujat(m,
         xlim = c(0, max_x),
         ylim = c(0, max_y),
         bty  = "l",
         las  = 1,
         main = paste0("Baujat Plot (", et, ")"),
         symbol = "slab",
         grid = TRUE)
  dev.off()
}
