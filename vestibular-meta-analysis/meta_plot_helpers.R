############################################################
# Shared helpers for repo-relative funnel, Baujat, and
# forest plots using a reconciled secondary-plot input.
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

meta_columns <- function() {
  c(
    "Study_ID", "Author", "Year", "Title", "Journal", "DOI_or_PMID",
    "Etiology", "Subtype", "Congenital_or_Acquired", "Side_deaf_or_lesion",
    "Chronicity_months", "Sample_Size_Patients", "Sample_Size_Controls",
    "Mean_Age_Patients", "Sex_Ratio_Patients", "Modality",
    "Acquisition_Type", "Scanner_FieldStrength_T", "Analysis_Toolbox",
    "Hedges_g_exact", "Hedges_g_variance", "CI_lower", "CI_upper",
    "P_value", "Statistic_type", "Statistic_value", "Direction",
    "ROI_Homogenized", "Big_Area", "Matter", "Side", "MNI_X", "MNI_Y",
    "MNI_Z", "Measure", "Network_Assignment", "Study_Quality_Score",
    "Extractor", "Notes", "Source_PDF_or_ZIP"
  )
}

has_value <- function(x) {
  ifelse(
    is.na(x),
    FALSE,
    {
      text <- trimws(as.character(x))
      text != "" & !tolower(text) %in% c("na", "nan")
    }
  )
}

clean_key_part <- function(x) {
  ifelse(has_value(x), trimws(as.character(x)), "")
}

make_merge_key <- function(df) {
  paste(
    clean_key_part(df$Study_ID),
    clean_key_part(df$ROI_Homogenized),
    clean_key_part(df$Side),
    clean_key_part(df$Measure),
    sep = "||"
  )
}

prefer_value <- function(primary, secondary) {
  primary_ok <- has_value(primary)
  secondary_ok <- has_value(secondary)

  out <- primary
  out[!primary_ok & secondary_ok] <- secondary[!primary_ok & secondary_ok]
  out[!primary_ok & !secondary_ok] <- NA
  out
}

source_of_value <- function(primary, secondary, primary_name, secondary_name) {
  primary_ok <- has_value(primary)
  secondary_ok <- has_value(secondary)

  dplyr::case_when(
    primary_ok ~ primary_name,
    !primary_ok & secondary_ok ~ secondary_name,
    TRUE ~ "missing"
  )
}

verified_dk_map <- function() {
  tibble::tribble(
    ~pattern,                                      ~region,
    "anterior cingulate cortex",                   "rostral anterior cingulate",
    "cingulate gyrus",                             "posterior cingulate",
    "cuneus",                                      "cuneus",
    "fusiform gyrus",                              "fusiform",
    "fusiform",                                    "fusiform",
    "insula",                                      "insula",
    "intracalcarine cortex",                       "pericalcarine",
    "intracalcarine",                              "pericalcarine",
    "lingual gyrus",                               "lingual",
    "lateral occipital cortex",                    "lateral occipital",
    "lateral occipital",                           "lateral occipital",
    "middle frontal gyrus",                        "rostral middle frontal",
    "middle temporal gyrus \\(mt/v5\\)",           "middle temporal",
    "middle temporal visual area \\(mt/v5\\)",     "middle temporal",
    "middle temporal gyrus",                       "middle temporal",
    "^mt/v5$",                                     "middle temporal",
    "postcentral gyrus",                           "postcentral",
    "precentral gyrus",                            "precentral",
    "precuneus / superior parietal white matter",  "superior parietal",
    "precuneus",                                   "precuneus",
    "superior frontal gyrus",                      "superior frontal",
    "superior orbitofrontal cortex",               "lateral orbitofrontal",
    "superior orbitofrontal",                      "lateral orbitofrontal",
    "orbital gyrus",                               "lateral orbitofrontal",
    "superior temporal gyrus",                     "superior temporal",
    "primary somatosensory cortex",                "postcentral",
    "supramarginal gyrus",                         "supramarginal"
  )
}

