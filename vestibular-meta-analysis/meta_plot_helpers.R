############################################################
# Shared helpers for repo-relative funnel and Baujat plots.
############################################################

get_script_dir <- function() {
  frames <- sys.frames()
  for (i in rev(seq_along(frames))) {
    if (!is.null(frames[[i]]$ofile)) {
      ofile <- frames[[i]]$ofile
      if (file.exists(ofile)) {
        return(dirname(normalizePath(ofile)))
      }
      if (file.exists(file.path(getwd(), basename(ofile)))) {
        return(normalizePath(getwd()))
      }
    }
  }
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg) > 0) {
    return(dirname(normalizePath(sub("^--file=", "", file_arg[1]))))
  }
  normalizePath(getwd())
}

verified_dk_map <- function() {
  tibble::tribble(
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
}

verified_sub_map <- function() {
  tibble::tribble(
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
    "vermi",         "cerebellum"
  )
}

match_from_map <- function(value, map_df, label_col) {
  hits <- map_df[[label_col]][
    vapply(map_df$pattern, function(pattern) stringr::str_detect(value, pattern), logical(1))
  ]
  if (length(hits) == 0) {
    return(NA_character_)
  }
  hits[1]
}

attach_region_labels <- function(meta) {
  meta %>%
    dplyr::rowwise() %>%
    dplyr::mutate(
      dk_region = match_from_map(ROI_clean, verified_dk_map(), "region"),
      sub_label = match_from_map(ROI_clean, verified_sub_map(), "label")
    ) %>%
    dplyr::ungroup()
}

load_verified_meta <- function(root_dir = get_script_dir()) {
  input_file <- file.path(root_dir, "mycode-11.24", "output_with_g.csv")
  if (!file.exists(input_file)) {
    stop("Missing input file: ", input_file)
  }

  meta <- readr::read_csv(input_file, show_col_types = FALSE)
  meta <- meta %>%
    dplyr::mutate(
      Congenital_or_Acquired = tolower(Congenital_or_Acquired),
      ROI_clean = ifelse(
        is.na(ROI_Homogenized),
        "",
        stringr::str_squish(tolower(ROI_Homogenized))
      )
    )

  attach_region_labels(meta)
}

meta_output_dir <- function(root_dir = get_script_dir()) {
  out_dir <- file.path(root_dir, "mycode-11.24")
  if (!dir.exists(out_dir)) {
    dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
  }
  out_dir
}

subset_meta_region <- function(meta, etio, region_type, require_variance = TRUE) {
  dat <- meta %>%
    dplyr::filter(
      Congenital_or_Acquired == etio,
      !is.na(Hedges_g_exact)
    )

  if (require_variance) {
    dat <- dat %>%
      dplyr::filter(!is.na(Hedges_g_variance))
  }

  if (region_type == "cortex") {
    dat <- dat %>% dplyr::filter(!is.na(dk_region))
  } else {
    dat <- dat %>% dplyr::filter(!is.na(sub_label))
  }

  dat
}

make_study_labels <- function(dat) {
  dat %>%
    dplyr::mutate(
      Author_clean = stringr::str_remove_all(Author, ",") %>%
        stringr::str_split(" ", simplify = TRUE) %>%
        .[, 1],
      StudyBase = paste0(Year, "-", Author_clean)
    ) %>%
    dplyr::ungroup() %>%
    dplyr::mutate(Study = ave(StudyBase, StudyBase, FUN = function(x) paste0(x, ".", seq_along(x))))
}

write_placeholder_plot <- function(path, title, lines, width = 900, height = 700) {
  grDevices::png(path, width = width, height = height)
  graphics::plot.new()
  graphics::title(main = title)
  if (length(lines) == 0) {
    lines <- "No data available."
  }
  y_positions <- seq(0.65, 0.35, length.out = length(lines))
  for (i in seq_along(lines)) {
    graphics::text(0.5, y_positions[i], labels = lines[[i]], cex = 1)
  }
  grDevices::dev.off()
}
