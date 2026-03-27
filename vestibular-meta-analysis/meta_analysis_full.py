#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meta_analysis_full.py

End-to-end analysis for your vestibular meta-analysis dataset.

Input:
    all_meta_rows.csv  (output of your AI+JSON pipeline, with master schema)

Outputs (PNG files in the same folder):
    summary_*.txt (printed to terminal only)
    plot_big_area_mean_effect.png
    plot_big_area_counts.png
    plot_matter_counts.png
    plot_side_counts.png
    plot_roi_counts_top20.png
    (if Hedges_g filled:)
        forest_all_effects.png
        forest_overall_random_effect.png
        funnel_plot.png
        baujat_plot.png
        subgroup_congenital_acquired.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.stats.meta_analysis import combine_effects

# ---------------------------
# 0. Configuration
# ---------------------------
DATA_FILE = "all_meta_rows.csv"

# Columns we expect (from your master schema)
EXPECTED_COLS = [
    "Study_ID",
    "Author",
    "Year",
    "Title",
    "Journal",
    "DOI_or_PMID",
    "Etiology",
    "Subtype",
    "Congenital_or_Acquired",
    "Side_deaf_or_lesion",
    "Chronicity_months",
    "Sample_Size_Patients",
    "Sample_Size_Controls",
    "Mean_Age_Patients",
    "Sex_Ratio_Patients",
    "Modality",
    "Acquisition_Type",
    "Scanner_FieldStrength_T",
    "Analysis_Toolbox",
    "Hedges_g_exact",
    "Hedges_g_variance",
    "CI_lower",
    "CI_upper",
    "P_value",
    "Statistic_type",
    "Statistic_value",
    "Direction",
    "ROI_Homogenized",
    "Big_Area",
    "Matter",
    "Side",
    "MNI_X",
    "MNI_Y",
    "MNI_Z",
    "Measure",
    "Network_Assignment",
    "Study_Quality_Score",
    "Extractor",
    "Notes",
    "Source_PDF_or_ZIP",
]