verified_sub_map <- function() {
  tibble::tribble(
    ~pattern,                     ~label,
    "hippocampus",                "hippocampus",
    "parahippocamp",              "hippocampus",
    "presubiculum",               "hippocampus",
    "amygdala",                   "amygdala",
    "caudate",                    "caudate",
    "putamen",                    "putamen",
    "pallid",                     "pallidum",
    "accumb",                     "accumbens",
    "thalam",                     "thalamus",
    "brainstem",                  "brainstem",
    "pons",                       "brainstem",
    "mesencephalon",              "brainstem",
    "midbrain",                   "brainstem",
    "pontomesencephalic",         "brainstem",
    "vestibular nuclei",          "brainstem",
    "gracile nucleus",            "brainstem",
    "cerebell",                   "cerebellum",
    "vermi",                      "cerebellum",
    "culmen",                     "cerebellum",
    "peduncle",                   "cerebellum",
    "inferior semi-lunar lobule", "cerebellum",
    "crus i",                     "cerebellum",
    "lobule vi",                  "cerebellum"
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

normalize_etiology_value <- function(x) {
  stringr::str_squish(stringr::str_to_lower(as.character(x)))
}

derive_condition_normalized <- function(etiology_clean, etiology_raw) {
  dplyr::case_when(
    stringr::str_detect(etiology_clean, "acute unilateral peripheral vestibular neuritis|vestibular neuritis") ~ "Vestibular neuritis",
    etiology_clean == "post-concussive vestibular dysfunction" ~ "Post-concussive vestibular dysfunction",
    etiology_clean == "mild traumatic brain injury with vestibular symptoms" ~ "Mild traumatic brain injury with vestibular symptoms",
    stringr::str_detect(etiology_clean, "sports-related concussion") ~ "Sports-related concussion with persistent post-concussive symptoms",
    etiology_clean == "bilateral vestibular loss" ~ "Bilateral vestibular loss",
    etiology_clean == "bilateral vestibular failure" ~ "Bilateral vestibular failure",
    etiology_clean == "bilateral vestibulopathy" ~ "Bilateral vestibulopathy",
    stringr::str_detect(etiology_clean, "neurofibromatosis 2") ~ "NF2 bilateral vestibular loss after neurectomy",
    stringr::str_detect(etiology_clean, "acoustic neuroma surgery|acoustic neurinoma surgery|vestibular schwannoma removal") ~ "Unilateral vestibular deafferentation after vestibular schwannoma surgery",
    etiology_clean == "peripheral vestibular dysfunction" ~ "Peripheral vestibular dysfunction",
    stringr::str_detect(etiology_clean, "méni|meni") ~ "Meniere's disease",
    etiology_clean == "persistent postural perceptual dizziness" ~ "Persistent postural perceptual dizziness",
    etiology_clean == "long-term vestibular adaptation in professional ballet dancers" ~ "Professional ballet dancers",
    stringr::str_detect(etiology_clean, "vestibular migraine") ~ "Vestibular migraine",
    stringr::str_detect(etiology_clean, "small-vessel|small vessel|white matter disease") ~ "White matter disease or small-vessel lesions",
    stringr::str_detect(etiology_clean, "stroke|ischemi") ~ "Stroke or ischemic vestibular-circuit lesions",
    stringr::str_detect(etiology_clean, "spaceflight|microgravity|astronaut") ~ "Spaceflight-related vestibular adaptation",
    stringr::str_detect(etiology_clean, "healthy adults|healthy older|healthy younger|older adults|younger adults|aging") ~ "Healthy aging",
    TRUE ~ ifelse(has_value(etiology_raw), as.character(etiology_raw), "Unclassified or needs review")
  )
}

derive_review_group <- function(condition_normalized) {
  dplyr::case_when(
    condition_normalized == "Vestibular neuritis" ~ "Unilateral vestibular loss or deafferentation",
    condition_normalized %in% c(
      "Post-concussive vestibular dysfunction",
      "Mild traumatic brain injury with vestibular symptoms",
      "Sports-related concussion with persistent post-concussive symptoms"
    ) ~ "Post-traumatic or concussive vestibulopathy",
    condition_normalized %in% c(
      "Bilateral vestibular loss",
      "Bilateral vestibular failure",
      "Bilateral vestibulopathy"
    ) ~ "Bilateral vestibulopathy",
    condition_normalized %in% c(
      "NF2 bilateral vestibular loss after neurectomy",
      "Unilateral vestibular deafferentation after vestibular schwannoma surgery"
    ) ~ "Vestibular schwannoma resection",
    condition_normalized == "Peripheral vestibular dysfunction" ~ "Chronic or mild vestibulopathy",
    condition_normalized == "Meniere's disease" ~ "Meniere's disease",
    condition_normalized == "Vestibular migraine" ~ "Vestibular migraine",
    condition_normalized == "White matter disease or small-vessel lesions" ~ "White matter disease or small-vessel lesions",
    condition_normalized == "Stroke or ischemic vestibular-circuit lesions" ~ "Stroke or ischemic vestibular-circuit lesions",
    condition_normalized == "Professional ballet dancers" ~ "Vestibular experts",
    condition_normalized == "Healthy aging" ~ "Healthy aging",
    condition_normalized == "Spaceflight-related vestibular adaptation" ~ "Spaceflight-related vestibular adaptation",
    condition_normalized == "Persistent postural perceptual dizziness" ~ "Other vestibular clinical cohorts",
    TRUE ~ "Unclassified or needs review"
  )
}

derive_condition_family <- function(condition_normalized, review_group) {
  dplyr::case_when(
    condition_normalized %in% c("Vestibular neuritis", "Peripheral vestibular dysfunction") ~ "Unilateral peripheral vestibular syndromes",
    review_group == "Post-traumatic or concussive vestibulopathy" ~ "Concussion-related vestibulopathy",
    condition_normalized %in% c("Bilateral vestibular loss", "Bilateral vestibular failure", "Bilateral vestibulopathy") ~ "Bilateral vestibular syndromes",
    review_group == "Vestibular schwannoma resection" ~ "Vestibular schwannoma resection or deafferentation",
    condition_normalized == "Meniere's disease" ~ "Meniere's disease",
    condition_normalized == "Persistent postural perceptual dizziness" ~ "Functional vestibular disorders",
    review_group %in% c("Vestibular experts", "Healthy aging", "Spaceflight-related vestibular adaptation") ~ "Adaptive or non-clinical cohorts",
    condition_normalized == "Vestibular migraine" ~ "Vestibular migraine",
    review_group %in% c("White matter disease or small-vessel lesions", "Stroke or ischemic vestibular-circuit lesions") ~ "Central vascular or white-matter vestibular disorders",
    TRUE ~ review_group
  )
}

derive_cohort_contrast <- function(review_group, n_patients, n_controls) {
  both_sample_sizes <- has_value(n_patients) & has_value(n_controls)

  dplyr::case_when(
    review_group == "Vestibular experts" ~ "expertise_vs_control",
    review_group == "Healthy aging" ~ "healthy_subgroup_comparison",
    review_group == "Spaceflight-related vestibular adaptation" ~ "adaptation_or_exposure_comparison",
    both_sample_sizes ~ "clinical_vs_control_style",
    TRUE ~ "unclear_or_nonstandard"
  )
}

derive_grouping_fields <- function(meta) {
  meta %>%
    dplyr::mutate(
      Etiology_clean = normalize_etiology_value(Etiology),
      Condition_Normalized = derive_condition_normalized(Etiology_clean, Etiology),
      Review_Group = derive_review_group(Condition_Normalized),
      Condition_Family = derive_condition_family(Condition_Normalized, Review_Group),
      Cohort_Contrast = derive_cohort_contrast(Review_Group, Sample_Size_Patients, Sample_Size_Controls)
    )
}

safe_slug <- function(x) {
  ascii <- iconv(as.character(x), from = "", to = "ASCII//TRANSLIT")
  ascii[is.na(ascii)] <- as.character(x[is.na(ascii)])
  slug <- gsub("[^a-z0-9]+", "_", tolower(ascii))
  gsub("(^_+|_+$)", "", slug)
}

available_group_values <- function(meta, group_field) {
  values <- meta[[group_field]]
  values <- values[has_value(values)]
  sort(unique(as.character(values)))
}

read_meta_table <- function(path, source_name) {
  if (!file.exists(path)) {
    stop("Missing ", source_name, " input file: ", path)
  }

  meta <- readr::read_csv(path, show_col_types = FALSE)
  missing_cols <- setdiff(meta_columns(), names(meta))
  if (length(missing_cols) > 0) {
    stop(
      source_name,
      " table is missing expected columns: ",
      paste(missing_cols, collapse = ", ")
    )
  }

  meta %>%
    dplyr::mutate(
      .merge_key = make_merge_key(dplyr::pick(Study_ID, ROI_Homogenized, Side, Measure)),
      .source_table = source_name
    )
}

assert_unique_keys <- function(meta, source_name) {
  dupes <- meta %>%
    dplyr::count(.merge_key, name = "n") %>%
    dplyr::filter(n > 1)

  if (nrow(dupes) > 0) {
    sample_keys <- paste(head(dupes$.merge_key, 5), collapse = ", ")
    stop(
      source_name,
      " has non-unique composite keys on Study_ID + ROI_Homogenized + Side + Measure. Sample keys: ",
      sample_keys
    )
  }

  invisible(meta)
}

prepare_single_source_meta <- function(meta, source_name) {
  meta %>%
    dplyr::select(dplyr::all_of(meta_columns()), .merge_key) %>%
    dplyr::mutate(
      effect_source = source_of_value(
        Hedges_g_exact,
        rep(NA_character_, n()),
        source_name,
        "missing"
      ),
      variance_source = source_of_value(
        Hedges_g_variance,
        rep(NA_character_, n()),
        source_name,
        "missing"
      ),
      ci_source = dplyr::case_when(
        has_value(CI_lower) & has_value(CI_upper) ~ source_name,
        TRUE ~ "missing"
      )
    )
}

reconcile_secondary_tables <- function(historical, computed) {
  historical_keys <- sort(unique(historical$.merge_key))
  computed_keys <- sort(unique(computed$.merge_key))

  missing_in_computed <- setdiff(historical_keys, computed_keys)
  missing_in_historical <- setdiff(computed_keys, historical_keys)

  if (length(missing_in_computed) > 0 || length(missing_in_historical) > 0) {
    details <- c(
      if (length(missing_in_computed) > 0) {
        paste0("missing in computed: ", paste(head(missing_in_computed, 5), collapse = ", "))
      },
      if (length(missing_in_historical) > 0) {
        paste0("missing in historical: ", paste(head(missing_in_historical, 5), collapse = ", "))
      }
    )
    stop("Historical and computed secondary-plot tables do not cover the same composite keys: ", paste(details, collapse = " | "))
  }

  joined <- historical %>%
    dplyr::select(dplyr::all_of(meta_columns()), .merge_key) %>%
    dplyr::rename_with(~ paste0(.x, ".historical"), dplyr::all_of(meta_columns())) %>%
    dplyr::left_join(
      computed %>%
        dplyr::select(dplyr::all_of(meta_columns()), .merge_key) %>%
        dplyr::rename_with(~ paste0(.x, ".computed"), dplyr::all_of(meta_columns())),
      by = ".merge_key"
    )

  reconciled <- tibble::tibble(.merge_key = joined$.merge_key)

  for (col in meta_columns()) {
    historical_col <- joined[[paste0(col, ".historical")]]
    computed_col <- joined[[paste0(col, ".computed")]]
    reconciled[[col]] <- prefer_value(historical_col, computed_col)
  }

  reconciled %>%
    dplyr::mutate(
      effect_source = source_of_value(
        joined$Hedges_g_exact.historical,
        joined$Hedges_g_exact.computed,
        "historical",
        "computed"
      ),
      variance_source = source_of_value(
        joined$Hedges_g_variance.historical,
        joined$Hedges_g_variance.computed,
        "historical",
        "computed"
      ),
      ci_source = dplyr::case_when(
        has_value(joined$CI_lower.historical) & has_value(joined$CI_upper.historical) ~ "historical",
        has_value(joined$CI_lower.computed) & has_value(joined$CI_upper.computed) ~ "computed",
        TRUE ~ "missing"
      )
    )
}

load_secondary_plot_meta <- function(root_dir = get_script_dir(), input_policy = "hybrid") {
  input_policy <- match.arg(input_policy, c("hybrid", "historical", "computed"))

  historical_file <- file.path(root_dir, "mycode-11.24", "output_with_g.csv")
  computed_file <- file.path(root_dir, "mycode-11.24", "output_with_g_computed.csv")

  historical <- read_meta_table(historical_file, "historical")
  computed <- read_meta_table(computed_file, "computed")

  assert_unique_keys(historical, "historical")
  assert_unique_keys(computed, "computed")

  meta <- switch(
    input_policy,
    hybrid = reconcile_secondary_tables(historical, computed),
    historical = prepare_single_source_meta(historical, "historical"),
    computed = prepare_single_source_meta(computed, "computed")
  )

  meta %>%
    dplyr::mutate(
      Congenital_or_Acquired = stringr::str_to_lower(trimws(as.character(Congenital_or_Acquired))),
      ROI_clean = ifelse(
        is.na(ROI_Homogenized),
        "",
        stringr::str_squish(stringr::str_to_lower(ROI_Homogenized))
      )
    ) %>%
    derive_grouping_fields() %>%
    attach_region_labels()
}

meta_output_dir <- function(root_dir = get_script_dir()) {
  out_dir <- file.path(root_dir, "mycode-11.24")
  if (!dir.exists(out_dir)) {
    dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
  }
  out_dir
}

subset_meta_region <- function(meta, etio, region_type, require_variance = FALSE, require_ci = FALSE) {
  dat <- meta %>%
    dplyr::filter(
      Congenital_or_Acquired == etio,
      has_value(Hedges_g_exact)
    )

  if (region_type == "cortex") {
    dat <- dat %>% dplyr::filter(!is.na(dk_region))
  } else {
    dat <- dat %>% dplyr::filter(!is.na(sub_label))
  }

  if (require_variance) {
    dat <- dat %>% dplyr::filter(has_value(Hedges_g_variance))
  }

  if (require_ci) {
    dat <- dat %>%
      dplyr::filter(has_value(CI_lower), has_value(CI_upper))
  }

  dat
}

subset_meta_group <- function(meta, group_field, group_value, region_type = NULL, require_variance = FALSE, require_ci = FALSE) {
  dat <- meta %>%
    dplyr::filter(
      .data[[group_field]] == group_value,
      has_value(Hedges_g_exact)
    )

  if (!is.null(region_type)) {
    if (region_type == "cortex") {
      dat <- dat %>% dplyr::filter(!is.na(dk_region))
    } else {
      dat <- dat %>% dplyr::filter(!is.na(sub_label))
    }
  }

  if (require_variance) {
    dat <- dat %>% dplyr::filter(has_value(Hedges_g_variance))
  }

  if (require_ci) {
    dat <- dat %>% dplyr::filter(has_value(CI_lower), has_value(CI_upper))
  }

  dat
}

summarize_plot_eligibility <- function(meta, group_field = "Congenital_or_Acquired") {
  groups <- available_group_values(meta, group_field)
  region_types <- c("cortex", "subcortex")

  if (length(groups) == 0) {
    return(tibble::tibble(
      group_field = character(0),
      group_value = character(0),
      region_type = character(0),
      rows_effect = integer(0),
      rows_variance = integer(0),
      rows_ci = integer(0)
    ))
  }

  dplyr::bind_rows(lapply(groups, function(group_value) {
    dplyr::bind_rows(lapply(region_types, function(region_type) {
      base <- subset_meta_group(meta, group_field, group_value, region_type = region_type)
      variance <- subset_meta_group(meta, group_field, group_value, region_type = region_type, require_variance = TRUE)
      ci <- subset_meta_group(meta, group_field, group_value, region_type = region_type, require_ci = TRUE)

      tibble::tibble(
        group_field = group_field,
        group_value = group_value,
        region_type = region_type,
        rows_effect = nrow(base),
        rows_variance = nrow(variance),
        rows_ci = nrow(ci)
      )
    }))
  }))
}

summarize_legacy_plot_eligibility <- function(meta) {
  specs <- tibble::tribble(
    ~etio,        ~region_type,
    "acquired",   "cortex",
    "acquired",   "subcortex",
    "congenital", "cortex",
    "congenital", "subcortex"
  )

  dplyr::bind_rows(lapply(seq_len(nrow(specs)), function(i) {
    etio <- specs$etio[[i]]
    region_type <- specs$region_type[[i]]

    base <- subset_meta_region(meta, etio, region_type)
    variance <- subset_meta_region(meta, etio, region_type, require_variance = TRUE)
    ci <- subset_meta_region(meta, etio, region_type, require_ci = TRUE)

    tibble::tibble(
      etio = etio,
      region_type = region_type,
      rows_effect = nrow(base),
      rows_variance = nrow(variance),
      rows_ci = nrow(ci)
    )
  }))
}

forest_group_eligibility <- function(meta, group_field = "Condition_Normalized") {
  groups <- available_group_values(meta, group_field)

  if (length(groups) == 0) {
    return(tibble::tibble(
      group_field = character(0),
      group_value = character(0),
      rows_ci = integer(0),
      cohort_contrast = character(0)
    ))
  }

  dplyr::bind_rows(lapply(groups, function(group_value) {
    dat <- meta %>%
      dplyr::filter(
        .data[[group_field]] == group_value,
        has_value(Hedges_g_exact),
        has_value(CI_lower),
        has_value(CI_upper)
      )

    tibble::tibble(
      group_field = group_field,
      group_value = group_value,
      rows_ci = nrow(dat),
      cohort_contrast = if (nrow(dat) > 0) dat$Cohort_Contrast[[1]] else NA_character_
    )
  }))
}

format_n_label <- function(n_patients, n_controls) {
  patient_text <- ifelse(has_value(n_patients), trimws(as.character(n_patients)), "NA")
  control_text <- ifelse(has_value(n_controls), trimws(as.character(n_controls)), "NA")
  paste0(patient_text, "/", control_text)
}

make_study_labels <- function(dat) {
  if (nrow(dat) == 0) {
    dat$Author_clean <- character(0)
    dat$Year_clean <- character(0)
    dat$StudyBase <- character(0)
    dat$Study <- character(0)
    return(dat)
  }

  dat %>%
    dplyr::mutate(
      Author_text = stringr::str_squish(stringr::str_remove_all(as.character(Author), ",")),
      Author_clean = dplyr::case_when(
        !has_value(Author) ~ "Unknown",
        TRUE ~ dplyr::coalesce(stringr::word(Author_text, 1), "Unknown")
      ),
      Year_clean = dplyr::if_else(has_value(Year), as.character(Year), "NA"),
      StudyBase = paste0(Year_clean, "-", Author_clean)
    ) %>%
    dplyr::select(-Author_text) %>%
    dplyr::ungroup() %>%
    dplyr::mutate(Study = ave(StudyBase, StudyBase, FUN = function(x) paste0(x, ".", seq_along(x))))
}