# ---------------------------
# 1. Load and clean data
# ---------------------------
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Ensure expected columns exist (add missing as empty)
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = np.nan

    # Reorder columns
    df = df[EXPECTED_COLS]

    # Coerce numeric columns
    numeric_cols = [
        "Year",
        "Chronicity_months",
        "Sample_Size_Patients",
        "Sample_Size_Controls",
        "Mean_Age_Patients",
        "Scanner_FieldStrength_T",
        "Hedges_g_exact",
        "Hedges_g_variance",
        "CI_lower",
        "CI_upper",
        "Statistic_value",
        "MNI_X",
        "MNI_Y",
        "MNI_Z",
        "Study_Quality_Score",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ---------------------------
# 2. Summary prints
# ---------------------------
def print_basic_summary(df: pd.DataFrame):
    print("========== BASIC SUMMARY ==========")
    print(f"Rows (effects / ROIs): {len(df)}")
    print(f"Unique studies:        {df['Study_ID'].nunique()}")
    print(f"Unique authors:        {df['Author'].nunique()}")

    print("\nEtiology counts:")
    print(df["Etiology"].value_counts(dropna=False))

    print("\nModality counts:")
    print(df["Modality"].value_counts(dropna=False))

    print("\nMeasure counts:")
    print(df["Measure"].value_counts(dropna=False))

    print("\nMatter counts:")
    print(df["Matter"].value_counts(dropna=False))

    n_g = df["Hedges_g_exact"].notna().sum()
    n_var = df["Hedges_g_variance"].notna().sum()
    print(f"\nRows with Hedges_g_exact:   {n_g}")
    print(f"Rows with Hedges_g_variance:{n_var}")
    print("===================================\n")


# ---------------------------
# 3. Descriptive plots (no effect size needed)
# ---------------------------
def plot_big_area(df: pd.DataFrame):
    """Mean effect and counts per Big_Area."""
    # Mean effect (only if some g values present)
    if df["Hedges_g_exact"].notna().sum() > 0:
        area_mean = (
            df.dropna(subset=["Big_Area", "Hedges_g_exact"])
              .groupby("Big_Area")["Hedges_g_exact"]
              .mean()
              .sort_values()
        )
        plt.figure(figsize=(8, 4))
        area_mean.plot(kind="bar")
        plt.axhline(0, color="gray", linestyle="--")
        plt.ylabel("Mean Hedges g")
        plt.title("Mean effect size by Big_Area")
        plt.tight_layout()
        plt.savefig("plot_big_area_mean_effect.png", dpi=300)
        plt.close()
    else:
        print("[INFO] No Hedges_g_exact present; skipping Big_Area mean effect plot.")

    # Pure counts per Big_Area (always possible)
    counts = df["Big_Area"].value_counts().sort_values(ascending=False)
    plt.figure(figsize=(8, 4))
    counts.plot(kind="bar")
    plt.ylabel("Number of ROIs")
    plt.title("Counts of ROIs by Big_Area")
    plt.tight_layout()
    plt.savefig("plot_big_area_counts.png", dpi=300)
    plt.close()


def plot_matter_counts(df: pd.DataFrame):
    counts = df["Matter"].value_counts().sort_values(ascending=False)
    plt.figure(figsize=(5, 4))
    counts.plot(kind="bar")
    plt.ylabel("Number of ROIs")
    plt.title("Counts by Matter (Gray/White)")
    plt.tight_layout()
    plt.savefig("plot_matter_counts.png", dpi=300)
    plt.close()


def plot_side_counts(df: pd.DataFrame):
    counts = df["Side"].value_counts().sort_values(ascending=False)
    plt.figure(figsize=(5, 4))
    counts.plot(kind="bar")
    plt.ylabel("Number of ROIs")
    plt.title("Counts by Hemisphere Side")
    plt.tight_layout()
    plt.savefig("plot_side_counts.png", dpi=300)
    plt.close()


def plot_roi_counts(df: pd.DataFrame, top_n: int = 20):
    counts = (
        df["ROI_Homogenized"]
        .value_counts()
        .sort_values(ascending=False)
        .head(top_n)
    )
    plt.figure(figsize=(8, 4))
    counts.plot(kind="bar")
    plt.ylabel("Number of entries")
    plt.title(f"Top {top_n} ROIs by count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("plot_roi_counts_top20.png", dpi=300)
    plt.close()


# ---------------------------
# 4. Effect-size based meta-analysis (if available)
# ---------------------------
def run_meta_analysis(df: pd.DataFrame):
    es_df = df.dropna(subset=["Hedges_g_exact", "Hedges_g_variance"]).copy()
    n = len(es_df)
    if n == 0:
        print("[INFO] No rows with Hedges_g_exact and variance; skipping meta-analysis.")
        return
    if n < 3:
        print(f"[INFO] Only {n} rows with effect sizes; meta plots may be unstable but will run.")

    # Extract arrays
    yi = es_df["Hedges_g_exact"].values
    vi = es_df["Hedges_g_variance"].values

    # --- 4.1 Forest-like plot of individual effects ---
    order = np.argsort(yi)
    sorted_yi = yi[order]
    sorted_vi = vi[order]
    se = np.sqrt(sorted_vi)
    ci_low = sorted_yi - 1.96 * se
    ci_high = sorted_yi + 1.96 * se

    plt.figure(figsize=(6, max(4, 0.25 * len(sorted_yi))))
    y_pos = np.arange(len(sorted_yi))
    plt.errorbar(sorted_yi, y_pos, xerr=1.96 * se, fmt="o", capsize=3)
    plt.axvline(0, color="gray", linestyle="--")
    plt.yticks(y_pos, [])
    plt.xlabel("Hedges g")
    plt.title("Forest plot of individual effects (unsorted studies)")
    plt.tight_layout()
    plt.savefig("forest_all_effects.png", dpi=300)
    plt.close()

    # --- 4.2 Random-effects pooled effect (DerSimonian-Laird) ---
    res = combine_effects(yi, vi, method_re="dl")
    sf = res.summary_frame()
    rand = sf.loc["random effect"]
    pooled = rand["eff"]
    ci_l = rand["ci_low"]
    ci_u = rand["ci_upp"]

    print("========== META-ANALYSIS (Random Effects, all rows with g) ==========")
    print(f"Pooled Hedges g = {pooled:.3f}  [{ci_l:.3f}, {ci_u:.3f}]")
    print(sf)
    print("=====================================================================\n")

    # small forest showing only pooled effect
    plt.figure(figsize=(4, 3))
    plt.errorbar(pooled, 0, xerr=[[pooled - ci_l], [ci_u - pooled]], fmt="o")
    plt.axvline(0, color="gray", linestyle="--")
    plt.yticks([])
    plt.xlabel("Hedges g (random-effects)")
    plt.title("Overall pooled effect")
    plt.tight_layout()
    plt.savefig("forest_overall_random_effect.png", dpi=300)
    plt.close()

    # --- 4.3 Funnel plot ---
    se_all = np.sqrt(vi)
    plt.figure(figsize=(5, 6))
    plt.scatter(yi, 1 / se_all, s=25, color="black")
    plt.axvline(pooled, color="blue", linestyle="--", label="Pooled g")
    plt.axvline(0, color="gray", linestyle=":")
    plt.xlabel("Hedges g")
    plt.ylabel("Precision (1 / SE)")
    plt.title("Funnel plot")
    plt.legend()
    plt.tight_layout()
    plt.savefig("funnel_plot.png", dpi=300)
    plt.close()

    # --- 4.4 Baujat-style plot (influence vs residual) ---
    w = 1.0 / vi
    mu = np.sum(w * yi) / np.sum(w)
    se_i = np.sqrt(vi)
    sq_resid = ((yi - mu) / se_i) ** 2

    influence = []
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        if mask.sum() == 0:
            influence.append(0.0)
        else:
            w2 = 1.0 / vi[mask]
            mu2 = np.sum(w2 * yi[mask]) / np.sum(w2)
            influence.append(abs(mu2 - mu))
    influence = np.array(influence)

    plt.figure(figsize=(5, 4))
    plt.scatter(sq_resid, influence, s=25)
    plt.xlabel("Squared Pearson residual")
    plt.ylabel("Influence on pooled g")
    plt.title("Baujat-style plot")
    plt.tight_layout()
    plt.savefig("baujat_plot.png", dpi=300)
    plt.close()

    # --- 4.5 Simple subgroup: Congenital vs Acquired ---
    sub_df = es_df.copy()
    # Normalize label
    sub_df["Congenital_or_Acquired_norm"] = sub_df["Congenital_or_Acquired"].str.strip().str.title()

    groups = ["Congenital", "Acquired"]
    means = []
    err = []
    labels = []
    for g_name in groups:
        tmp = sub_df[sub_df["Congenital_or_Acquired_norm"] == g_name]
        if len(tmp) == 0:
            continue
        yi_g = tmp["Hedges_g_exact"].values
        vi_g = tmp["Hedges_g_variance"].values
        if len(yi_g) == 0:
            continue
        res_g = combine_effects(yi_g, vi_g, method_re="dl")
        sf_g = res_g.summary_frame()
        rand_g = sf_g.loc["random effect"]
        pooled_g = rand_g["eff"]
        ci_lg = rand_g["ci_low"]
        ci_ug = rand_g["ci_upp"]
        means.append(pooled_g)
        err.append([pooled_g - ci_lg, ci_ug - pooled_g])
        labels.append(g_name)

    if len(labels) > 0:
        plt.figure(figsize=(4, 4))
        x_pos = np.arange(len(labels))
        lower_err = [e[0] for e in err]
        upper_err = [e[1] for e in err]
        plt.errorbar(
            means,
            x_pos,
            xerr=[lower_err, upper_err],
            fmt="o",
            capsize=4,
        )
        plt.axvline(0, color="gray", linestyle="--")
        plt.yticks(x_pos, labels)
        plt.xlabel("Hedges g (pooled)")
        plt.title("Congenital vs Acquired (random-effects)")
        plt.tight_layout()
        plt.savefig("subgroup_congenital_acquired.png", dpi=300)
        plt.close()
    else:
        print("[INFO] No valid Congenital/Acquired subgroups with effect sizes; skipping subgroup plot.")


# ---------------------------
# 5. Main
# ---------------------------
def main():
    df = load_data(DATA_FILE)
    print_basic_summary(df)

    # Descriptive plots (always)
    plot_big_area(df)
    plot_matter_counts(df)
    plot_side_counts(df)
    plot_roi_counts(df, top_n=20)

    # Effect-size meta-analysis (only if data present)
    run_meta_analysis(df)

    print("✅ Analysis complete. Check generated PNG files in the current folder.")


if __name__ == "__main__":
    main()
